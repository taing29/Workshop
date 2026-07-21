---
title: "Tổng quan workshop"
date: 2024-01-01
weight: 1
chapter: false
pre: " <b> 5.1. </b> "
---

#### ReviewSentinal là gì

ReviewSentinal là một ứng dụng AWS serverless nhận dữ liệu đánh giá sản phẩm, lưu vào DynamoDB, chấm điểm cảm xúc bằng Amazon Comprehend, và hiển thị kết quả qua API Gateway cùng các endpoint được bảo vệ bởi Cognito.

#### Những gì được triển khai

+ **Lưu trữ và sự kiện**: S3 cho file tải lên thô, DynamoDB cho dữ liệu review và sản phẩm, SQS cho lỗi, SES cho cảnh báo.
+ **Xử lý**: ba Lambda function cho nhận review, phân tích cảm xúc và API.
+ **Lớp truy cập**: API Gateway, Cognito, và luồng upload/query ở phía frontend.
+ **Phân tích tùy chọn**: Secrets Manager lưu API key OpenRouter nếu bạn muốn bật bước phân tích sâu hơn.

#### Mục tiêu triển khai

Hãy dùng cùng một AWS region xuyên suốt workshop. Hướng dẫn này được viết cho `ap-southeast-1` và mặc định mọi tài nguyên đều dùng region đó, trừ khi có bước ghi khác.
