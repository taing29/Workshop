---
title: "Worklog Tuần 11"
date: 2026-07-13
weight: 11
chapter: false
pre: " <b> 1.11. </b> "
---

### Mục tiêu tuần 11:

* Hoàn thiện kiến trúc tổng thể của hệ thống ReviewSentinel trên nền tảng AWS.
* Thiết kế mô hình bảo mật, mô hình dữ liệu và đặc tả các thành phần xử lý của hệ thống.
* Chuẩn bị hạ tầng và môi trường phát triển để sẵn sàng triển khai dự án trong các tuần tiếp theo.

### Các công việc cần triển khai trong tuần này:

| Công việc | Ngày bắt đầu | Ngày hoàn thành | Nguồn tài liệu |
| --- | ------------ | --------------- | -------------- |
| Hoàn thiện kiến trúc hệ thống ReviewSentinel <br> - Rà soát kiến trúc tổng thể <br> - Xác định các dịch vụ AWS sử dụng <br> - Hoàn thiện luồng xử lý dữ liệu | 13/07/2026 | 13/07/2026 | AWS Study Group |
| Thiết kế mô hình bảo mật <br> - Thiết kế Amazon Cognito User Pool <br> - Xây dựng cơ chế xác thực JWT với API Gateway <br> - Thiết kế IAM Role theo nguyên tắc Least Privilege | 14/07/2026 | 14/07/2026 | AWS Study Group |
| Thiết kế mô hình dữ liệu <br> - Thiết kế bảng DynamoDB (Reviews, Products, Users) <br> - Xây dựng Primary Key, GSI và các mẫu truy vấn <br> - Lập kế hoạch sử dụng Amazon S3 và Event Notification | 15/07/2026 | 15/07/2026 | AWS Study Group |
| Thiết kế Lambda Functions và chuẩn bị hạ tầng <br> - Xây dựng đặc tả cho review_processor, sentiment_analyzer và api_handler <br> - Xác định Input/Output, Error Handling <br> - Chuẩn bị S3 Bucket, DynamoDB và môi trường phát triển | 16/07/2026 | 16/07/2026 | AWS Study Group |

### Kết quả đạt được tuần 11:

* Hoàn thiện kiến trúc tổng thể của hệ thống **ReviewSentinel**, bao gồm các thành phần Amazon API Gateway, Amazon Cognito, AWS Lambda, Amazon DynamoDB, Amazon S3, Amazon Comprehend, Amazon Bedrock và Amazon CloudWatch, đồng thời xác định rõ luồng xử lý dữ liệu giữa các dịch vụ.

* Thiết kế mô hình bảo mật cho hệ thống bằng Amazon Cognito kết hợp JWT Authentication và IAM Role theo nguyên tắc **Least Privilege**, đồng thời xác định các yêu cầu bảo mật như mã hóa dữ liệu, kiểm soát quyền truy cập và quản lý log.

* Hoàn thành thiết kế cơ sở dữ liệu trên Amazon DynamoDB với các bảng **Reviews**, **Products** và **Users**, bao gồm Primary Key, Global Secondary Index (GSI) và các mẫu truy vấn phục vụ quá trình phân tích dữ liệu và xử lý đánh giá.

* Xây dựng đặc tả cho các Lambda Function chính gồm **review_processor**, **sentiment_analyzer** và **api_handler**, xác định cơ chế kích hoạt, Input/Output, quy trình xử lý lỗi và chuẩn bị các thành phần hạ tầng như Amazon S3 Bucket, DynamoDB để sẵn sàng triển khai trong giai đoạn tiếp theo.