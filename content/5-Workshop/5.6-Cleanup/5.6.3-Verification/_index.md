---
title: "5.6.3 Verification"
weight: 3
---

# Verification

## Overview

Use this page to confirm the account is clean and no ReviewSentinal resources remain.

### Checks to run

- CloudFormation stack list for remaining ReviewSentinal stacks
- S3 bucket list for leftover upload buckets
- Lambda function list for remaining functions
- DynamoDB table list for leftover tables
- API Gateway and Cognito list checks if needed

## Step-by-step

1. Check CloudFormation for any remaining ReviewSentinal stacks.
2. Check S3 for leftover buckets.
3. Check Lambda for any remaining functions.
4. Check DynamoDB for leftover tables.
5. Check API Gateway and Cognito if you want to be thorough.
6. Confirm the billing view no longer shows active ReviewSentinal resources.

## Notes

1. Do the verification after the destructive cleanup steps finish.
2. If something remains, delete it before closing the workshop.

## Expected result

The account should be free of ReviewSentinal resources and ready for a new deployment.
