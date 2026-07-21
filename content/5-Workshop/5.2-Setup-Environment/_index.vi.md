---
title: "Điều kiện chuẩn bị"
date: 2024-01-01
weight: 2
chapter: false
pre: " <b> 5.2. </b> "
---

#### Bạn cần chuẩn bị

+ Một tài khoản AWS có quyền tạo các tài nguyên S3, DynamoDB, Lambda, IAM, Cognito, API Gateway, CloudWatch, SES, SQS và Secrets Manager.
+ Một region thống nhất cho toàn bộ bài triển khai. Hướng dẫn này dùng `ap-southeast-1`.
+ Mã nguồn ReviewSentinal và Account ID của tài khoản AWS.
+ Máy local có trình duyệt, cùng Node.js nếu bạn định build frontend trên máy.

#### Trước khi bắt đầu

1. Đăng nhập AWS Console và kiểm tra region đã là `ap-southeast-1`.
2. Ghi lại Account ID từ menu người dùng ở góc trên bên phải.
3. Đảm bảo bạn có thể mở các console S3, DynamoDB, Lambda, Cognito, API Gateway và CloudWatch mà không bị lỗi quyền.
4. Giữ hướng dẫn triển khai mở trong lúc làm, vì nhiều bước sau sẽ dùng lại cùng tên tài nguyên và ARN.

#### Kết quả mong đợi

Kết thúc phần này, bạn đã có quyền truy cập console, region đã được chọn, và đủ thông tin nền để đặt tên tài nguyên nhất quán ở các bước tiếp theo.
