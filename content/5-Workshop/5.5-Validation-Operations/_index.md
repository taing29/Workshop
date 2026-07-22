---
title: "Validation and operations"
date: 2024-01-01
weight: 5
chapter: false
pre: " <b> 5.5. </b> "
---

#### Overview

This section covers the user-facing integration layer: API Gateway, Cognito, CORS, dashboard alarms, and the checks you should run before calling the deployment complete.

#### Content

1. [Auth and API](5.5.1-auth-api/)
2. [Monitoring](5.5.2-monitoring/)
3. [Frontend checks](5.5.3-frontend-checks/)
4. [Ready to launch](5.5.4-ready-to-launch/)

#### Configure access

1. Create the Cognito user pool and app client for the frontend sign-in flow.
2. Create the REST API methods for products, reviews, uploads, and analysis.
3. Enable CORS on the API resources and deploy a `dev` stage.
4. Add CloudWatch dashboard widgets and alarms for Lambda, DynamoDB, and API latency.
5. Build and test the frontend with the deployed API URL and Cognito settings.

#### Validation checklist

+ Upload a sample review file and confirm the processor writes to DynamoDB.
+ Confirm the sentiment analyzer updates the review and can publish alerts.
+ Sign in through Cognito and exercise the API routes from the browser.
+ Verify the dashboard and alarms show healthy values before you move on.
