---
title: "5.4.2 Lambda functions"
weight: 2
---

# Lambda functions for ReviewSentinal

## Overview

Create the three Lambda handlers that power the ingestion, analysis, and API flow. All three functions use the same deployment package, but each one has different runtime settings, environment variables, and trigger wiring.

### Functions to create

1. `review-sentiment-analyzer-processor`
2. `review-sentiment-analyzer-analyzer`
3. `review-sentiment-analyzer-api`

### Shared setup

- Runtime: Python 3.11
- Architecture: x86_64
- Source package: the shared `01_lambda_functions.py` file
- Dead-letter queue: `lambda-dlq`

## Step-by-step

### 1. Create the processor function

1. Open **Lambda** and choose **Create function**.
2. Select **Author from scratch**.
3. Name the function `review-sentiment-analyzer-processor`.
4. Choose Python 3.11 and the default x86_64 architecture.
5. Use the existing role `review-processor-role`.
6. Create the function.
7. Replace the default code with the full contents of `01_lambda_functions.py`.
8. Deploy the code.
9. Open **Runtime settings** and set the handler to `lambda_function.lambda_handler_review_processor`.
10. Set timeout to 1 minute and memory to 512 MB.
11. Add the environment variables for `REVIEWS_TABLE`, `PRODUCTS_TABLE`, `USERS_TABLE`, and `RAW_BUCKET`.
12. Configure the asynchronous invocation DLQ to use `lambda-dlq`.

### 2. Create the analyzer function

1. Create a second Lambda function with the name `review-sentiment-analyzer-analyzer`.
2. Use Python 3.11 and the existing role `sentiment-analyzer-role`.
3. Paste the same deployment package again and deploy it.
4. Set the handler to `lambda_function.lambda_handler_sentiment_analyzer`.
5. Set timeout to 2 minutes and memory to 1024 MB.
6. Add `REVIEWS_TABLE`, `PRODUCTS_TABLE`, `OPENROUTER_MODEL`, and `OPENROUTER_API_KEY_SECRET_NAME`.
7. Configure the same DLQ.
8. **Important**: This function now uses Amazon SES for user notifications instead of SNS. No SNS topic ARN is needed.

### 3. Create the API function

1. Create a third Lambda function named `review-sentiment-analyzer-api`.
2. Use Python 3.11 and the existing role `api-handler-role`.
3. Paste the same deployment package and deploy it.
4. Set the handler to `lambda_function.lambda_handler_api`.
5. Set timeout to 30 seconds and memory to 256 MB.
6. Add `REVIEWS_TABLE`, `PRODUCTS_TABLE`, `USERS_TABLE`, `RAW_BUCKET`, and `CORS_ALLOWED_ORIGIN`.
7. Configure the same DLQ.

### Analysis completion flow (updated)

The analyzer function now follows this flow when processing reviews:
1. Process all review records from the DynamoDB stream batch
2. For each review:
   - Perform sentiment analysis using Comprehend
   - Optionally get deeper insights from OpenRouter if requested
   - Update the review record with sentiment analysis results
   - Track which user uploaded the review (from UploadedBy field)
   - Increment sentiment counters (Positive/Neutral/Negative/Mixed)
3. After processing all records:
   - Log the overall analysis summary
   - Group reviews by the user who uploaded them, then by product
   - For each user-product combination, calculate specific sentiment counts
   - Send a personalized email summary via Amazon SES to each user for each product they uploaded
   - The email includes the analysis summary in the requested format

### Notes

1. Keep all three handlers in the same source file so deployment stays simple.
2. The processor writes review records after S3 upload.
3. The analyzer runs Comprehend and can optionally call OpenRouter, then sends completion emails via SES.
4. The API function serves REST requests and the scheduled daily digest.

### Expected result

All three Lambda functions should exist, use the correct roles, and be ready for event source wiring on the next subpage. The analyzer function should be configured to send emails via Amazon SES when analysis completes.
