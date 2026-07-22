---
title: "Prerequisites"
date: 2024-01-01
weight: 2
chapter: false
pre: " <b> 5.2. </b> "
---

#### What you need first

+ An AWS account with permission to create S3, DynamoDB, Lambda, IAM, Cognito, API Gateway, CloudWatch, SES, SQS, and Secrets Manager resources.
+ A consistent region for the whole build. This guide uses `ap-southeast-1`.
+ The ReviewSentinal source repository and the account ID for your AWS account.
+ A local machine with a browser, plus Node.js if you plan to build the frontend locally.

**Must have file for the workshop**

📥[Download lambda functions (PY)](01_lambda_functions.py)

📥[Download react frontend (TSX)](03_react_dashboard.tsx)

📥[Download review sample 1 (20 products) (json)](test_reviews_1.json)

📥[Download review sample 2 (100 products) (csv)](reviews_sample_1.csv)

📥[Download review sample 3 (100 products) (csv)](reviews_sample_2.csv)

#### Before you start

1. Sign in to the AWS Console and confirm the region is set to `ap-southeast-1`.
2. Record the account ID from the user menu in the top-right corner.
3. Make sure you can open the S3, DynamoDB, Lambda, Cognito, API Gateway, and CloudWatch consoles without permission errors.
4. Refer to the workshop sections for resource names and ARNs as needed.

#### Expected output

By the end of this section you should have access to the console, the region selected, and the basic information needed to name resources consistently in the next steps.
