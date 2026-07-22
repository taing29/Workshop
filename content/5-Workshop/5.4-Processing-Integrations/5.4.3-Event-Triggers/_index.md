---
title: "5.4.3 Event triggers"
weight: 3
---

# Event triggers for ReviewSentinal

## Overview

Wire the storage and database events into the Lambda functions so the pipeline runs automatically. This step connects the infrastructure created earlier to the business logic created in the previous subpage.

### Triggers to configure

- S3 object-created event for the processor Lambda
- DynamoDB Streams trigger for the analyzer Lambda

## Step-by-step

### 1. Wire the S3 trigger

1. Open the `review-sentiment-analyzer-processor` Lambda.
2. Choose **Add trigger**.
3. Select **S3**.
4. Choose the raw upload bucket.
5. Set the event type to **All object create events**.
6. Add the prefix `uploads/`.
7. Confirm the recursive invocation warning and add the trigger.

![Guide](/Workshop/images/5-Workshop/event-1.PNG)

### 2. Wire the DynamoDB stream trigger

1. Open the `review-sentiment-analyzer-analyzer` Lambda.
2. Choose **Add trigger**.
3. Select **DynamoDB**.
4. Choose the `Reviews` table.
5. Keep the batch size at `100` and the starting position at **Latest**.

![Guide](/Workshop/images/5-Workshop/event-2.PNG)

6. Add the filter criteria so the Lambda only fires on `INSERT` events where `ProcessingStatus` is `PENDING`.
```json
[
  {
    "Pattern": "{  \"eventName\": [\"INSERT\"],  \"dynamodb\": {    \"NewImage\": {      \"ProcessingStatus\": {        \"S\": [\"PENDING\"]      }    }  }}"
  }
]
```

![Guide](/Workshop/images/5-Workshop/event-3.PNG)

7. Enable split batch on error.
8. Add the trigger.



### Notes

1. The S3 trigger starts the ingestion path.
2. The DynamoDB stream trigger must filter out updates from the analyzer itself. The analyzer function now:
   - Processes incoming review records
   - Updates each review with sentiment analysis results
   - Updates the corresponding analysis record counters (ProcessedReviews, Positive/Neutral/Negative)
   - When all reviews for an analysis are processed, it:
     * Updates the analysis status to COMPLETED
     * Sets the CompletedAt timestamp
     * Sends a completion email via Amazon SES to the user's email address

### Expected result

The ingestion path starts from S3 and continues through DynamoDB Streams. The analyzer function will now also update analysis records and send completion emails via SES when an analysis finishes processing.