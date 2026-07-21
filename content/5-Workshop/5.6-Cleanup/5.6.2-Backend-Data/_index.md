---
title: "5.6.2 Backend and data cleanup"
weight: 2
---
# Backend and data cleanup

## Overview

Remove the API, compute, storage, messaging, and secret resources that power the application.

### What to delete

- API Gateway stage and REST API
- Lambda functions and IAM roles
- S3 upload bucket
- DynamoDB tables
- SQS queue (SNS topic replaced with SES for notifications)
- Secrets Manager secret
- CloudWatch dashboard and alarms

## Step-by-step

1. Delete the API Gateway API and its stage.
2. Delete the three Lambda functions.
3. Remove the CloudWatch log groups for those functions.
4. Delete the IAM roles used by the Lambdas.
5. Delete the SQS queue (SNS topic is not needed as notifications use Amazon SES).
6. Delete the Secrets Manager secret.
7. Delete the DynamoDB tables.
8. Empty and delete the S3 upload bucket.
9. Delete the CloudWatch dashboard and alarms.

## Notes

1. Delete the Lambda functions before deleting the roles that they use.
2. Empty the S3 bucket before deleting it.
3. Keep the order simple so dependent resources disappear cleanly.

## Expected result

The core application services should no longer exist after this step. Note that SES verified identities are not deleted here as they may be used for other purposes.