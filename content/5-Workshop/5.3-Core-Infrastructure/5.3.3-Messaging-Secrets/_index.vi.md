---
title: "5.3.3 Messaging và secret"
weight: 3
---

# Messaging và secret cho ReviewSentinal

## Tổng quan

Tạo dead-letter queue, cấu hình Amazon SES để gửi thông báo người dùng, và thiết lập secret mà các Lambda sẽ dùng ở các bước sau.

### SQS dead-letter queue

1. Mở SQS và chọn **Create queue**.
2. Chọn **Standard**.
3. Đặt tên queue là `lambda-dlq`.

![Guide](/Workshop/images/5-Workshop/sqs-1.PNG)

4. Xác nhận encryption **SSE-SQS** đang bật.
5. Đặt message retention là 14 ngày.
6. Tạo queue.
7. Copy ARN của queue từ trang chi tiết.

![Guide](/Workshop/images/5-Workshop/sqs-2.PNG)

### Amazon SES cho thông báo người dùng

1. Truy cập **Amazon SES → Verified identities → Create identity**
2. Loại kiểu danh tính: **Địa chỉ email**
3. Email: `noreply@yourdomain.com` (hoặc Gmail của bạn nếu bạn đang trong SES sandbox)
4. Xác minh địa chỉ email
5. *(Chỉ dành cho sandbox)* Xác minh chính địa chỉ email nhận của bạn

![Guide](/Workshop/images/5-Workshop/messaging-1.PNG)

### Secrets Manager secret

1. Mở Secrets Manager và chọn **Store a new secret**.
2. Chọn **Other type of secret**.
3. Dùng tab **Plaintext**, không dùng key/value pairs.
4. Nhập giá trị placeholder như `REPLACE_ME_LATER`.
5. Giữ encryption bằng key AWS-managed mặc định.

![Guide](/Workshop/images/5-Workshop/messaging-2.PNG)

6. Đặt tên secret `review-sentiment-analyzer-openrouter-api-key`.
7. Bỏ rotation và lưu lại.
8. Copy ARN của secret.

![Guide](/Workshop/images/5-Workshop/messaging-3.PNG)

### Kết quả mong đợi

Bạn nên có:
- ARN của SQS DLQ
- Địa chỉ email SES đã xác minh làm người gửi
- ARN của Secrets Manager secret

Các ARN và chi tiết cấu hình này sẽ được sử dụng trong chính sách IAM và biến môi trường Lambda trong các phần sau.