---
title: "Workshop overview"
date: 2024-01-01
weight: 1
chapter: false
pre: " <b> 5.1. </b> "
---

#### ReviewSentinal at a glance

ReviewSentinal is a serverless AWS application that ingests product reviews, stores them in DynamoDB, scores them with Amazon Comprehend, and exposes the results through API Gateway and Cognito-protected endpoints.

#### What gets deployed

+ **Storage and events**: S3 for raw uploads, DynamoDB for review and product records, SQS for failures, and SES for alerts.
+ **Processing**: three Lambda functions for review ingestion, sentiment analysis, and API access.
+ **Access layer**: API Gateway, Cognito, and the frontend-facing upload and query flow.
+ **Optional insight**: Secrets Manager stores the OpenRouter API key for the deeper analysis pass if you choose to enable it.

#### Deployment target

Use a single AWS region throughout the workshop. The guide is written for `ap-southeast-1` and assumes the same region for every resource unless a step explicitly says otherwise.
