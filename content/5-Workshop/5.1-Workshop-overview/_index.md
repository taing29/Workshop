---
title: "Workshop overview"
date: 2024-01-01
weight: 1
chapter: false
pre: " <b> 5.1. </b> "
---

# ReviewSentinal Workshop Overview

ReviewSentinal is a serverless AWS application designed to ingest and analyze product reviews using AWS native services. The application ingests product reviews, stores them in DynamoDB, performs sentiment analysis using Amazon Comprehend, and optionally enhances insights with OpenRouter/LLM analysis. Results are exposed through secure API endpoints and can be visualized via a React dashboard.

## Key Components

**Storage & Events**
- **S3 Buckets**: Raw review uploads storage with CORS configuration for direct browser uploads
- **DynamoDB**: Single-table design pattern with three logical tables (Reviews, Products, Users) using username-based partition keys and multiple GSI indexes
- **SQS**: Dead letter queue (`lambda-dlq`) for asynchronous failure handling
- **Secrets Manager**: Optional storage for OpenRouter API key for enhanced LLM analysis

**Processing Layer**
- **Three Lambda Functions** (all Python 3.11, x86_64, sharing same deployment package):
  1. **Review Processor** (`review-sentiment-analyzer-processor`): Handles S3 uploads, writes initial review records to DynamoDB
  2. **Sentiment Analyzer** (`review-sentiment-analyzer-analyzer`): Processes DynamoDB streams, runs Comprehend sentiment analysis, optional OpenRouter enhancement, sends SES notifications
  3. **API Handler** (`review-sentiment-analyzer-api`): Serves REST API requests and scheduled daily digest emails

**Access & Security Layer**
- **API Gateway**: REST API with `dev` stage, CORS-enabled resources for products, reviews, uploads, and analysis endpoints
- **Cognito**: User pool and app client for authentication, with Lambda triggers for custom flows if needed
- **WAF**: Regional AWS WAF for API Gateway protection (mentioned in monitoring notes)
- **Encryption**: KMS encryption for data at rest where applicable

**Monitoring & Observability**
- **CloudWatch Dashboard**: `ReviewAnalyzerDashboard` with metrics for Lambda invocations, errors, duration, and DynamoDB consumption
- **CloudWatch Alarms**: Per-function error alarms (>5 errors/5min) and API latency alarm (>5000ms duration)
- **Logs Insights**: Error tracking queries
- **Budget Alerts**: Monthly and daily cost budgets with 80%/100% threshold notifications
- **SES Direct Notifications**: Alarm notifications sent directly via SES (bypassing SNS)

## Architecture Diagram

![ReviewSentinal Architecture](/Workshop/images/2-Proposal/architecture-diagram.png)

## Workshop Flow

This workshop follows a complete serverless application deployment workflow:

1. **Workshop Overview** - Understand ReviewSentinal's architecture and components
2. **Prerequisites & Setup** - Configure AWS account, install tools (AWS CLI, Node.js), record account ID and region (`ap-southeast-1`)
3. **Core Infrastructure** - Create foundational resources:
   - S3 bucket for raw review uploads (with CORS)
   - DynamoDB tables (Reviews, Products, Users) with streams and PITR enabled
   - SES configuration for email notifications
   - SQS dead letter queue
   - Secrets Manager placeholder for OpenRouter API key (optional)
4. **Processing & Integrations** - Build the processing logic:
   - Create least-privilege IAM roles for each Lambda function
   - Deploy the three Lambda functions from shared `01_lambda_functions.py` package
   - Configure S3→Processor trigger (ObjectCreated)
   - Configure DynamoDB Stream→Analyzer trigger
   - Configure DLQ for all Lambda functions
   - Configure optional OpenRouter secret access for analyzer and API functions
5. **Validation & Operations** - Configure user-facing components and monitoring:
   - Create Cognito user pool and app client
   - Configure API Gateway resources and methods (products, reviews, uploads, analysis)
   - Enable CORS and deploy `dev` stage
   - Deploy CloudWatch dashboard with Lambda and DynamoDB widgets
   - Configure Lambda error alarms and API latency alarm (direct SES notifications)
   - Set up cost budget alerts
6. **Frontend Validation** - Build and test the React dashboard:
   - Configure with deployed API URL and Cognito settings
   - Test review upload → analysis → visualization flow
7. **Cleanup** - Optional section for tearing down resources to avoid ongoing costs

## What You'll Learn

**Infrastructure as Code Patterns**
- AWS resource naming conventions for predictable ARN references
- Least-privilege IAM role design for Lambda functions
- DynamoDB single-table design with GSI strategies
- S3 bucket configuration for secure direct browser uploads

**Serverless Application Patterns**
- Synchronous/Async Processing
  - S3-triggered synchronous processing (review intake)
  - DynamoDB Stream-triggered asynchronous processing (sentiment analysis)
  - API Gateway-triggered synchronous processing (user queries)
- Dead Letter Queue implementation for failure handling
- Optional enhancement patterns (Comprehend → OpenRouter fallback)

**AWS Service Integration**
- Amazon Comprehend for natural language processing sentiment analysis
- Amazon SES for transactional email notifications (processing completion summaries)
- Amazon Cognito for user authentication and authorization
- API Gateway for secure, versioned REST APIs
- CloudWatch for observability (metrics, logs, alarms, dashboards)

**Operational Excellence**
- Structured logging and error tracking with CloudWatch Logs Insights
- Proper alarm scoping (function-specific vs service-wide metrics)
- Direct SES notifications for operational alerts (avoiding SNS overhead)
- Cost monitoring and budget alerts for predictable serverless spending
- Dashboard design for operational visibility

**Full-Stack Serverless Development**
- Backend: Lambda functions with shared deployment package
- Infrastructure: Consumable AWS resources with clear boundaries
- Frontend: React dashboard consuming secure APIs
- Validation: End-to-end testing from upload to visualization

This workshop demonstrates how to build a production-ready, cost-aware serverless application that processes user-generated content with AI-enhanced insights while maintaining security, observability, and operational best practices.