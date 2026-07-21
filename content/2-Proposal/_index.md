---
title: "Proposal"
date: 2026-07-06
weight: 2
chapter: false
pre: " <b> 2. </b> "
---

# ReviewSentinel: AI-Powered Product Review Sentiment Analyzer
## A Serverless AWS Solution for Automated Review Analysis

### 1. Executive Summary

ReviewSentinel is a study/demo project that builds a small, fully serverless pipeline on AWS to automatically collect product reviews, analyze their sentiment with AI, and surface the results on a live dashboard. It is sized for a few hundred to a few thousand reviews rather than production traffic, using Amazon Comprehend for baseline sentiment scoring and Meta Llama 3.1 8B Instruct (via the OpenRouter API) for deeper natural-language insight, DynamoDB and S3 for storage, and a React dashboard for visualization. The goal is to demonstrate a complete, working, secure pipeline end-to-end — not to build a commercial product — while keeping monthly cost close to $0 by relying on AWS Free Tier, the low usage volume of a demo, and tearing down resources between sessions.

> **Note:** Amazon Bedrock was originally considered for the deeper-insight step, but the AWS sandbox account used for this project is a free-credit account that cannot invoke paid Bedrock models. Meta Llama 3.1 8B Instruct via OpenRouter was chosen as a drop-in replacement — same role in the pipeline (an optional, richer analysis pass on top of Comprehend), reached over HTTPS instead of an AWS SDK call. OpenRouter's Llama 3.1 8B Instruct is a paid, pay-as-you-go model ($0.02 / $0.03 per 1M input/output tokens) — there is no free tier for it — but because the model is small and usage at demo scale is light, the actual cost is a fraction of a cent, far below Bedrock's per-request pricing.

### 2. Problem Statement

**What's the Problem?**
Reading through product reviews one by one to gauge how customers feel does not scale even at small volume, and doing it manually gives no consistent, repeatable way to flag negative feedback quickly. There is no lightweight, low-cost way to automatically score sentiment and see trends without either building a heavy custom system or paying for a full commercial analytics platform.

**The Solution**
ReviewSentinel ingests review files (CSV/JSON) through S3, automatically validates and cleans them with Lambda, stores them in DynamoDB, and runs each review through Amazon Comprehend for sentiment scoring, with an optional call to Meta Llama 3.1 8B Instruct (via OpenRouter) for deeper insight on ambiguous or high-value reviews. Strongly negative reviews trigger an email alert via SNS. A React dashboard, protected by Amazon Cognito login, shows sentiment breakdowns and trends per product. Everything is provisioned with Terraform so the whole environment can be deployed and destroyed on demand.

**Benefits**
The project gives hands-on experience with a realistic serverless + AI architecture pattern (event-driven ingestion → AI enrichment → authenticated API → dashboard) that generalizes to many other use cases, including how to safely call a third-party AI API from a Lambda function. It produces a working reference implementation and a reusable Terraform base for future projects. Because it runs on AWS Free Tier and only makes light, pay-as-you-go calls to OpenRouter, there is effectively no meaningful ongoing cost at demo scale, as long as resources are torn down between uses and a spend cap is set on the OpenRouter account as a safety net.

### 3. Solution Architecture

The platform uses a serverless, event-driven AWS architecture. A review file uploaded to S3 triggers a Lambda function that validates and cleans the data before storing it in DynamoDB. Writing to DynamoDB triggers a second Lambda (via DynamoDB Streams) that calls Amazon Comprehend to score sentiment, optionally enriching results with a call to Meta Llama 3.1 8B Instruct through the OpenRouter API. Negative results publish an alert through SNS. A Cognito-authenticated API Gateway + Lambda layer serves the React dashboard, which visualizes the data.

![Architecture Diagram](/Workshop/images/2-Proposal/architecture-diagram.png)

**AWS Services Used**
- **Amazon S3**: Stores raw uploaded review files and processed reports (2 buckets), public access blocked, encrypted at rest (SSE-S3, AES256).
- **AWS Lambda**: Three functions — review-processor (validation/cleaning), sentiment-analyzer (Comprehend + OpenRouter), api-handler (REST API).
- **Amazon DynamoDB**: Three tables (Reviews, Products, Users) with GSIs for query patterns and Streams enabled for the sentiment pipeline.
- **Amazon Comprehend**: Baseline sentiment, key phrase, and entity extraction.
- **Amazon API Gateway**: REST API with a **Cognito User Pool Authorizer** attached to every method.
- **Amazon Cognito**: User authentication (JWT) for the dashboard and API.
- **Amazon SNS**: Email alerts on strongly negative reviews.
- **Amazon SQS**: Dead-letter queue for failed processing events.
- **Amazon CloudWatch**: Logs, dashboards, and alarms (Lambda errors, API latency).
- **AWS Secrets Manager**: Stores the OpenRouter API key; the sentiment-analyzer Lambda role is granted `secretsmanager:GetSecretValue` on only this one secret. Terraform creates the secret with a placeholder value — the real key is set afterward via console or CLI, and `lifecycle.ignore_changes` keeps future `terraform apply` runs from ever overwriting it or capturing it in state history.
- **Terraform**: Infrastructure as Code for the entire stack, enabling clean deploy/teardown.

**External Service Used**
- **OpenRouter API — Meta Llama 3.1 8B Instruct**: Called over HTTPS from the sentiment-analyzer Lambda for an optional, deeper natural-language pass (nuanced phrasing, sarcasm, mixed sentiment) on top of Comprehend's baseline score. This is a paid, pay-as-you-go model ($0.02 / $0.03 per 1M input/output tokens, no free tier). Used selectively, not necessarily on every review, to control latency and keep spend predictable — though at this project's volume, cost is negligible either way.

**Component Design**
- **Ingestion**: Users upload CSV/JSON review files via presigned S3 URLs issued by the API.
- **Processing**: review-processor Lambda validates schema, de-duplicates, and cleans text before writing to DynamoDB; failures land in an SQS dead-letter queue instead of being dropped.
- **AI Analysis**: sentiment-analyzer Lambda is triggered by **DynamoDB Streams** whenever a new review row is written (this is the trigger mechanism — the Lambda is subscribed to the stream as its event source). It calls Comprehend for baseline sentiment/key phrases/entities, and — for a sampled subset or low-confidence cases — calls the OpenRouter API (Meta Llama 3.1 8B Instruct) over HTTPS for a richer read on the review text. It then writes the result back onto the *same* review record via a separate `UpdateItem` call. **These are two distinct one-way calls, not a bidirectional link**: DynamoDB → Lambda (stream trigger) and Lambda → DynamoDB (write result) happen in opposite directions for different reasons. The OpenRouter API key is read from Secrets Manager at runtime, never stored in code or environment variables in plain text.
- **Alerting**: SNS publishes an email notification when sentiment is strongly negative.
- **API & Auth**: Amplify → Cognito for login (JWT issued to the browser). Every subsequent API call carries that JWT, but **the Lambda itself never validates it** — API Gateway's Cognito User Pool Authorizer checks the token first and rejects invalid/missing ones before the request ever reaches api-handler. api-handler serves products, reviews, and analytics endpoints only once the token has already been verified.
- **Dashboard**: A React + TypeScript app shows product lists, an upload interface, and sentiment charts (pie/line/bar via Recharts).

**Lambda Functions**

| Lambda | Handler | Job |
|---|---|---|
| Review Processor | `lambda_handler_review_processor` | Read file from S3 → parse (JSON/CSV) → validate + dedupe → clean text → store to DynamoDB |
| Sentiment Analyzer | `lambda_handler_sentiment_analyzer` | Comprehend sentiment score → optional OpenRouter deep insight → write result back to DynamoDB (`UpdateItem`) → SNS alert if negative |
| API | `lambda_handler_api` | `GET/POST /products`, `GET /products/{id}/reviews`, `GET /products/{id}/analytics`, `POST /upload` (issues presigned URL) |

**Request & Data Flow**

1. End User → Route 53 (DNS resolution)
2. Route 53 → CloudFront (CDN routes to origin)
3. CloudFront → Amplify (serves the React dashboard)
4. Amplify → Cognito (user logs in, gets JWT)
5. Amplify → API Gateway (API call, JWT attached)
6. API Gateway → API Lambda (Cognito authorizer validates the JWT first, then forwards)
7. API Lambda → S3 (issues a presigned URL; browser PUTs the review file directly to S3)
8. S3 → Review Processor Lambda (S3 event trigger)
9. Review Processor Lambda → DynamoDB Reviews Table (write review, after validate/clean/dedupe)
10. DynamoDB Stream → Sentiment Analyzer Lambda (trigger)
11. Sentiment Analyzer Lambda → Comprehend (baseline sentiment, always runs)
12. Sentiment Analyzer Lambda → Secrets Manager → OpenRouter API (optional deep insight, sampled/low-confidence reviews only)
13. Sentiment Analyzer Lambda → DynamoDB Reviews Table (write sentiment back, `UpdateItem` — opposite direction from step 10)
14. Sentiment Analyzer Lambda → SNS (alert if negative)

### 4. Technical Implementation

**Implementation Phases**
The project follows four phases:
- **Foundation & IaC Setup**: Set up the AWS sandbox account, initialize Terraform, and define S3 buckets, DynamoDB tables, and base IAM roles (Days 1–3).
- **Backend Processing & AI Pipeline**: Build and deploy the review-processor and sentiment-analyzer Lambda functions, wire up S3 events and DynamoDB Streams, integrate Comprehend, add the OpenRouter (Meta Llama 3.1 8B Instruct) call with the API key stored in Secrets Manager, and configure the SNS alert (Days 4–11).
- **API, Auth & Frontend**: Set up Cognito, deploy the authenticated API Gateway + api-handler Lambda, and build/deploy the React dashboard (Days 12–18).
- **Testing & Hardening**: Run integration tests against sample data, verify IAM least-privilege and encryption settings, confirm the OpenRouter key is not exposed in logs, and finalize documentation (Days 19–21).

**Technical Requirements**
- **Backend**: Python 3.9+ for Lambda functions, boto3 for AWS SDK calls, `urllib3` for the OpenRouter HTTPS call (already a boto3/botocore dependency — no extra Lambda layer needed), Terraform for infrastructure.
- **AI Services**: Amazon Comprehend (sentiment, key phrases, entities) enabled in the target region; an OpenRouter account with billing/spend-cap configured and an API key for Meta Llama 3.1 8B Instruct (pay-as-you-go, $0.02 / $0.03 per 1M input/output tokens).
- **Frontend**: Node.js 18+, React + TypeScript, Recharts for charts, deployed via Amplify or S3 + CloudFront.
- **Security**: Cognito user pool for authentication, least-privilege IAM role per Lambda function, encryption at rest (S3/DynamoDB) and in transit (TLS/HTTPS), no public S3 access, no hard-coded credentials — the OpenRouter API key lives only in Secrets Manager, fetched at runtime, cached per warm execution environment, and never logged.
- **Region**: Single region (ap-southeast-1), serverless-only — no EC2 or self-managed databases. The sentiment-analyzer Lambda needs outbound internet access to reach the OpenRouter API, which works by default outside a VPC (no NAT gateway required).

### 5. Timeline & Milestones

**Project Timeline** (~3 weeks, part-time, single contributor — compresses with more people working in parallel)
- **Week 1**: Foundation & IaC setup; backend processing pipeline (upload → validate → store) working end-to-end.
- **Week 2**: AI sentiment pipeline live (Comprehend + optional OpenRouter/Llama 3.1 8B call); SNS alerts verified; authenticated API deployed.
- **Week 3**: React dashboard built and deployed; full integration testing; security self-review (including API key handling); documentation and teardown instructions finalized.

### 6. Budget Estimation

Because this is a study/demo project rather than a production deployment, the estimate below reflects both a demo-scale reality check and a reference point at higher (50,000 reviews/month) volume to show the architecture scales without redesign. The reference-scale figures are drawn directly from an [AWS Pricing Calculator estimate](https://calculator.aws/#/estimate?id=a72fc71949ca17460585fc2e0dd16056631c87fd) built against this architecture's actual services (ap-southeast-1 / Singapore pricing).

**At demo scale (a few hundred reviews, tested over a few days)**
- Nearly every AWS service below falls within AWS Free Tier.
- Meta Llama 3.1 8B Instruct on OpenRouter is a paid, pay-as-you-go model — $0.02 per 1M input tokens and $0.03 per 1M output tokens, with no free tier. At demo volume, a few hundred short review texts amounts to well under 1M tokens total, so the actual charge is a fraction of a cent (effectively rounds to $0.00–$0.05 on an OpenRouter invoice).
- Comprehend usage costs at most a few cents to a few dollars for testing volumes.
- Running `terraform destroy` between work sessions avoids ongoing DynamoDB/CloudWatch charges.
- Set a spend cap / usage limit on the OpenRouter account as a safety net, since it is billed pay-as-you-go with no built-in free quota.
- **Estimated cost: under $2 for the full study/demo period.**

**Reference: at 50,000 reviews/month (for scale illustration only)**

Assuming each review averages ~300 input tokens (review text + prompt) and ~120 output tokens when the Llama enrichment step runs on every review (a conservative upper bound — sampling only a subset would cost even less):

- Input: 50,000 × 300 tokens = 15M tokens × $0.02/1M = **$0.30**
- Output: 50,000 × 120 tokens = 6M tokens × $0.03/1M = **$0.18**
- **OpenRouter total ≈ $0.50/month even at full volume** (priced separately — OpenRouter is not an AWS service and doesn't appear in the AWS Pricing Calculator)

| Service | Monthly Cost (USD) | Notes |
|---|---|---|
| AWS Lambda (3 functions) | $0.00 | ~110K invocations/month combined, fully covered by the 1M free requests + 400K GB-second Free Tier |
| Amazon DynamoDB (on-demand + Streams) | $0.37 | ~100K writes, ~200K reads, 1 GB storage; Streams reads via Lambda triggers are not billed |
| Amazon S3 (Standard + Data Transfer) | $0.62 | 2 GB storage, ~250K requests, 2 GB in/out transfer |
| Amazon API Gateway (REST) | ~$0.04 | ~10K requests/month |
| Amazon Comprehend (Sentiment + Key Phrases) | $30.00 | 50K reviews × 2 API calls, 250 chars avg (rounds to 3-unit/300-char minimum per call) |
| AWS Secrets Manager | $0.65 | 1 secret (OpenRouter API key), 30-day duration, ~50K GetSecretValue calls (conservative; warm-Lambda caching means actual calls are far fewer) |
| Amazon CloudWatch | $5.62 | Metrics, 3 GB logs ingested, 1 dashboard, 5 alarms |
| Amazon SNS (Standard topics) | $0.00 | ~500 publishes + email notifications/month |
| Amazon Cognito | $0.01 | 25 MAU, Lite tier — well under the 10,000 MAU free tier |
| Amazon Route 53 | $0.54 | 1 hosted zone (flat monthly fee) + negligible query volume |
| Amazon CloudFront | $0.00 | Free Plan (1 TB / 10M requests) — usage is a small fraction of the allowance |
| AWS WAF | $7.06 | 1 Web ACL, 1 custom rule, 1 AWS Managed Rule Group, ~100–200K requests inspected |
| AWS Amplify Hosting | $0.97 | React SPA build + hosting, no SSR |
| OpenRouter — Meta Llama 3.1 8B Instruct | ≈ $0.50 | Pay-as-you-go, outside AWS billing; $0.02 / $0.03 per 1M input/output tokens |
| **Total** | **≈ $46.34/month** | AWS services: $45.84/month (calculator) + OpenRouter: ≈$0.50/month. Comprehend and WAF are the two dominant line items — not DynamoDB, contrary to the original manual estimate |

### 7. Risk Assessment

**Risk Matrix**
- Unexpected OpenRouter charges if a bug or retry loop causes far more calls than intended, since there is no free tier to absorb the overage: Low impact (cost is small per-call), low-medium probability.
- OpenRouter API key leaked via logs, source control, or environment variables: High impact, low probability (mitigated by design below).
- Misconfigured IAM permissions on a Lambda role: High impact, low probability.
- Idle resources left running after the demo (API Gateway cache, CloudWatch logs): Low impact, medium probability.
- Sample/synthetic test data not representative enough to validate sentiment accuracy: Low impact, low probability.
- OpenRouter service outage or model deprecation: Medium impact, low probability.

**Mitigation Strategies**
- Use Comprehend as the default, always-on sentiment path; call the OpenRouter/Llama 3.1 8B step only on a sample or for low-confidence cases, both to keep spend predictable and to keep the pipeline functional if OpenRouter is briefly unavailable.
- Set a spend cap / usage limit on the OpenRouter account so a runaway loop cannot generate a surprise bill.
- Store the OpenRouter API key exclusively in AWS Secrets Manager, with `lifecycle.ignore_changes` on the Terraform-managed secret so the real key (set manually post-deploy) is never overwritten or captured in state; grant the sentiment-analyzer Lambda role read access to that one secret only; never print the key to logs or commit it to source control.
- Review each Lambda's IAM role against the specific actions/resources it actually needs; avoid wildcard permissions.
- Document and run `terraform destroy` after each work session; set an AWS budget alarm as a backstop.
- Use a varied, manually labeled test set spanning positive, negative, and neutral reviews.

**Contingency Plans**
- If OpenRouter is unavailable, over budget, or the model is deprecated, fall back to Comprehend-only scoring — the pipeline still functions with baseline sentiment.
- If a Terraform apply fails partway, `terraform destroy` and redeploy from a clean state rather than patching manually.
- If the OpenRouter API key is ever suspected compromised, rotate it in the OpenRouter dashboard and update the Secrets Manager value directly (console or CLI) — no code change or redeploy required.

### 8. Expected Outcomes

**Technical Improvements**
A working, end-to-end demonstration of an event-driven, AI-enriched data pipeline: upload → validate → store → analyze → alert → visualize, with authenticated APIs and encrypted data throughout, and a safely-integrated external AI API call alongside native AWS AI services.

**Learning Outcomes**
Hands-on experience with Infrastructure as Code (Terraform), serverless event-driven design (S3 events, DynamoDB Streams), combining a native AWS AI service (Comprehend) with a third-party LLM API (OpenRouter/Meta Llama 3.1 8B Instruct), and applying security fundamentals (least-privilege IAM, encrypted secrets management, authenticated APIs) without over-building for a scale the project doesn't need.

**Reusability**
The Terraform stack and Lambda code serve as a reusable starting point for future serverless + AI projects — including the pattern of calling an external LLM API securely from Lambda — and the sample data and test scripts make the pipeline easy to re-demo or extend later.