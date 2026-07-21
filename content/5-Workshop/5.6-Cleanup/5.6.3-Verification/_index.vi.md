---
title: "5.6.3 Xác minh"
weight: 3
---

# Xác minh

## Tổng quan

Dùng trang này để xác nhận tài khoản đã sạch và không còn tài nguyên ReviewSentinal nào.

### Các kiểm tra cần chạy

- CloudFormation stack còn lại của ReviewSentinal
- Bucket S3 còn sót
- Lambda function còn sót
- DynamoDB table còn sót
- API Gateway và Cognito nếu cần kiểm tra thêm

## Từng bước

1. Kiểm tra CloudFormation xem còn stack nào của ReviewSentinal hay không.
2. Kiểm tra S3 xem còn bucket nào không.
3. Kiểm tra Lambda xem còn function nào không.
4. Kiểm tra DynamoDB xem còn table nào không.
5. Nếu muốn kỹ hơn, kiểm tra API Gateway và Cognito.
6. Xác nhận billing không còn tài nguyên ReviewSentinal đang hoạt động.

## Ghi chú

1. Thực hiện bước xác minh sau khi các bước xóa hoàn tất.
2. Nếu còn tài nguyên nào đó, hãy xóa nó trước khi kết thúc workshop.

## Kết quả mong đợi

Tài khoản nên không còn tài nguyên ReviewSentinal và sẵn sàng cho một lần triển khai mới.
