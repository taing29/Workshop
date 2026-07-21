---
title: "Week 12 Worklog"
date: 2026-07-20
weight: 12
chapter: false
pre: " <b> 1.12. </b> "
---

### Week 12 Objectives:

* Complete the deployment of the entire ReviewSentinel system on AWS.
* Integrate all backend, frontend, and infrastructure components into a fully functional application.
* Validate the end-to-end processing workflow and finalize the project deployment.

### Tasks Completed This Week:

| Task | Start Date | Completion Date | Reference Material |
| --- | ------------ | --------------- | ------------------ |
| Deploy AWS Lambda <br> - Deploy the **review_processor**, **sentiment_analyzer**, and **api_handler** Lambda functions <br> - Configure IAM Roles following the Principle of Least Privilege <br> - Set up Environment Variables and verify Lambda execution | 20/07/2026 | 20/07/2026 | AWS Study Group |
| Configure Amazon API Gateway <br> - Integrate Amazon Cognito Authorizer <br> - Configure CORS <br> - Deploy REST APIs and grant Lambda Invoke permissions | 20/07/2026 | 20/07/2026 | AWS Study Group |
| Configure the Event-driven Architecture <br> - Configure Amazon S3 Event Notifications to trigger Lambda <br> - Configure Amazon DynamoDB Streams triggers <br> - Verify the automated data processing workflow | 21/07/2026 | 21/07/2026 | AWS Study Group |
| Deploy the Frontend and perform system testing <br> - Deploy the React application to AWS Amplify <br> - Configure integration with Amazon API Gateway and Amazon Cognito <br> - Perform end-to-end testing and monitor the system using Amazon CloudWatch | 21/07/2026 | 21/07/2026 | AWS Study Group |

### Week 12 Achievements:

* Successfully deployed the core **AWS Lambda Functions**—**review_processor**, **sentiment_analyzer**, and **api_handler**—and configured IAM Roles and Environment Variables to ensure secure and reliable execution.

* Completed the configuration of **Amazon API Gateway** integrated with **Amazon Cognito** for user authentication, configured CORS policies, and deployed REST APIs to support both the frontend application and backend services.

* Successfully implemented an **event-driven architecture** by integrating **Amazon S3**, **AWS Lambda**, and **Amazon DynamoDB Streams**, enabling automatic processing of uploaded review files without manual intervention.

* Deployed the **React** frontend application to **AWS Amplify**, integrated it with Amazon Cognito and Amazon API Gateway, and completed the required callback URLs, CORS settings, and environment variable configuration for seamless communication between the frontend and backend.

* Performed comprehensive **end-to-end testing**, including user registration, authentication, file uploads, review processing, sentiment analysis, and storing results in Amazon DynamoDB. Additionally, used **Amazon CloudWatch** to monitor logs, metrics, and the operational health of the entire system.

* Successfully completed the **ReviewSentinel** project by building a fully functional **serverless application** on AWS, integrating Amazon S3, AWS Lambda, Amazon DynamoDB, Amazon API Gateway, Amazon Cognito, Amazon CloudWatch, and AWS Amplify into a complete end-to-end product review processing and sentiment analysis workflow.