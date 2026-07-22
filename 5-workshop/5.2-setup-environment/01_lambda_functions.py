# =====================================================
# AWS LAMBDA FUNCTIONS - Product Review Sentiment Analyzer
# =====================================================
# Region: ap-southeast-1 (Singapore)
# All functions use Python 3.11 runtime

import json
import boto3
import os
import uuid
import urllib3
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Any, Optional
import logging
import re
from botocore.exceptions import ClientError

# Initialize AWS clients
s3 = boto3.client('s3', region_name='ap-southeast-1')
dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')
comprehend = boto3.client('comprehend', region_name='ap-southeast-1')
secretsmanager = boto3.client('secretsmanager', region_name='ap-southeast-1')
sns = boto3.client('sns', region_name='ap-southeast-1')
ses = boto3.client('ses', region_name='ap-southeast-1')
cognitoidp = boto3.client('cognito-idp', region_name='ap-southeast-1')

# Plain HTTPS pool for the OpenRouter call. urllib3 ships as a boto3/botocore
# dependency, so this needs no extra Lambda layer.
http = urllib3.PoolManager()

# Environment variables
REVIEWS_TABLE = os.environ.get('REVIEWS_TABLE', 'Reviews')
PRODUCTS_TABLE = os.environ.get('PRODUCTS_TABLE', 'Products')
USERS_TABLE = os.environ.get('USERS_TABLE', 'Users')
RAW_BUCKET = os.environ.get('RAW_BUCKET', 'raw-reviews-bucket')
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN', '')
SES_SOURCE_EMAIL = os.environ.get('SES_SOURCE_EMAIL', 'noreply@your-domain.com')
USER_POOL_ID = os.environ.get('USER_POOL_ID', '')

# OpenRouter (Meta Llama 3.1 8B Instruct) -- used for the optional deep-insight
# pass on top of Comprehend's baseline sentiment. Swapped in from Amazon
# Bedrock because the study/demo AWS account is a free-credit account that
# cannot invoke paid Bedrock models. This is a pay-as-you-go model
# ($0.02 / $0.03 per 1M input/output tokens, no free tier), so the API key
# is never hard-coded -- it's fetched from Secrets Manager at runtime and
# cached for the life of this execution environment.
OPENROUTER_MODEL = os.environ.get('OPENROUTER_MODEL', 'meta-llama/llama-3.1-8b-instruct')
OPENROUTER_API_KEY_SECRET_NAME = os.environ.get('OPENROUTER_API_KEY_SECRET_NAME', 'openrouter-api-key')
OPENROUTER_API_URL = 'https://openrouter.ai/api/v1/chat/completions'
_openrouter_api_key_cache = None  # populated on first use, reused across warm invocations

# Application URL for email links (e.g., the frontend domain)
APPLICATION_URL = os.environ.get('APPLICATION_URL', 'https://www.example.com')

# Allowed file types for presigned upload URLs -- whitelist, not whatever
ALLOWED_UPLOAD_FILE_TYPES = ('json', 'csv')

# Frontend origin allowed to call this API. In a real deployment this
# should be the CloudFront domain or custom domain, not '*'.
CORS_ALLOWED_ORIGIN = os.environ.get('CORS_ALLOWED_ORIGIN', '*')
# Frontend application URL for links in emails (e.g., "View Full Report" button)
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'https://www.example.com')

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# DynamoDB Tables
reviews_table = dynamodb.Table(REVIEWS_TABLE)
products_table = dynamodb.Table(PRODUCTS_TABLE)
users_table = dynamodb.Table(USERS_TABLE)


# =====================================================
# LAMBDA 1: Review Processor (S3 Trigger)
# =====================================================

def lambda_handler_review_processor(event, context):
    """
    Triggered by S3 event when review files are uploaded.
    Validates, cleans, deduplicates, and stores reviews to DynamoDB.

    Expected event structure:
    {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": "raw-reviews-bucket"},
                    "object": {"key": "uploads/reviews.json"}
                }
            }
        ]
    }
    """

    try:
        logger.info(f"Event received: {json.dumps(event)}")

        for record in event.get('Records', []):
            bucket = record['s3']['bucket']['name']
            key = record['s3']['object']['key']

            logger.info(f"Processing file: s3://{bucket}/{key}")

            # Read the deep-insight choice back out of the key path (see
            # generate_presigned_url) -- defaults to False for anything
            # that doesn't match the expected .../deep/... or
            # .../standard/... shape, e.g. files placed directly by a
            # script rather than through the UI's upload flow.
            # Also extract user_id from path for data isolation
            use_deep_insight = '/deep/' in key
            path_parts = key.split('/')
            if len(path_parts) >= 4 and path_parts[0] == 'uploads':
                user_id = path_parts[3]
                logger.info(f"Extracted user_id from S3 path: {user_id}")
            else:
                user_id = 'system'
                logger.info(f"Using default user_id: {user_id} (path_parts length: {len(path_parts)}, first: {path_parts[0] if path_parts else 'None'})")

            # Read file from S3
            response = s3.get_object(Bucket=bucket, Key=key)
            content = response['Body'].read().decode('utf-8')

            # Parse file (support JSON and CSV)
            reviews = parse_review_file(content, key)

            # Validate and process reviews
            processed_count = 0
            skipped_count = 0

            for review in reviews:
                try:
                    # Map whatever column names this file actually used
                    # onto our internal schema before validating.
                    review = normalize_review_fields(review)

                    # Validate review data
                    if not validate_review(review):
                        logger.warning(f"Invalid review skipped: {review}")
                        skipped_count += 1
                        continue

                    # Check for duplicates
                    if is_duplicate(review):
                        logger.info(f"Duplicate review skipped: {review.get('product_id')}")
                        skipped_count += 1
                        continue

                    # Clean text data
                    review = clean_review_data(review)

                    # Store to DynamoDB
                    store_review(review, use_deep_insight=use_deep_insight, user_id=user_id)
                    processed_count += 1

                except Exception as e:
                    logger.error(f"Error processing review: {str(e)}")
                    skipped_count += 1
                    continue

            logger.info(f"File processing complete: {processed_count} processed, {skipped_count} skipped")

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Reviews processed successfully',
                'processed_count': processed_count,
                'skipped_count': skipped_count
            })
        }

    except Exception as e:
        logger.error(f"Fatal error in review processor: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def parse_review_file(content: str, key: str) -> List[Dict]:
    """Parse JSON or CSV review files"""

    try:
        if key.endswith('.json'):
            data = json.loads(content)
            return data if isinstance(data, list) else [data]

        elif key.endswith('.csv'):
            import csv
            from io import StringIO

            reader = csv.DictReader(StringIO(content))
            return [dict(row) for row in reader]

        else:
            raise ValueError(f"Unsupported file format: {key}")

    except Exception as e:
        logger.error(f"Error parsing file {key}: {str(e)}")
        raise


# Maps common alternate column names onto our internal snake_case schema
# (product_id, user_id, review_text, rating, ...). Without this,
# validate_review() rejects every single row of a file that doesn't use
# our exact field names -- including very common real-world datasets,
# e.g. Amazon Fine Food Reviews (Id/ProductId/UserId/Score/Time/Text/
# Summary/ProfileName), silently, with no error surfaced beyond the
# Lambda logs. Each internal field name maps to itself too, so a file
# that already uses our schema is unaffected (a no-op).
FIELD_ALIASES = {
    'product_id': ['productid', 'product', 'asin', 'sku', 'itemid'],
    'user_id': ['userid', 'reviewerid', 'customerid'],
    'review_text': ['text', 'reviewtext', 'review', 'comment', 'body', 'content'],
    'rating': ['score', 'stars', 'starrating'],
    'created_at': ['time', 'timestamp', 'date', 'reviewdate', 'created'],
    'title': ['summary', 'headline'],
    'reviewer_name': ['profilename', 'username', 'author'],
    'helpful_count': ['helpfulnessnumerator', 'helpful'],
    'verified_purchase': ['verified'],
}

_ALIAS_TO_FIELD = {}
for _field, _aliases in FIELD_ALIASES.items():
    _ALIAS_TO_FIELD[_field] = _field
    for _alias in _aliases:
        _ALIAS_TO_FIELD[_alias] = _field


def _normalize_key(key: str) -> str:
    """Lowercases and strips spaces/underscores, so 'Product Id',
    'ProductId', and 'product_id' all resolve to the same lookup key."""
    return re.sub(r'[\s_]+', '', key.strip().lower())


def normalize_review_fields(review: Dict) -> Dict:
    """
    Renames a row's actual columns onto our internal field names via
    FIELD_ALIASES, case-insensitively. Also converts a Unix-timestamp
    'created_at' (e.g. Kaggle's "Time" column, seconds since epoch) into
    the ISO 8601 string the rest of the pipeline expects -- a rename
    alone wouldn't be enough there, the value itself needs converting.

    Unrecognized columns are dropped rather than raising -- a file with
    extra columns we don't understand should still process on the
    columns we do recognize, not fail outright.
    """
    normalized: Dict = {}
    for raw_key, value in review.items():
        if value in (None, ''):
            continue
        field = _ALIAS_TO_FIELD.get(_normalize_key(str(raw_key)))
        if field and field not in normalized:
            normalized[field] = value

    if 'created_at' in normalized:
        raw = str(normalized['created_at']).strip()
        if re.match(r'^\d+$', raw):
            try:
                normalized['created_at'] = datetime.utcfromtimestamp(int(raw)).isoformat()
            except (ValueError, OSError, OverflowError):
                pass  # leave as-is; clean_review_data() falls back to "now" if this doesn't parse later

    return normalized


def validate_review(review: Dict) -> bool:
    """Validate required review fields"""

    required_fields = ['product_id', 'user_id', 'review_text', 'rating']

    for field in required_fields:
        if field not in review or not review[field]:
            logger.warning(f"Missing required field: {field}")
            return False

    # Validate rating is 1-5
    try:
        rating = float(review['rating'])
        if rating < 1 or rating > 5:
            return False
    except (ValueError, TypeError):
        return False

    # Validate text length (between 5 and 5000 chars)
    text = str(review.get('review_text', ''))
    if len(text) < 5 or len(text) > 5000:
        return False

    return True


def is_duplicate(review: Dict) -> bool:
    """Check if review already exists in DynamoDB"""

    try:
        # NOTE: previously used Limit=1 together with FilterExpression --
        # in DynamoDB, Limit caps how many items get evaluated against
        # the key condition BEFORE the filter is applied, not how many
        # matching results come back after filtering. With Limit=1, this
        # only ever inspected a single, essentially arbitrary item from
        # the partition (ReviewID is a random UUID, not time-ordered) and
        # checked *that one* against the filter -- it almost never had a
        # real chance to find an actual duplicate elsewhere in the
        # partition. Every re-upload of the same file was silently
        # creating fresh duplicates instead of being caught.
        #
        # Fixed by querying the full partition (paginating if needed) and
        # filtering client-side in Python -- also fixes a second issue:
        # the old FilterExpression compared the full stored ReviewText
        # against only the first 100 characters of the incoming text,
        # which only coincidentally worked for reviews under 100 chars.
        review_text = review['review_text']
        user_id = review['user_id']

        items = []
        query_kwargs = {
            'KeyConditionExpression': 'ProductID = :pid',
            'ExpressionAttributeValues': {':pid': review['product_id']},
        }
        while True:
            response = reviews_table.query(**query_kwargs)
            items.extend(response.get('Items', []))
            last_key = response.get('LastEvaluatedKey')
            if not last_key:
                break
            query_kwargs['ExclusiveStartKey'] = last_key

        return any(
            item.get('UserID') == user_id and item.get('ReviewText') == review_text
            for item in items
        )

    except Exception as e:
        logger.error(f"Error checking duplicate: {str(e)}")
        return False


def clean_review_data(review: Dict) -> Dict:
    """Clean and normalize review data"""

    cleaned = {
        'product_id': str(review.get('product_id')).strip(),
        'user_id': str(review.get('user_id')).strip(),
        'review_text': str(review.get('review_text')).strip(),
        'rating': float(review.get('rating')),
        'review_id': str(uuid.uuid4()),
        'source': review.get('source', 'upload'),
        'created_at': review.get('created_at', datetime.utcnow().isoformat()),
        'sentiment': 'PENDING'
    }

    # Add optional fields if present
    optional_fields = ['title', 'reviewer_name', 'verified_purchase', 'helpful_count']
    for field in optional_fields:
        if field in review:
            cleaned[field] = review[field]

    # Clean HTML/special characters from text
    cleaned['review_text'] = re.sub(r'<[^>]+>', '', cleaned['review_text'])
    cleaned['review_text'] = cleaned['review_text'].replace('\n', ' ').replace('\t', ' ')

    return cleaned


def store_review(review: Dict, use_deep_insight: bool = False, user_id: str = 'system') -> None:
    """Store review to DynamoDB"""

    logger.info(f"Storing review for product: {review.get('product_id')}, user_id: {user_id}")

    item = {
        'ProductID': review['product_id'],
        'ReviewID': review['review_id'],
        'UserID': review['user_id'],
        'UploadedBy': user_id,  # Track which user uploaded this review
        'ReviewText': review['review_text'],
        'Rating': Decimal(str(review['rating'])),
        'Source': review.get('source', 'upload'),
        'CreatedAt': review['created_at'],
        'Sentiment': review.get('sentiment', 'PENDING'),
        # NOTE: this MUST be 'PENDING', not e.g. 'QUEUED' -- the DynamoDB
        # Stream event-source-mapping filter in Terraform (and the guard
        # in lambda_handler_sentiment_analyzer below) only forwards/accepts
        # records where ProcessingStatus == 'PENDING'. A mismatched value
        # here silently breaks the entire sentiment analysis pipeline.
        'ProcessingStatus': 'PENDING',
        # Carries the user's upload-time checkbox choice through to the
        # sentiment analyzer, which runs later via a DynamoDB Stream
        # trigger and has no other way to know what was chosen.
        'UseDeepInsight': use_deep_insight
    }

    # Add optional fields
    if 'title' in review:
        item['Title'] = review['title']
    if 'reviewer_name' in review:
        item['ReviewerName'] = review.get('reviewer_name')
    if 'verified_purchase' in review:
        item['VerifiedPurchase'] = review.get('verified_purchase')

    reviews_table.put_item(Item=item)
    logger.info(f"Stored review: {review['product_id']} / {review['review_id']}")

    # NOTE: this call was missing entirely from the original design.
    # Nothing in the review pipeline ever wrote to the Products table --
    # only the separate, user-facing POST /products endpoint did (and
    # that endpoint always generates its own random product_id via
    # uuid.uuid4(), ignoring any ID the caller sends, so it could never
    # produce a record matching an already-uploaded review's product_id
    # anyway). Without this, reviews for a product nobody explicitly
    # registered first were permanently invisible in the dashboard --
    # GET /products would never return them, even though the reviews
    # themselves were stored and processed correctly.
    ensure_product_exists(review['product_id'], user_id)


def ensure_product_exists(product_id: str, user_id: str) -> None:
    """
    Auto-registers a minimal Products record for product_id if one
    doesn't already exist yet. Called from store_review() so the S3
    upload pipeline registers its product automatically -- matching how
    a real review pipeline behaves (reviews arrive for products that
    exist in the source catalog, not ones a human manually pre-creates
    one at a time through a form).

    Uses a conditional put so this never overwrites a product that was
    already properly created (e.g. via POST /products with a real name/
    category) -- it only fills the gap when nothing exists yet.
    """
    try:
        logger.info(f"Attempting to ensure product exists: {product_id} for user: {user_id}")
        products_table.put_item(
            Item={
                'ProductID': product_id,
                'Name': product_id,
                'Category': 'Uncategorized',
                'CreatedBy': user_id,
                'CreatedAt': datetime.utcnow().isoformat(),
                'ReviewCount': 0,
                'AverageRating': Decimal('0'),
                'AverageSentimentScore': Decimal('0')
            },
            ConditionExpression='attribute_not_exists(ProductID)'
        )
        logger.info(f"Auto-registered product: {product_id} for user: {user_id}")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            pass  # Product already exists -- nothing to do, this is the expected common case
        else:
            raise


# =====================================================
# LAMBDA 2: Sentiment Analyzer
# =====================================================

def lambda_handler_sentiment_analyzer(event, context):
    """
    Triggered by DynamoDB Stream when new reviews are added.
    Performs sentiment analysis using Comprehend and optionally OpenRouter
    (Meta Llama 3.1 8B Instruct) for a deeper natural-language pass.
    Updates review with sentiment scores and keywords.
    Triggers alerts if negative sentiment is detected.

    Event structure from DynamoDB Stream:
    {
        "Records": [
            {
                "dynamodb": {
                    "NewImage": {
                        "ProductID": {"S": "PROD-001"},
                        "ReviewID": {"S": "review-uuid"},
                        "ReviewText": {"S": "..."}
                    }
                }
            }
        ]
    }
    """

    try:
        logger.info(f"Sentiment analyzer triggered: {json.dumps(event)}")

        processed_reviews = 0
        sentiment_counts = {'POSITIVE': 0, 'NEGATIVE': 0, 'NEUTRAL': 0, 'MIXED': 0}
        # Track reviews by user_id who uploaded them and product_id for email summaries
        user_reviews = {}  # Dict of user_id -> list of (product_id, sentiment_result)

        for record in event.get('Records', []):
            try:
                # Extract review from DynamoDB stream
                new_image = record['dynamodb'].get('NewImage', {})

                if not new_image:
                    continue

                product_id = new_image.get('ProductID', {}).get('S')
                review_id = new_image.get('ReviewID', {}).get('S')
                review_text = new_image.get('ReviewText', {}).get('S')
                rating = float(new_image.get('Rating', {}).get('N', 0))

                # Track user_id who uploaded this review (from UploadedBy field)
                uploaded_by_user_id = new_image.get('UploadedBy', {}).get('S')

                # IMPORTANT: only analyze reviews that are still PENDING.
                # update_review_sentiment() (below) writes ProcessingStatus
                # = 'COMPLETED' back to this same table, which re-emits a
                # stream record and would re-trigger this very function
                # forever if we didn't skip it here. For belt-and-suspenders
                # protection, also add a DynamoDB Stream filter expression
                # in Terraform scoped to ProcessingStatus = PENDING so
                # already-completed records never even invoke this Lambda.
                processing_status = new_image.get('ProcessingStatus', {}).get('S')
                if processing_status and processing_status != 'PENDING':
                    logger.info(
                        f"Skipping {product_id}/{review_id}: "
                        f"ProcessingStatus={processing_status} (already handled)"
                    )
                    continue

                if not all([product_id, review_id, review_text]):
                    logger.warning("Missing required fields in stream record")
                    continue

                # The upload-time checkbox choice, carried through via
                # store_review() -> DynamoDB -> this stream record.
                # DynamoDB Streams represent booleans as {"BOOL": ...};
                # default to False if the attribute is somehow absent
                # (e.g. a review written before this feature existed).
                use_deep_insight = new_image.get('UseDeepInsight', {}).get('BOOL', False)

                logger.info(f"Analyzing review: {product_id}/{review_id} (deep_insight={use_deep_insight})")

                # Perform sentiment analysis
                sentiment_result = analyze_sentiment(review_text)

                # Optional: Get deeper insights from OpenRouter (Meta Llama 3.1 8B
                # Instruct) -- only when the uploader explicitly opted in via the
                # checkbox. Comprehend's score above is always the source of
                # truth regardless; this is additive and must never block the
                # pipeline if it fails or if OpenRouter is unreachable/over budget.
                advanced_insights = None
                if use_deep_insight:
                    try:
                        advanced_insights = get_deep_insights(review_text, rating)
                    except Exception as e:
                        logger.warning(f"OpenRouter deep-insight call failed, continuing with Comprehend result only: {str(e)}")

                # Update review with sentiment data
                update_review_sentiment(product_id, review_id, sentiment_result, advanced_insights)
                processed_reviews += 1

                # Track sentiment counts for summary
                sentiment = sentiment_result['sentiment']
                if sentiment in sentiment_counts:
                    sentiment_counts[sentiment] += 1

                # Track reviews by user for email summary
                if uploaded_by_user_id and product_id:
                    if uploaded_by_user_id not in user_reviews:
                        user_reviews[uploaded_by_user_id] = []
                    user_reviews[uploaded_by_user_id].append({
                        'product_id': product_id,
                        'sentiment_result': sentiment_result
                    })

            except Exception as e:
                logger.error(f"Error processing record: {str(e)}")
                continue

        # Log summary of sentiment analysis
        total_reviews = sum(sentiment_counts.values())
        logger.info(f"Analysis Complete\n"
                   f"✓ Total Reviews     {total_reviews}\n"
                   f"😊 Positive         {sentiment_counts['POSITIVE']}\n"
                   f"😐 Neutral           {sentiment_counts['NEUTRAL']}\n"
                   f"☹ Negative          {sentiment_counts['NEGATIVE']}\n"
                   f"😕 Mixed             {sentiment_counts['MIXED']}")

        # Send email summary to users who uploaded the processed reviews
        emails_sent = 0
        emails_skipped = 0
        for user_id, reviews in user_reviews.items():
            user_email = get_user_email(user_id)
            if user_email:
                # Calculate aggregate totals across ALL products for this user
                total_user_reviews = len(reviews)
                user_sentiment_counts = {'POSITIVE': 0, 'NEGATIVE': 0, 'NEUTRAL': 0, 'MIXED': 0}

                # Optional: Also track per-product breakdown for the email if needed
                # But per user request, we'll send one summary per user (not per product)
                for review in reviews:
                    sentiment = review['sentiment_result']['sentiment']
                    if sentiment in user_sentiment_counts:
                        user_sentiment_counts[sentiment] += 1

                # Send a single summary email for this user (all their products combined)
                if send_email_summary(user_email, user_id, user_sentiment_counts, total_user_reviews):
                    emails_sent += 1
                    logger.info(f"Sent sentiment analysis email to {user_email} for user {user_id}")
                else:
                    emails_skipped += 1
                    logger.warning(f"Failed to send sentiment analysis email to {user_email} for user {user_id}")
            else:
                emails_skipped += 1
                logger.warning(f"Skipping email sending for user {user_id} - no email address available")

        if emails_sent > 0:
            logger.info(f"Email summary complete: {emails_sent} emails sent, {emails_skipped} skipped")
        elif emails_skipped > 0:
            logger.warning(f"Email summary complete: 0 emails sent, {emails_skipped} skipped (check user email configuration)")
        else:
            logger.info("Email summary complete: No emails to send (no reviews processed)")

        return {
            'statusCode': 200,
            'body': json.dumps({
                'processed_reviews': processed_reviews,
                'sentiment_counts': sentiment_counts,
                'total_reviews': total_reviews
            })
        }

    except Exception as e:
        logger.error(f"Fatal error in sentiment analyzer: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def analyze_sentiment(text: str) -> Dict[str, Any]:
    """
    Use Amazon Comprehend for sentiment analysis.
    Supports multiple languages automatically.

    Returns:
    {
        'sentiment': 'POSITIVE'|'NEGATIVE'|'NEUTRAL'|'MIXED',
        'scores': {
            'Positive': float,
            'Negative': float,
            'Neutral': float,
            'Mixed': float
        },
        'key_phrases': [str],
        'language': str
    }
    """

    try:
        # Detect language first
        lang_response = comprehend.detect_dominant_language(Text=text)
        language = lang_response['Languages'][0]['LanguageCode']
        logger.info(f"Detected language: {language}")

        # Perform sentiment analysis
        sentiment_response = comprehend.detect_sentiment(
            Text=text,
            LanguageCode=language
        )

        # Extract key phrases
        phrases_response = comprehend.detect_key_phrases(
            Text=text,
            LanguageCode=language
        )

        key_phrases = [phrase['Text'] for phrase in phrases_response.get('KeyPhrases', [])][:10]

        return {
            'sentiment': sentiment_response['Sentiment'],
            'scores': sentiment_response['SentimentScore'],
            'key_phrases': key_phrases,
            'language': language
        }

    except Exception as e:
        logger.error(f"Comprehend analysis failed: {str(e)}")
        raise


def _get_openrouter_api_key() -> str:
    """
    Fetch the OpenRouter API key from Secrets Manager, cached for the
    lifetime of this execution environment so a warm Lambda doesn't
    re-fetch it on every invocation. The key is never logged, never
    stored in an environment variable, and never committed to source --
    only this one secret, read at runtime.
    """
    global _openrouter_api_key_cache
    if _openrouter_api_key_cache is None:
        response = secretsmanager.get_secret_value(SecretId=OPENROUTER_API_KEY_SECRET_NAME)
        _openrouter_api_key_cache = response['SecretString']
    return _openrouter_api_key_cache


def get_deep_insights(review_text: str, rating: float) -> Dict[str, Any]:
    """
    Use OpenRouter (Meta Llama 3.1 8B Instruct) for advanced analysis.
    Extracts aspect-based sentiment, action items, and detailed insights.

    This is a pay-as-you-go model ($0.02 / $0.03 per 1M input/output
    tokens,output
    tokens, no free tier) called over plain HTTPS -- not a Bedrock/AWS
    SDK call, so it needs outbound internet access, which a Lambda has
    by default as long as it isn't placed in a VPC. If this call fails
    or times out for any reason, the caller falls back to the Comprehend
    result alone; this function must never raise in a way that breaks
    the pipeline.
    """

    try:
        api_key = _get_openrouter_api_key()

        payload = {
            'model': OPENROUTER_MODEL,
            'messages': [
                {'role': 'user', 'content': prompt}
            ],
            'max_tokens': 1024,
            'temperature': 0.2  # low temperature: consistent JSON, not creativity
        }

        response = http.request(
            'POST',
            OPENROUTER_API_URL,
            body=json.dumps(payload).encode('utf-8'),
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            },
            timeout=urllib3.Timeout(connect=5.0, read=25.0)
        )

        if response.status != 200:
            logger.warning(f"OpenRouter returned HTTP {response.status}, skipping insights")
            return {}

        body = json.loads(response.data.decode('utf-8'))
        insights_text = body['choices'][0]['message']['content'].strip()

        # The model sometimes wraps JSON in markdown code fences despite
        # instructions not to -- strip them defensively before parsing.
        if insights_text.startswith('```'):
            insights_text = re.sub(r'^```(?:json)?\s*|\s*```$', '', insights_text.strip())

        try:
            insights = json.loads(insights_text)
        except json.JSONDecodeError:
            # Smaller/free models in particular are prone to adding
            # conversational text around the JSON despite explicit
            # instructions not to -- e.g. "Here's the analysis:" before
            # it, or trailing commentary after. The JSON itself is often
            # still perfectly valid; only the surrounding text broke a
            # naive parse. Fall back to extracting the outermost {...}
            # block and retrying before giving up entirely.
            match = re.search(r'\{.*\}', insights_text, re.DOTALL)
            if not match:
                raise
            insights = json.loads(match.group(0))

        # Record which model actually served this request -- OpenRouter's
        # own response body is the authoritative source (body['model']),
        # more reliable than just echoing back what was requested, in
        # case OpenRouter ever does provider-side fallback routing.
        # Stamped onto the review itself (see update_review_sentiment)
        # so which model analyzed which review stays visible per-review
        # in the dashboard, not just as a Lambda environment variable you
        # have to go check separately -- and stays accurate historically
        # even after OPENROUTER_MODEL is later changed to something else.
        model_used = body.get('model', OPENROUTER_MODEL)
        logger.info(f"OpenRouter deep-insight call served by model: {model_used}")
        insights['_model_used'] = model_used

        return insights

    except json.JSONDecodeError as e:
        logger.warning(f"OpenRouter returned non-JSON response, skipping insights: {str(e)}")
        return {}
    except Exception as e:
        logger.error(f"OpenRouter deep-insight call failed: {str(e)}")
        return {}


def update_review_sentiment(product_id: str, review_id: str,
                           sentiment_result: Dict, advanced_insights: Dict = None) -> None:
    """Update review in DynamoDB with sentiment analysis results"""

    try:
        # NOTE: sentiment_result['scores'] comes straight from Comprehend
        # (via analyze_sentiment()) as plain Python floats -- Comprehend
        # isn't DynamoDB, so botocore doesn't wrap its numbers in Decimal.
        # boto3's DynamoDB *resource* interface, on the other hand,
        # rejects raw floats outright on write ("Float types are not
        # supported. Use Decimal types instead."). Without this
        # conversion, this update_item call raises on every single
        # review, permanently stuck at Sentiment=PENDING with no visible
        # frontend error -- the review "succeeds" at the S3/store_review
        # stage, then silently fails one step later here.
        sentiment_scores = {k: Decimal(str(v)) for k, v in sentiment_result['scores'].items()}

        update_data = {
            'Sentiment': sentiment_result['sentiment'],
            'SentimentScores': sentiment_scores,
            'KeyPhrases': sentiment_result['key_phrases'],
            'Language': sentiment_result['language'],
            'AnalyzedAt': datetime.utcnow().isoformat(),
            'ProcessingStatus': 'COMPLETED'
        }

        # Add OpenRouter deep-insight fields if the optional call succeeded
        if advanced_insights:
            update_data['Aspects'] = advanced_insights.get('main_aspects', [])
            update_data['AspectSentiments'] = advanced_insights.get('aspect_sentiments', [])
            update_data['ActionItems'] = advanced_insights.get('action_items', [])
            update_data['Summary'] = advanced_insights.get('summary', '')
            update_data['DeepInsightModel'] = advanced_insights.get('_model_used', OPENROUTER_MODEL)

        # Build update expression
        # NOTE: previously built as `f"{k} = :{k}"` with raw attribute
        # names directly in the UpdateExpression -- DynamoDB has a long
        # list of reserved words (Language, Name, Status, Date, Timestamp,
        # Data, and dozens more: https://docs.aws.amazon.com/amazon
        # dynamodb/latest/developerguide/ReservedWords.html), and using
        # any of them unescaped raises "Attribute name is a reserved
        # keyword". Rather than special-case the ones we've hit so far,
        # every attribute name is now aliased via ExpressionAttributeNames
        # (#k placeholders) universally, so no future field added to
        # update_data can hit this class of bug again, reserved or not.
        update_expr = 'SET ' + ', '.join([f"#{k} = :{k}" for k in update_data.keys()])
        expr_names = {f"#{k}": k for k in update_data.keys()}
        expr_values = {f":{k}": v for k, v in update_data.items()}

        reviews_table.update_item(
            Key={'ProductID': product_id, 'ReviewID': review_id},
            UpdateExpression=update_expr,
            ExpressionAttributeNames=expr_names,
            ExpressionAttributeValues=expr_values
        )

        logger.info(f"Updated review sentiment: {product_id}/{review_id}")

    except Exception as e:
        logger.error(f"Error updating sentiment: {str(e)}")
        raise


def get_user_email(user_id: str) -> Optional[str]:
    """Get user email from Cognito User Pool"""
    try:
        if not USER_POOL_ID:
            logger.warning("USER_POOL_ID not configured, falling back to Users table")
            # Fallback to original Users table method for backward compatibility
            response = users_table.get_item(
                Key={'UserID': user_id}
            )
            user_item = response.get('Item')
            if user_item and 'Email' in user_item:
                return user_item['Email']
            else:
                logger.warning(f"No email found for user {user_id} in Users table")
                return None

        # Get user from Cognito
        response = cognitoidp.admin_get_user(
            UserPoolId=USER_POOL_ID,
            Username=user_id  # In our system, user_id is the Cognito 'sub' claim
        )

        # Extract email from user attributes
        for attribute in response['UserAttributes']:
            if attribute['Name'] == 'email':
                return attribute['Value']

        logger.warning(f"No email attribute found for user {user_id} in Cognito")
        return None

    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'UserNotFoundException':
            logger.warning(f"User {user_id} not found in Cognito User Pool")
        elif error_code == 'AccessDeniedException':
            logger.error(
                f"Missing Cognito permissions for sentiment analyzer. "
                f"Please add cognito-idp:AdminGetUser permission for user pool {USER_POOL_ID}. "
                f"Error: {str(e)}"
            )
        else:
            logger.error(f"AWS service error getting user email for {user_id}: {error_code} - {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error getting user email for {user_id}: {str(e)}")
        return None


def send_email_summary(user_email: str, user_id: str, sentiment_counts: Dict[str, int], total_reviews: int) -> bool:
    """Send email summary of sentiment analysis results via SES (HTML format matching requested design)"""

    # Format the summary message as HTML
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; }}
        .header {{
            background-color: #4CAF50;
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 8px 8px 0 0;
        }}
        .content {{
            background-color: #f9f9f9;
            padding: 30px;
            border-radius: 0 0 8px 8px;
            border: 1px solid #ddd;
            border-top: none;
        }}
        .stats {{
            display: flex;
            justify-content: space-around;
            margin: 25px 0;
            flex-wrap: wrap;
        }}
        .stat-box {{
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 15px;
            min-width: 100px;
            text-align: center;
            margin: 5px;
        }}
        .stat-value {{
            font-size: 24px;
            font-weight: bold;
            margin: 10px 0;
        }}
        .stat-label {{
            font-size: 14px;
            color: #666;
            text-transform: capitalize;
        }}
        .button {{
            display: inline-block;
            background-color: #4CAF50;
            color: white;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 4px;
            font-weight: bold;
            margin-top: 20px;
        }}
        .button:hover {{ background-color: #45a049; }}
        .footer {{
            margin-top: 30px;
            font-size: 12px;
            color: #999;
            text-align: center;
        }}
        .emoji {{
            font-size: 18px;
            margin-right: 8px;
            vertical-align: middle;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>Analysis Complete</h2>
        </div>
        <div class="content">
            <div class="stats">
                <div class="stat-box">
                    <div class="emoji">📊</div>
                    <div class="stat-value">{total_reviews}</div>
                    <div class="stat-label">total reviews</div>
                </div>
                <div class="stat-box">
                    <div class="emoji">😊</div>
                    <div class="stat-value">{sentiment_counts.get('POSITIVE', 0)}</div>
                    <div class="stat-label">positive</div>
                </div>
                <div class="stat-box">
                    <div class="emoji">😐</div>
                    <div class="stat-value">{sentiment_counts.get('NEUTRAL', 0)}</div>
                    <div class="stat-label">neutral</div>
                </div>
                <div class="stat-box">
                    <div class="emoji">☹</div>
                    <div class="stat-value">{sentiment_counts.get('NEGATIVE', 0)}</div>
                    <div class="stat-label">negative</div>
                </div>
                <div class="stat-box">
                    <div class="emoji">😕</div>
                    <div class="stat-value">{sentiment_counts.get('MIXED', 0)}</div>
                    <div class="stat-label">mixed</div>
                </div>
            </div>
            <a href="{APPLICATION_URL}/user/{user_id}/report" class="button">View Full Report</a>
            <div class="footer">
                This is an automated message from Review Sentiment Analyzer.
            </div>
        </div>
    </div>
</body>
</html>
"""

    # Also create a plain text version for email clients that don't support HTML
    text_body = f"""
Analysis Complete
================

📊 Total Reviews:     {total_reviews}
😊 Positive:          {sentiment_counts.get('POSITIVE', 0)}
😐 Neutral:           {sentiment_counts.get('NEUTRAL', 0)}
☹ Negative:          {sentiment_counts.get('NEGATIVE', 0)}
😕 Mixed:             {sentiment_counts.get('MIXED', 0)}

View Full Report: {APPLICATION_URL}/user/{user_id}/report

--
This is an automated message from Review Sentiment Analyzer.
"""

    try:
        response = ses.send_email(
            Source=SES_SOURCE_EMAIL,  # Use configured source email
            Destination={
                'ToAddresses': [user_email]
            },
            Message={
                'Subject': {
                    'Data': f'Sentiment Analysis Summary for User {user_id}',
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Text': {
                        'Data': text_body,
                        'Charset': 'UTF-8'
                    },
                    'Html': {
                        'Data': html_body,
                        'Charset': 'UTF-8'
                    }
                }
            }
        )

        logger.info(f"Email sent to {user_email}: {response['MessageId']}")
        return True

    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'MessageRejected':
            # Handle SES-specific issues like unverified addresses
            logger.error(
                f"Email rejected by SES for {user_email}. "
                f"This commonly occurs when:\n"
                f"1. Sender address ({SES_SOURCE_EMAIL}) is not verified in SES\n"
                f"2. Recipient address ({user_email}) is not verified in SES (required in sandbox mode)\n"
                f"3. Account is still in SES sandbox\n"
                f"To fix: Verify both sender and recipient addresses in Amazon SES console, "
                f"or request production access for your SES account.\n"
                f"Error details: {str(e)}"
            )
        else:
            logger.error(f"SES client error sending email to {user_email}: {error_code} - {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error sending email to {user_email}: {str(e)}")
        return False


def add_cors_headers(response):
    """
    Add CORS headers to API Gateway response
    """
    if 'headers' not in response:
        response['headers'] = {}

    response['headers'].update({
        'Access-Control-Allow-Origin': CORS_ALLOWED_ORIGIN,
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
    })

    return response


# =====================================================
# LAMBDA 3: API Handler
# =====================================================

def add_cors_headers(response):
    """
    Add CORS headers to API Gateway response
    """
    if 'headers' not in response:
        response['headers'] = {}

    response['headers'].update({
        'Access-Control-Allow-Origin': CORS_ALLOWED_ORIGIN,
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
    })

    return response


def lambda_handler_api(event, context):
    """
    Main API handler. Also doubles as the target for a scheduled
    EventBridge rule (per the architecture diagram: EventBridge -> API
    Lambda), so this function is invoked in one of two distinct shapes:

    1. EventBridge scheduled event (no 'httpMethod'/'path', has
       event['source'] == 'aws.events') -> runs the daily digest job,
       no HTTP response needed.
    2. Cognito-authenticated API Gateway request (Authorization: Bearer
       <JWT>) -> event['requestContext']['authorizer']['claims'] is
       populated by the COGNITO_USER_POOLS authorizer.

    Endpoints:
    - GET /products - List all products
    - GET /products/{id} - Get product details
    - POST /products - Create new product
    - GET /products/{id}/reviews - Get reviews for product
    - GET /products/{id}/analytics - Get sentiment analytics
    - POST /upload - Generate S3 presigned URL (Cognito-authenticated)
    - POST /analyze - Synchronously analyze a single review, no persistence (Cognito-authenticated)
    - DELETE /products/{id} - Delete a product and cascade-delete its reviews
    - DELETE /products/{id}/reviews/{review_id} - Delete a single review
    """

    # Shape 1: EventBridge scheduled trigger, not an API Gateway proxy event at all.
    if event.get('source') == 'aws.events':
        return run_scheduled_digest()

    try:
        # Extract request details
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '')
        body = json.loads(event.get('body', '{}')) if event.get('body') else {}

        # Get authenticated user from Cognito -- every remaining route is
        # Cognito-authenticated, but .get() chains stay defensive rather
        # than assuming the shape, cheap insurance against a KeyError.
        user_id = (
            event.get('requestContext', {})
            .get('authorizer', {})
            .get('claims', {})
            .get('sub')
        )

        logger.info(f"{http_method} {path} - User: {user_id}")

        # Route to appropriate handler
        if path == '/products' and http_method == 'GET':
            return add_cors_headers(get_products(user_id))

        elif path.startswith('/products/') and '/reviews/' in path and http_method == 'DELETE':
            # /products/{id}/reviews/{review_id} -- must be checked before
            # the more general '/reviews' GET check below, since this path
            # also contains "/reviews".
            parts = path.split('/')
            product_id = parts[2]
            review_id = parts[4]
            return add_cors_headers(delete_review(product_id, review_id, user_id))

        elif path.startswith('/products/') and '/reviews' in path and http_method == 'GET':
            product_id = path.split('/')[2]
            return add_cors_headers(get_product_reviews(product_id, user_id))

        elif path.startswith('/products/') and '/analytics' in path and http_method == 'GET':
            product_id = path.split('/')[2]
            return add_cors_headers(get_product_analytics(product_id, user_id))

        elif path == '/products' and http_method == 'POST':
            return add_cors_headers(create_product(body, user_id))

        elif path.startswith('/products/') and '/reviews' not in path and '/analytics' not in path and http_method == 'DELETE':
            # /products/{id} -- cascade-deletes the product and all its reviews.
            product_id = path.split('/')[2]
            return add_cors_headers(delete_product(product_id, user_id))

        elif path == '/upload' and http_method == 'POST':
            return add_cors_headers(generate_presigned_url(body, user_id))

        elif path == '/analyze' and http_method == 'POST':
            return add_cors_headers(analyze_single_review(body))

        else:
            return add_cors_headers({
                'statusCode': 404,
                'body': json.dumps({'error': 'Endpoint not found'})
            })

    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return add_cors_headers({
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        })


def run_scheduled_digest():
    """
    EventBridge-triggered daily digest (rate(1 day)). Scans Products,
    rolls up each product's negative-sentiment count from the last 24h
    via the SentimentIndex GSI, and publishes a single summary email
    through the existing SNS topic -- reusing infrastructure that's
    already wired up rather than adding new resources (e.g. no need for
    a second S3 "reports" bucket for a study/demo project).
    """
    try:
        products = products_table.scan(Limit=200).get('Items', [])
        cutoff = (datetime.utcnow() - timedelta(days=1)).isoformat()

        lines = []
        for product in products:
            product_id = product['ProductID']
            resp = reviews_table.query(
                IndexName='SentimentIndex',
                KeyConditionExpression='ProductID = :pid AND Sentiment = :s',
                ExpressionAttributeValues={':pid': product_id, ':s': 'NEGATIVE'}
            )
            recent_negative = [
                i for i in resp.get('Items', [])
                if i.get('CreatedAt', '') >= cutoff
            ]
            if recent_negative:
                lines.append(f"{product.get('Name', product_id)}: {len(recent_negative)} negative review(s) in the last 24h")

        if lines and SNS_TOPIC_ARN:
            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject="Daily Sentiment Digest",
                Message="\n".join(lines)
            )
            logger.info(f"Digest sent: {len(lines)} product(s) with negative reviews")
        else:
            logger.info("Digest run: nothing to report")

        return {'statusCode': 200, 'body': json.dumps({'products_flagged': len(lines)})}

    except Exception as e:
        logger.error(f"Digest error: {str(e)}")
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}


def get_products(user_id: str):
    """GET /products - List all products for the current user"""

    try:
        logger.info(f"Getting products for user_id: {user_id}")
        # Return products created by this user
        response = products_table.scan(
            FilterExpression='CreatedBy = :uid',
            ExpressionAttributeValues={':uid': user_id}
        )

        items = response.get('Items', [])
        logger.info(f"Found {len(items)} products for user {user_id}")
        for item in items:
            logger.info(f"Product found: {item.get('ProductID')} - CreatedBy: {item.get('CreatedBy')}")

        products = []
        for item in items:
            product_id = item['ProductID']

            review_response = reviews_table.query(
                KeyConditionExpression='ProductID = :pid',
                ExpressionAttributeValues={':pid': product_id}
            )
            review_items = review_response.get('Items', [])
            review_count = len(review_items)
            ratings = [float(r.get('Rating', 0)) for r in review_items]
            avg_rating = (sum(ratings) / len(ratings)) if ratings else 0
            positive_count = sum(1 for r in review_items if r.get('Sentiment') == 'POSITIVE')
            avg_sentiment_score = (positive_count / review_count) if review_count > 0 else 0

            products.append({
                'product_id': product_id,
                'name': item.get('Name'),
                'category': item.get('Category'),
                'review_count': review_count,
                'avg_rating': round(avg_rating, 2),
                'avg_sentiment_score': round(avg_sentiment_score, 4)
            })

        logger.info(f"Returning {len(products)} processed products")
        return {
            'statusCode': 200,
            'body': json.dumps({
                'products': products,
                'count': len(products)
            })
        }

    except Exception as e:
        logger.error(f"Error getting products: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def get_product_reviews(product_id: str, user_id: str):
    """GET /products/{id}/reviews - Get reviews for product (only if user owns the product)"""

    try:
        # FIRST verify the product belongs to this user
        product_resp = products_table.get_item(
            Key={'ProductID': product_id}
        )

        product_item = product_resp.get('Item')
        if not product_item or product_item.get('CreatedBy') != user_id:
            return {
                'statusCode': 403,
                'body': json.dumps({'error': 'Access denied: product not found or not owned by user'})
            }

        # THEN get reviews for this product (now we know user owns the product)
        items = []
        query_kwargs = {
            'KeyConditionExpression': 'ProductID = :pid',
            'ExpressionAttributeValues': {':pid': product_id},
        }
        while True:
            response = reviews_table.query(**query_kwargs)
            items.extend(response.get('Items', []))
            last_key = response.get('LastEvaluatedKey')
            if not last_key:
                break
            query_kwargs['ExclusiveStartKey'] = last_key

        items.sort(key=lambda x: x.get('CreatedAt', ''), reverse=True)
        items = items[:50]

        reviews = []
        for item in items:
            reviews.append({
                'review_id': item['ReviewID'],
                'user_id': item['UserID'],
                'text': item.get('ReviewText', ''),
                'rating': float(item.get('Rating', 0)),
                'sentiment': item.get('Sentiment'),
                'created_at': item.get('CreatedAt'),
                'key_phrases': item.get('KeyPhrases', []),
                'use_deep_insight': bool(item.get('UseDeepInsight', False)),
                # NOTE: these were previously stored by update_review_sentiment()
                # whenever the (always-on, no-checkbox) OpenRouter call
                # succeeded, but no API response ever included them --
                # the LLM's actual output was invisible no matter what.
                # Only meaningful when use_deep_insight is true; empty/
                # absent otherwise.
                'summary': item.get('Summary'),
                'aspects': item.get('Aspects', []),
                'aspect_sentiments': item.get('AspectSentiments', []),
                'action_items': item.get('ActionItems', []),
                'deep_insight_model': item.get('DeepInsightModel')
            })

        return {
            'statusCode': 200,
            'body': json.dumps({
                'product_id': product_id,
                'reviews': reviews,
                'count': len(reviews)
            })
        }

    except Exception as e:
        logger.error(f"Error getting reviews: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def get_product_analytics(product_id: str, user_id: str):
    """GET /products/{id}/analytics - Get sentiment analytics (only if user owns the product)"""

    try:
        # FIRST verify the product belongs to this user
        product_resp = products_table.get_item(
            Key={'ProductID': product_id}
        )

        product_item = product_resp.get('Item')
        if not product_item or product_item.get('CreatedBy') != user_id:
            return {
                'statusCode': 403,
                'body': json.dumps({'error': 'Access denied: product not found or not owned by user'})
            }

        # THEN get analytics for this product (now we know user owns the product)
        # Query reviews using Sentiment GSI
        gsi_name = 'SentimentIndex'

        response = reviews_table.query(
            IndexName=gsi_name,
            KeyConditionExpression='ProductID = :pid',
            ExpressionAttributeValues={':pid': product_id}
        )

        # Calculate analytics
        sentiments = {'POSITIVE': 0, 'NEGATIVE': 0, 'NEUTRAL': 0, 'MIXED': 0}
        ratings = []

        for item in response.get('Items', []):
            sentiment = item.get('Sentiment', 'UNKNOWN')
            if sentiment in sentiments:
                sentiments[sentiment] += 1
            ratings.append(float(item.get('Rating', 0)))

        total_reviews = sum(sentiments.values())
        avg_rating = sum(ratings) / len(ratings) if ratings else 0

        return {
            'statusCode': 200,
            'body': json.dumps({
                'product_id': product_id,
                'total_reviews': total_reviews,
                'sentiment_distribution': sentiments,
                'average_rating': round(avg_rating, 2),
                'positive_percentage': round((sentiments['POSITIVE'] / total_reviews * 100) if total_reviews > 0 else 0, 2),
                'negative_percentage': round((sentiments['NEGATIVE'] / total_reviews * 100) if total_reviews > 0 else 0, 2)
            })
        }

    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def create_product(body: Dict, user_id: str):
    """POST /products - Create new product"""

    try:
        product_id = str(uuid.uuid4())

        item = {
            'ProductID': product_id,
            'Name': body.get('name'),
            'Category': body.get('category'),
            'CreatedBy': user_id,
            'CreatedAt': datetime.utcnow().isoformat(),
            'ReviewCount': 0,
            'AverageRating': Decimal('0'),
            'AverageSentimentScore': Decimal('0')
        }

        if 'image_url' in body:
            item['ImageURL'] = body['image_url']

        products_table.put_item(Item=item)

        return {
            'statusCode': 201,
            'body': json.dumps({
                'product_id': product_id,
                'message': 'Product created successfully'
            })
        }

    except Exception as e:
        logger.error(f"Error creating product: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def delete_product(product_id: str, user_id: str):
    """
    DELETE /products/{id} - Delete a product and cascade-delete all of
    its reviews.

    Cascading is deliberate, not incidental: ensure_product_exists()
    (called from store_review() on every uploaded review) will silently
    recreate a bare product record -- generic name, category
    "Uncategorized" -- the moment any future review arrives for this
    product_id. Deleting only the Products row without also clearing out
    its reviews wouldn't feel like a real delete; the product would just
    reappear, stripped of any custom name, the next time someone
    uploaded data for it.
    """
    try:
        # FIRST verify ownership
        product_resp = products_table.get_item(Key={'ProductID': product_id})
        product_item = product_resp.get('Item')
        if not product_item or product_item.get('CreatedBy') != user_id:
            return {
                'statusCode': 403,
                'body': json.dumps({'error': 'Access denied: cannot delete product'})
            }

        # THEN proceed with deletion
        review_response = reviews_table.query(
            KeyConditionExpression='ProductID = :pid',
            ExpressionAttributeValues={':pid': product_id}
        )
        review_items = review_response.get('Items', [])

        with reviews_table.batch_writer() as batch:
            for item in review_items:
                batch.delete_item(Key={'ProductID': product_id, 'ReviewID': item['ReviewID']})

        products_table.delete_item(Key={'ProductID': product_id})

        logger.info(f"Deleted product {product_id} and {len(review_items)} review(s)")

        return {
            'statusCode': 200,
            'body': json.dumps({
                'status': 'deleted',
                'product_id': product_id,
                'reviews_deleted': len(review_items)
            })
        }

    except Exception as e:
        logger.error(f"Error deleting product: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def delete_review(product_id: str, review_id: str, user_id: str):
    """DELETE /products/{id}/reviews/{review_id} - Delete a single review (only if user owns the product)"""

    try:
        # FIRST verify the product belongs to this user
        product_resp = products_table.get_item(
            Key={'ProductID': product_id}
        )

        product_item = product_resp.get('Item')
        if not product_item or product_item.get('CreatedBy') != user_id:
            return {
                'statusCode': 403,
                'body': json.dumps({'error': 'Access denied: product not found or not owned by user'})
            }

        # THEN proceed with deletion (now we know user owns the product)
        reviews_table.delete_item(
            Key={'ProductID': product_id, 'ReviewID': review_id},
            ConditionExpression='attribute_exists(ProductID)'
        )
        logger.info(f"Deleted review {product_id}/{review_id}")
        return {
            'statusCode': 200,
            'body': json.dumps({'status': 'deleted', 'review_id': review_id})
        }

    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return {'statusCode': 404, 'body': json.dumps({'error': 'Review not found'})}
        logger.error(f"Error deleting review: {str(e)}")
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
    except Exception as e:
        logger.error(f"Error deleting review: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def generate_presigned_url(body: Dict, user_id: str):
    """POST /upload - Generate presigned URL for S3 upload"""

    try:
        if not body:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Request body is required'})
            }

        file_type = body.get('file_type', 'json')

        # Whitelist file types -- never interpolate caller-controlled
        # strings into an S3 key/path without validating them first.
        if file_type not in ALLOWED_UPLOAD_FILE_TYPES:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': f"Invalid file_type. Allowed values: {', '.join(ALLOWED_UPLOAD_FILE_TYPES)}"
                })
            }

        # The user's "use AI deep insight" checkbox choice has to survive
        # the trip from this API call all the way to the sentiment
        # analyzer Lambda, which runs later and separately (triggered by
        # a DynamoDB Stream record, not by this request). There's no
        # shared request context between them -- so the choice is encoded
        # directly in the S3 key path, which review_processor reads back
        # when it processes the uploaded file and stamps onto every
        # review it stores.
        # Also include user_id for data isolation
        mode = 'deep' if body.get('use_deep_insight') else 'standard'
        key = f"uploads/{datetime.utcnow().strftime('%Y%m%d')}/{mode}/{user_id}/{uuid.uuid4()}.{file_type}"

        presigned_url = s3.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': RAW_BUCKET,
                'Key': key,
                'ContentType': 'application/json' if file_type == 'json' else 'text/csv'
            },
            ExpiresIn=3600  # URL valid for 1 hour
        )

        return {
            'statusCode': 200,
            'body': json.dumps({
                'upload_url': presigned_url,
                'bucket': RAW_BUCKET,
                'key': key,
                'expires_in': 3600
            })
        }

    except Exception as e:
        logger.error(f"Error generating presigned URL: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def analyze_single_review(body: Dict):
    """
    POST /analyze - Synchronously analyze a single review, no persistence (Cognito-authenticated)
    """

    try:
        if not body:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Request body is required'})
            }

        review_text = body.get('review_text')
        rating = float(body.get('rating', 0)) if body.get('rating') else 0.0
        use_deep_insight = bool(body.get('use_deep_insight', False))

        if not review_text:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'review_text is required'})
            }

        if rating < 1 or rating > 5:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'rating must be between 1 and 5'})
            }

        # Perform sentiment analysis
        sentiment_result = analyze_sentiment(review_text)

        # Optional: Get deeper insights from OpenRouter
        advanced_insights = None
        if use_deep_insight:
            try:
                advanced_insights = get_deep_insights(review_text, rating)
            except Exception as e:
                logger.warning(f"OpenRouter deep-insight call failed: {str(e)}")

        # Prepare response
        response_data = {
            'sentiment': sentiment_result['sentiment'],
            'scores': sentiment_result['scores'],
            'key_phrases': sentiment_result['key_phrases'],
            'language': sentiment_result['language']
        }

        if advanced_insights:
            response_data.update({
                'aspects': advanced_insights.get('main_aspects', []),
                'aspect_sentiments': advanced_insights.get('aspect_sentiments', []),
                'action_items': advanced_insights.get('action_items', []),
                'summary': advanced_insights.get('summary', ''),
                'model_used': advanced_insights.get('_model_used', OPENROUTER_MODEL)
            })

        return {
            'statusCode': 200,
            'body': json.dumps(response_data)
        }

    except Exception as e:
        logger.error(f"Error analyzing single review: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }