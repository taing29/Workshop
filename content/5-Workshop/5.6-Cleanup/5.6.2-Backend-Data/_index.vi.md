---
title: "5.6.2 Dọn dẹp backend và dữ liệu"
weight: 2
---
# Dọn dẹp backend và dữ liệu

## Tổng quan

Xóa các tài nguyên API, compute, storage, messaging và secret đang vận hành ứng dụng.

### Những gì cần xóa

- Stage API Gateway và REST API
- Lambda function và IAM role
- Bucket S3 dùng để upload
- Các bảng DynamoDB
- SQS queue (SNS topic đã được thay thế bằng SES để gửi thông báo)
- Secrets Manager secret
- CloudWatch dashboard và alarm

## Từng bước

1. Xóa API Gateway API và stage của nó.
2. Xóa ba Lambda function.
3. Xóa CloudWatch log groups của các function đó.
4. Xóa IAM role mà Lambda đang dùng.
5. Xóa SQS queue (SNS topic không cần thiết vì thông báo sử dụng Amazon SES).
6. Xóa Secrets Manager secret.
7. Xóa các bảng DynamoDB.
8. Làm rỗng rồi xóa bucket S3 upload.
9. Xóa CloudWatch dashboard và alarm.

## Ghi chú

1. Xóa Lambda function trước rồi mới xóa role mà chúng dùng.
2. Làm rỗng bucket S3 trước khi xóa bucket.
3. Giữ thứ tự đơn giản để các tài nguyên phụ thuộc biến mất sạch sẽ.

## Kết quả mong đợi

Sau bước này, các dịch vụ chính của ứng dụng không còn tồn tại. Lưu ý rằng các địa chỉ email đã xác minh trong SES không bị xóa ở bước này vì chúng có thể được dùng cho mục đích khác.