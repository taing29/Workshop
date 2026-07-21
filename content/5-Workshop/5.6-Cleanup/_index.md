---
title: "Cleanup"
date: 2024-01-01
weight: 6
chapter: false
pre: " <b> 5.6. </b> "
---

Congratulations on completing the workshop.

#### Content

1. [Frontend cleanup](5.6.1-frontend/)
2. [Backend and data cleanup](5.6.2-backend-data/)
3. [Verification](5.6.3-verification/)

#### Cleanup

1. Delete the Amplify or static frontend deployment if you created one for the workshop.
2. Remove the API Gateway stage and the REST API if you no longer need the endpoint.
3. Delete the Lambda functions and their IAM roles.
4. Empty and delete the S3 upload bucket.
5. Delete the DynamoDB tables, SQS queue, and Secrets Manager secret.
6. Confirm CloudWatch dashboards and alarms are removed if you do not want them to keep generating noise or cost.

#### Final check

After cleanup, the account should no longer have any ReviewSentinal resources left behind. Note that verified email addresses in Amazon SES are not deleted in this cleanup as they may be used for other purposes.
