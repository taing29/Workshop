---
title: "5.4.1 IAM roles"
weight: 1
---

# IAM roles for the processing layer

## Overview

Create one least-privilege IAM role for each Lambda function used by ReviewSentinal. Do not reuse a shared role: the processor, analyzer, and API handler each touch a different set of resources.

### Roles to create

- `review-processor-role`
- `sentiment-analyzer-role`
- `api-handler-role`

### Common requirements

- Trust policy: `lambda.amazonaws.com`
- CloudWatch Logs permissions for all three roles
- SQS send permissions for the DLQ
- Scoped S3, DynamoDB, and Secrets Manager access based on the Lambda function
- **SES send email permission for the sentiment analyzer role**

## Step-by-step

### 1. Create the processor role

1. Open the IAM console and go to **Roles**.
2. Choose **Create role**.
3. Select **AWS service** as the trusted entity.
4. Choose **Lambda** as the use case.
5. Continue without attaching any AWS managed policy.
6. Name the role `review-processor-role` and create it.
7. Open the role and create an inline policy in the **JSON** editor.
8. Paste the following policy and replace `<ACCOUNT_ID>` with your real account ID:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "S3ReadAccess",
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:ListBucket"],
      "Resource": [
        "arn:aws:s3:::raw-reviews-<ACCOUNT_ID>-ap-southeast-1",
        "arn:aws:s3:::raw-reviews-<ACCOUNT_ID>-ap-southeast-1/*"
      ]
    },
    {
      "Sid": "DynamoDBWrite",
      "Effect": "Allow",
      "Action": ["dynamodb:PutItem", "dynamodb:UpdateItem", "dynamodb:GetItem", "dynamodb:Query"],
      "Resource": "arn:aws:dynamodb:ap-southeast-1:<ACCOUNT_ID>:table/Reviews"
    },
    {
      "Sid": "DynamoDBProductsAutoRegister",
      "Effect": "Allow",
      "Action": ["dynamodb:PutItem"],
      "Resource": "arn:aws:dynamodb:ap-southeast-1:<ACCOUNT_ID>:table/Products"
    },
    {
      "Sid": "DLQAccess",
      "Effect": "Allow",
      "Action": ["sqs:SendMessage"],
      "Resource": "arn:aws:sqs:ap-southeast-1:<ACCOUNT_ID>:lambda-dlq"
    },
    {
      "Sid": "CloudWatchLogs",
      "Effect": "Allow",
      "Action": ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
      "Resource": "arn:aws:logs:ap-southeast-1:<ACCOUNT_ID>:*"
    }
  ]
```
9. Save the policy as `review-processor-policy`.

### 2. Create the sentiment analyzer role

1. Repeat the same create-role flow.
2. Name the role `sentiment-analyzer-role`.
3. Create a second inline policy named `sentiment-analyzer-policy`.
4. Paste the following policy and replace `<ACCOUNT_ID>` and the Secrets Manager ARN with your real values:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ComprehendAccess",
      "Effect": "Allow",
      "Action": [
        "comprehend:DetectSentiment",
        "comprehend:DetectKeyPhrases",
        "comprehend:DetectEntities",
        "comprehend:DetectDominantLanguage"
      ],
      "Resource": "*"
    },
    {
      "Sid": "SecretsManagerAccess",
      "Effect": "Allow",
      "Action": ["secretsmanager:GetSecretValue"],
      "Resource": "arn:aws:secretsmanager:ap-southeast-1:<ACCOUNT_ID>:secret:review-sentiment-analyzer-openrouter-api-key-XXXXXX"
    },
    {
      "Sid": "DynamoDBAccess",
      "Effect": "Allow",
      "Action": ["dynamodb:GetItem", "dynamodb:UpdateItem", "dynamodb:Query"],
      "Resource": [
        "arn:aws:dynamodb:ap-southeast-1:<ACCOUNT_ID>:table/Reviews",
        "arn:aws:dynamodb:ap-southeast-1:<ACCOUNT_ID>:table/Products",
        "arn:aws:dynamodb:ap-southeast-1:<ACCOUNT_ID>:table/Reviews/index/*"
      ]
    },
    {
      "Sid": "DynamoDBStreamsAccess",
      "Effect": "Allow",
      "Action": ["dynamodb:DescribeStream", "dynamodb:GetRecords", "dynamodb:GetShardIterator", "dynamodb:ListStreams"],
      "Resource": "arn:aws:dynamodb:ap-southeast-1:<ACCOUNT_ID>:table/Reviews/stream/*"
    },
    {
      "Sid": "SNSPublish",
      "Effect": "Allow",
      "Action": ["sns:Publish"],
      "Resource": "arn:aws:sns:ap-southeast-1:<ACCOUNT_ID>:sentiment-alerts"
    },
    {
      "Sid": "DLQAccess",
      "Effect": "Allow",
      "Action": ["sqs:SendMessage"],
      "Effect": "Allow",
      "Action": ["sqs:SendMessage"],
      "Resource": "arn:aws:sqs:ap-southeast-1:<ACCOUNT_ID>:lambda-dlq"
    },
    {
      "Sid": "CloudWatchLogs",
      "Effect": "Allow",
      "Action": ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
      "Resource": "arn:aws:logs:ap-southeast-1:<ACCOUNT_ID>:*"
    }
  ]
}
```
5. Save the policy as `sentiment-analyzer-policy`.
6. Verify the `<ACCOUNT_ID>` and Secrets Manager ARN are correctly replaced in the policy.
7. Confirm the separate `DynamoDBStreamsAccess` statement is present.
8. **Add SES permissions**: Allow `ses:SendEmail` and `ses:SendRawEmail` for the verified sender email address (or use a resource wildcard if verifying multiple addresses).

### 3. Create the API handler role

1. Create a third IAM role for Lambda.
2. Name it `api-handler-role`.
3. Attach the `api-handler-policy` inline policy.
4. Paste the following policy and replace `<ACCOUNT_ID>` and the secret ARN with your real values:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DynamoDBAccess",
      "Effect": "Allow",
      "Action": ["dynamodb:GetItem", "dynamodb:Query", "dynamodb:Scan", "dynamodb:PutItem", "dynamodb:UpdateItem", "dynamodb:DeleteItem", "dynamodb:BatchWriteItem"],
      "Resource": [
        "arn:aws:dynamodb:ap-southeast-1:<ACCOUNT_ID>:table/Reviews",
        "arn:aws:dynamodb:ap-southeast-1:<ACCOUNT_ID>:table/Products",
        "arn:aws:dynamodb:ap-southeast-1:<ACCOUNT_ID>:table/Users",
        "arn:aws:dynamodb:ap-southeast-1:<ACCOUNT_ID>:table/Reviews/index/*",
        "arn:aws:dynamodb:ap-southeast-1:<ACCOUNT_ID>:table/Products/index/*"
      ]
    },
    {
      "Sid": "S3PresignedURL",
      "Effect": "Allow",
      "Action": ["s3:PutObject", "s3:GetObject"],
      "Resource": "arn:aws:s3:::raw-reviews-<ACCOUNT_ID>-ap-southeast-1/*"
    },
    {
      "Sid": "ComprehendAccess",
      "Effect": "Allow",
      "Action": ["comprehend:DetectSentiment", "comprehend:DetectKeyPhrases", "comprehend:DetectEntities", "comprehend:DetectDominantLanguage"],
      "Resource": "*"
    },
    {
      "Sid": "SecretsManagerAccess",
      "Effect": "Allow",
      "Action": ["secretsmanager:GetSecretValue"],
      "Resource": "arn:aws:secretsmanager:ap-southeast-1:<ACCOUNT_ID>:secret:review-sentiment-analyzer-openrouter-api-key-XXXXXX"
    },
    {
      "Sid": "DLQAccess",
      "Effect": "Allow",
      "Action": ["sqs:SendMessage"],
      "Resource": "arn:aws:sqs:ap-southeast-1:<ACCOUNT_ID>:lambda-dlq
    },
    {
      "Sid": "CloudWatchLogs",
      "Effect": "Allow",
      "Action": ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
      "Resource": "arn:aws:logs:ap-southeast-1:<ACCOUNT_ID>:*"
    }
  ]
}
```
5. Save the policy as `api-handler-policy`.
6. Replace `<ACCOUNT_ID>` and the secret ARN with your real values in the policy.

### Notes

1. The processor role needs S3 read access and DynamoDB write access.
2. The analyzer role needs stream access in addition to table access, and SES permissions to send completion emails.
3. The API handler role needs the broadest table permissions because it serves the REST API and scheduled digest path.
4. Keep CloudWatch Logs permissions in every role so each function can write logs on first invocation.
5. **No SNS permissions are required anymore** as the analyzer function uses Amazon SES for user notifications.

### Expected result

You should end this step with three IAM roles that are ready to attach to the Lambda functions in the next subpage. The sentiment-analyzer-role will have permissions to send emails via Amazon SES.
