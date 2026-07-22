---
title: "5.4.1 IAM role"
weight: 1
---

# IAM role cho lớp xử lý

## Tổng quan

Tạo một IAM role tối thiểu quyền cho từng Lambda function của ReviewSentinal. Không nên dùng chung một role: processor, analyzer và API handler truy cập các nhóm tài nguyên khác nhau.

### Các role cần tạo

- `review-processor-role`
- `sentiment-analyzer-role`
- `api-handler-role`

### Yêu cầu chung

- Trust policy: `lambda.amazonaws.com`
- Quyền CloudWatch Logs cho cả ba role
- Quyền gửi SQS cho DLQ
- Quyền S3, DynamoDB và Secrets Manager được giới hạn theo từng Lambda function
- **Quyền gửi email qua SES cho role sentiment-analyzer**

## Từng bước

### 1. Tạo role cho processor

1. Mở IAM console và vào **Roles**.
2. Chọn **Create role**.
3. Chọn **AWS service** làm trusted entity.
4. Chọn use case **Lambda**.

![Guide](/Workshop/images/5-Workshop/iam-1.PNG)

5. Não attach managed policy nào ở bước này.
6. Đặt tên role là `review-processor-role` rồi tạo role.
7. Mở role và tạo inline policy trong tab **JSON**.

![Guide](/Workshop/images/5-Workshop/iam-2.PNG)

8. Dán policy của processor sau đây và thay `<ACCOUNT_ID>` bằng account ID thật:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "S3ReadAccess",
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:ListBucket"],
      "Resource": [
        "arn:aws:s3:::raw-reviews-<ACCOUNT_ID>-ap-southeast-1",
        "arn:aws:s3:::raw-reviews-<ACCOUNT_ID>-ap-southeast-1/*"
      ]
    },
    {
      "Sid": "DynamoDBWrite",
      "Effect": "Allow",
      "Action": ["dynamodb:PutItem", "dynamodb:UpdateItem", "dynamodb:GetItem", "dynamodb:Query"],
      "Resource": "arn:aws:dynamodb:ap-southeast-1:<ACCOUNT_ID>:table/Reviews"
    },
    {
      "Sid": "DynamoDBProductsAutoRegister",
      "Effect": "Allow",
      "Action": ["dynamodb:PutItem"],
      "Resource": "arn:aws:dynamodb:ap-southeast-1:<ACCOUNT_ID>:table/Products"
    },
    {
      "Sid": "DLQAccess",
      "Effect": "Allow",
      "Action": ["sqs:SendMessage"],
      "Resource": "arn:aws:sqs:ap-southeast-1:<ACCOUNT_ID>:lambda-dlq"
    },
    {
      "Sid": "CloudWatchLogs",
      "Effect": "Allow",
      "Action": ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
      "Resource": "arn:aws:logs:ap-southeast-1:<ACCOUNT_ID>:*"
    }
  ]
}
```

![Guide](/Workshop/images/5-Workshop/iam-3.PNG)

9. Lưu policy với tên `review-processor-policy`.

### 2. Tạo role cho sentiment analyzer

1. Lặp lại flow tạo role.
2. Đặt tên role là `sentiment-analyzer-role`.
3. Tạo inline policy thứ hai tên `sentiment-analyzer-policy`.
4. Dán policy của analyzer sau đây và thay `<ACCOUNT_ID>` và ARN của Secrets Manager bằng giá trị thật:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ComprehendAccess",
      "Effect": "Allow",
      "Action": [
        "comprehend:DetectSentiment",
        "comprehend:DetectKeyPhrases",
        "comprehend:DetectEntities",
        "comprehend:DetectDominantLanguage"
      ],
      "Resource": "*"
    },
    {
      "Sid": "SecretsManagerAccess",
      "Effect": "Allow",
      "Action": ["secretsmanager:GetSecretValue"],
      "Resource": "arn:aws:secretsmanager:ap-southeast-1:<ACCOUNT_ID>:secret:review-sentiment-analyzer-openrouter-api-key-XXXXXX"
    },
    {
      "Sid": "DynamoDBAccess",
      "Effect": "Allow",
      "Action": ["dynamodb:GetItem", "dynamodb:UpdateItem", "dynamodb:Query"],
      "Resource": [
        "arn:aws:dynamodb:ap-southeast-1:<ACCOUNT_ID>:table/Reviews",
        "arn:aws:dynamodb:ap-southeast-1:<ACCOUNT_ID>:table/Products",
        "arn:aws:dynamodb:ap-southeast-1:<ACCOUNT_ID>:table/Reviews/index/*"
      ]
    },
    {
      "Sid": "DynamoDBStreamsAccess",
      "Effect": "Allow",
      "Action": ["dynamodb:DescribeStream", "dynamodb:GetRecords", "dynamodb:GetShardIterator", "dynamodb:ListStreams"],
      "Resource": "arn:aws:dynamodb:ap-southeast-1:<ACCOUNT_ID>:table/Reviews/stream/*"
    },
    {
      "Sid": "SNSPublish",
      "Effect": "Allow",
      "Action": ["sns:Publish"],
      "Resource": "arn:aws:sns:ap-southeast-1:<ACCOUNT_ID>:sentiment-alerts"
    },
    {
      "Sid": "DLQAccess",
      "Effect": "Allow",
      "Action": ["sqs:SendMessage"],
      "Resource": "arn:aws:sqs:ap-southeast-1:<ACCOUNT_ID>:lambda-dlq"
    },
    {
      "Sid": "CloudWatchLogs",
      "Effect": "Allow",
      "Action": ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
      "Resource": "arn:aws:logs:ap-southeast-1:<ACCOUNT_ID>:*"
    }
  ]
}
```
5. Đảm bảo statement `DynamoDBStreamsAccess` vẫn có mặt.
6. **Thêm quyền SES**: Cho phép `ses:SendEmail` và `ses:SendRawEmail` cho địa chỉ email đã xác minh (hoặc dùng resource wildcard nếu xác minh nhiều địa chỉ).

### 3. Tạo role cho API handler

1. Tạo role Lambda thứ ba.
2. Đặt tên là `api-handler-role`.
3. Gắn inline policy `api-handler-policy`.
4. Dán policy của API handler sau đây và thay `<ACCOUNT_ID>` và secret ARN bằng giá trị thật:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DynamoDBAccess",
      "Effect": "Allow",
      "Action": ["dynamodb:GetItem", "dynamodb:Query", "dynamodb:Scan", "dynamodb:PutItem", "dynamodb:UpdateItem", "dynamodb:DeleteItem", "dynamodb:BatchWriteItem"],
      "Resource": [
        "arn:aws:dynamodb:ap-southeast-1:<ACCOUNT_ID>:table/Reviews",
        "arn:aws:dynamodb:ap-southeast-1:<ACCOUNT_ID>:table/Products",
        "arn:aws:dynamodb:ap-southeast-1:<ACCOUNT_ID>:table/Users",
        "arn:aws:dynamodb:ap-southeast-1:<ACCOUNT_ID>:table/Reviews/index/*",
        "arn:aws:dynamodb:ap-southeast-1:<ACCOUNT_ID>:table/Products/index/*"
      ]
    },
    {
      "Sid": "S3PresignedURL",
      "Effect": "Allow",
      "Action": ["s3:PutObject", "s3:GetObject"],
      "Resource": "arn:aws:s3:::raw-reviews-<ACCOUNT_ID>-ap-southeast-1/*"
    },
    {
      "Sid": "ComprehendAccess",
      "Effect": "Allow",
      "Action": ["comprehend:DetectSentiment", "comprehend:DetectKeyPhrases", "comprehend:DetectEntities", "comprehend:DetectDominantLanguage"],
      "Resource": "*"
    },
    {
      "Sid": "SecretsManagerAccess",
      "Effect": "Allow",
      "Action": ["secretsmanager:GetSecretValue"],
      "Resource": "arn:aws:secretsmanager:ap-southeast-1:<ACCOUNT_ID>:secret:review-sentiment-analyzer-openrouter-api-key-XXXXXX"
    },
    {
      "Sid": "DLQAccess",
      "Effect": "Allow",
      "Action": ["sqs:SendMessage"],
      "Resource": "arn:aws:sqs:ap-southeast-1:<ACCOUNT_ID>:lambda-dlq"
    },
    {
      "Sid": "CloudWatchLogs",
      "Effect": "Allow",
      "Action": ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
      "Resource": "arn:aws:logs:ap-southeast-1:<ACCOUNT_ID>:*"
    }
  ]
}
```
5. Thay `<ACCOUNT_ID>` và secret ARN bằng giá trị thật trong policy.

![Guide](/Workshop/images/5-Workshop/iam-4.PNG)

### Ghi chú

1. Processor cần quyền đọc S3 và ghi DynamoDB.
2. Analyzer cần quyền stream ngoài quyền truy cập bảng, và quyền SES để gửi email thông báo hoàn thành.
3. API handler cần quyền bảng rộng hơn vì phục vụ REST API và daily digest.
4. Giữ CloudWatch Logs permissions trong cả ba role để function ghi log ngay từ lần chạy đầu.
5. **Không cần quyền SNS nữa** vì analyzer function sử dụng Amazon SES để thông báo người dùng.

### Kết quả mong đợi

Kết thúc bước này, bạn sẽ có ba IAM role sẵn sàng để gắn vào các Lambda function ở subpage tiếp theo. Role `sentiment-analyzer-role` sẽ có quyền gửi email qua Amazon SES.
