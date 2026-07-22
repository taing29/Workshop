---
title: "5.3.3 Messaging and secrets"
weight: 3
---

# Messaging and secrets for ReviewSentinal

## Overview

Create the dead-letter queue, configure Amazon SES for user notifications, and set up the secret that the Lambdas will use later.

### SQS dead-letter queue

1. Open SQS and choose **Create queue**.
2. Select **Standard**.
3. Name the queue `lambda-dlq`.

![Guide](/Workshop/images/5-Workshop/sqs-1.PNG)

4. Confirm **SSE-SQS** encryption is on.
5. Set message retention to 14 days.
6. Create the queue.

![Guide](/Workshop/images/5-Workshop/sqs-2.PNG)

7. Copy the queue ARN from the details page.



### Amazon SES for user notifications

1. Go to **Amazon SES → Verified identities → Create identity**
2. Identity type: **Email address**
3. Email: `noreply@yourdomain.com` (or your Gmail if you're in the SES sandbox)
4. Verify the email address
5. *(Sandbox only)* Also verify your own receiving email address

![Guide](/Workshop/images/5-Workshop/messaging-1.PNG)

### Secrets Manager secret

1. Open Secrets Manager and choose **Store a new secret**.
2. Pick **Other type of secret**.
3. Use the **Plaintext** tab, not key/value pairs.
4. Enter a placeholder value such as `REPLACE_ME_LATER`.
5. Leave encryption on the default AWS-managed key.

![Guide](/Workshop/images/5-Workshop/messaging-2.PNG)

6. Name the secret `review-sentiment-analyzer-openrouter-api-key`.
7. Skip rotation and store it.
8. Copy the secret ARN.

![Guide](/Workshop/images/5-Workshop/messaging-3.PNG)

### Expected result

You should have:
- An SQS DLQ ARN
- A verified SES sender email address
- A Secrets Manager secret ARN

These ARNs and configuration details will be used in IAM policies and Lambda environment variables in subsequent sections.