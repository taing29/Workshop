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

![Guide](/Workshop/images/5-Workshop/monitor-1.PNG)

4. Add a Metrics -> Metrics console -> Line widget for the three Lambda functions.
5. Include `Invocations`, `Errors`, and `Duration` metrics.

![Guide](/Workshop/images/5-Workshop/monitor-2.PNG)

![Guide](/Workshop/images/5-Workshop/monitor-3.PNG)

![Guide](/Workshop/images/5-Workshop/monitor-4.PNG)

6. Add a second widget for DynamoDB (Metrics -> Metrics console ->) Data table metrics.
7. Include `ConsumedWriteCapacityUnits` for `Reviews`.

![Guide](/Workshop/images/5-Workshop/monitor-5.PNG)

8. Add a (Logs ->) Line query widget that counts error messages over time.
```
SOURCE logGroups(namePrefix: [], class: "STANDARD") START=-604800s END=0s |
filter @message like /(?i)error/ 
| stats count(*) as errorCount by bin(5m)
```
9. Save the dashboard.

![Guide](/Workshop/images/5-Workshop/monitor-6.PNG)

### 2. Create the per-function error alarms

1. Open **CloudWatch** → **Alarms** → **All alarms**.
2. Create an alarm for the processor Lambda errors.
3. Scope each alarm to the specific function name.
4. Use a 5-minute period and a threshold of more than 5 errors.

![Guide](/Workshop/images/5-Workshop/monitor-7.PNG)

![Guide](/Workshop/images/5-Workshop/monitor-8.PNG)

5. Send notifications to your verified SNS email address. (Create new topic and use that topic for other alarms)

![Guide](/Workshop/images/5-Workshop/monitor-9.PNG)

6. Repeat for the analyzer Lambda.
7. Repeat for the API Lambda.

![Guide](/Workshop/images/5-Workshop/monitor-10.PNG)

### 3. Create the API latency alarm

1. Create a Lambda alarm for `review-sentiment-analyzer-api`.
2. Choose the `Duration` metric.
3. Use an average period of 5 minutes.
4. Trigger the alarm if duration is greater than 5000 ms.
5. Send notifications to your verified SNS email address.

![Guide](/Workshop/images/5-Workshop/monitor-11.PNG)

### 4. Create budget alerts

1. Open **Billing and Cost Management** → **Budgets**.
2. Create a monthly cost budget.
3. Create a daily cost budget.
4. Add threshold alerts at 80% of actual spend and 100% of forecasted spend.
5. Use your email address as the subscriber.

![Guide](/Workshop/images/5-Workshop/monitor-13.PNG)

### Notes

1. Scope the Lambda alarms to a specific function, not the generic service metric.
2. **Use direct SES email notifications instead of SNS topic for alarm notifications**.
3. Keep the widgets simple so the dashboard remains readable during validation.

### Expected result

You should be able to open the dashboard and confirm that the stack is healthy before running the final checks. Alarm notifications will now come directly from SES instead of through SNS.
