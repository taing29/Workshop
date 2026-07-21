---
title: "Processing and integrations"
date: 2024-01-01
weight: 4
chapter: false
pre: " <b> 5.4. </b> "
---

#### Overview

In this section you create the IAM roles, Lambda functions, and event triggers that connect the data layer to the analysis flow. This is where ReviewSentinal starts behaving like a live system instead of a set of isolated resources.

#### Content

1. [IAM roles](5.4.1-iam-roles/)
2. [Lambda functions](5.4.2-lambda-functions/)
3. [Event triggers](5.4.3-event-triggers/)

#### Build the processing layer

1. Create one least-privilege IAM role for each Lambda function: review processor, sentiment analyzer, and API handler.
2. Create the three Lambda functions and attach the matching role, handler, timeout, memory, and environment variables.
3. Wire the S3 bucket to the review processor with an object-created trigger.
4. Wire the DynamoDB stream on `Reviews` to the sentiment analyzer.
5. Add the optional OpenRouter secret access only to the analyzer and API handler roles.

#### Notes

+ Keep the stream permissions separate from the table permissions. The analyzer reads the DynamoDB stream, so it needs stream-level actions in addition to table access.
+ Use the DLQ for async failure handling so failed events do not disappear silently.
+ If you enable the optional deeper analysis path, store the raw key value in Secrets Manager and fetch it at runtime.
