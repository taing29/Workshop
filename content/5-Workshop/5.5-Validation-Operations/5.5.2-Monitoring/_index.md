---
title: "5.5.2 Monitoring"
weight: 2
---

# Monitoring and alarms

## Overview

Add the observability layer that keeps the deployment honest. This page groups the CloudWatch dashboard and the alarms that watch the core Lambda and API behavior.

### What to create

- CloudWatch dashboard
- Lambda error alarms
- API latency alarm
- DynamoDB activity widgets

### Useful signals

- Lambda `Errors`
- Lambda `Duration`
- DynamoDB consumed capacity
- API latency

## Step-by-step

### 1. Create the dashboard

1. Open **CloudWatch** → **Dashboards**.
2. Choose **Create dashboard**.
3. Name it `ReviewAnalyzerDashboard`.
4. Add a line widget for the three Lambda functions.
5. Include `Invocations`, `Errors`, and `Duration` metrics.
6. Add a second widget for DynamoDB table metrics.
7. Include `ConsumedWriteCapacityUnits` for `Reviews`.
8. Add a log query widget that counts error messages over time.
9. Save the dashboard.

### 2. Create the per-function error alarms

1. Open **CloudWatch** → **Alarms** → **All alarms**.
2. Create an alarm for the processor Lambda errors.
3. Repeat for the analyzer Lambda.
4. Repeat for the API Lambda.
5. Scope each alarm to the specific function name.
6. Use a 5-minute period and a threshold of more than 5 errors.
7. **Send notifications to your verified SES email address** (replace SNS topic with direct SES email).

### 3. Create the API latency alarm

1. Create a Lambda alarm for `review-sentiment-analyzer-api`.
2. Choose the `Duration` metric.
3. Use an average period of 5 minutes.
4. Trigger the alarm if duration is greater than 5000 ms.
5. **Send the notification to your verified SES email address** (replace SNS topic with direct SES email).

### 4. Create budget alerts

1. Open **Billing and Cost Management** → **Budgets**.
2. Create a monthly cost budget.
3. Create a daily cost budget.
4. Add threshold alerts at 80% of actual spend and 100% of forecasted spend.
5. Use your email address as the subscriber.

### Notes

1. Scope the Lambda alarms to a specific function, not the generic service metric.
2. **Use direct SES email notifications instead of SNS topic for alarm notifications**.
3. Keep the widgets simple so the dashboard remains readable during validation.

### Expected result

You should be able to open the dashboard and confirm that the stack is healthy before running the final checks. Alarm notifications will now come directly from SES instead of through SNS.
