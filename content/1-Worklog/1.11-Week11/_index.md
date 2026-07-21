---
title: "Week 11 Worklog"
date: 2026-07-13
weight: 11
chapter: false
pre: " <b> 1.11. </b> "
---

### Week 11 Objectives:

* Finalize the overall architecture of the ReviewSentinel system on AWS.
* Design the system's security model, data model, and processing components.
* Prepare the cloud infrastructure and development environment for the implementation phase.

### Tasks Completed This Week:

| Task | Start Date | Completion Date | Reference Material |
| --- | ------------ | --------------- | ------------------ |
| Finalize the ReviewSentinel system architecture <br> - Review the overall architecture <br> - Identify the required AWS services <br> - Complete the end-to-end data processing workflow | 13/07/2026 | 13/07/2026 | AWS Study Group |
| Design the security model <br> - Configure Amazon Cognito User Pool <br> - Design JWT authentication with Amazon API Gateway <br> - Define IAM Roles following the Principle of Least Privilege | 14/07/2026 | 14/07/2026 | AWS Study Group |
| Design the data model <br> - Design DynamoDB tables (Reviews, Products, Users) <br> - Define Primary Keys, Global Secondary Indexes (GSIs), and access patterns <br> - Plan Amazon S3 storage and Event Notifications | 15/07/2026 | 15/07/2026 | AWS Study Group |
| Design Lambda Functions and prepare the infrastructure <br> - Define specifications for **review_processor**, **sentiment_analyzer**, and **api_handler** <br> - Specify Input/Output formats and Error Handling <br> - Prepare Amazon S3 Buckets, DynamoDB tables, and the development environment | 16/07/2026 | 16/07/2026 | AWS Study Group |

### Week 11 Achievements:

* Completed the overall architecture design of the **ReviewSentinel** system, incorporating Amazon API Gateway, Amazon Cognito, AWS Lambda, Amazon DynamoDB, Amazon S3, Amazon Comprehend, Amazon Bedrock, and Amazon CloudWatch, while clearly defining the data flow between AWS services.

* Designed the system's security model using **Amazon Cognito** with JWT-based authentication and IAM Roles following the **Principle of Least Privilege**, while identifying key security requirements such as data encryption, access control, and log management.

* Completed the database design on **Amazon DynamoDB**, including the **Reviews**, **Products**, and **Users** tables, with appropriate Primary Keys, Global Secondary Indexes (GSIs), and access patterns to support review processing and sentiment analysis.

* Prepared detailed specifications for the core Lambda functions—**review_processor**, **sentiment_analyzer**, and **api_handler**—including trigger mechanisms, input/output formats, error-handling strategies, and the required infrastructure components such as Amazon S3 Buckets and DynamoDB tables, ensuring the project was ready for the implementation phase.