---
title: "5.4.2 Lambda function"
weight: 2
---

# Lambda function cho ReviewSentinal

## Tổng quan

Tạo ba Lambda handler để xử lý luồng nhận dữ liệu, phân tích và API. Ba function dùng chung một deployment package, nhưng có cấu hình runtime, memory, timeout và biến môi trường khác nhau.

### Các function cần tạo

1. `review-sentiment-analyzer-processor`
2. `review-sentiment-analyzer-analyzer`
3. `review-sentiment-analyzer-api`

### Thiết lập chung

- Runtime: Python 3.11
- Architecture: x86_64
- Source package: file chung `01_lambda_functions.py`
- Dead-letter queue: `lambda-dlq`

## Từng bước

### 1. Tạo function processor

1. Mở **Lambda** và chọn **Create function**.
2. Chọn **Author from scratch**.
3. Đặt tên `review-sentiment-analyzer-processor`.
4. Chọn Python 3.11 và architecture x86_64.
5. Dùng existing role `review-processor-role`.
6. Tạo function.
7. Dán toàn bộ nội dung `01_lambda_functions.py` vào tab code.
8. Deploy code.
9. Set handler thành `lambda_function.lambda_handler_review_processor`.
10. Timeout 1 phút, memory 512 MB.
11. Thêm các biến môi trường `REVIEWS_TABLE`, `PRODUCTS_TABLE`, `USERS_TABLE`, `RAW_BUCKET`.
12. Cấu hình DLQ bất đồng bộ dùng `lambda-dlq`.

### 2. Tạo function analyzer

1. Tạo Lambda thứ hai tên `review-sentiment-analyzer-analyzer`.
2. Dùng Python 3.11 và role `sentiment-analyzer-role`.
3. Dán lại cùng package và deploy.
4. Set handler thành `lambda_function.lambda_handler_sentiment_analyzer`.
5. Timeout 2 phút, memory 1024 MB.
6. Thêm các biến `REVIEWS_TABLE`, `PRODUCTS_TABLE`, `OPENROUTER_MODEL`, `OPENROUTER_API_KEY_SECRET_NAME`.
   **Quan trọng**: Function này giờ sử dụng Amazon SES để gửi email thay vì SNS, vì vậy không cần biến `SNS_TOPIC_ARN` nữa.
7. Dùng cùng DLQ.

### 3. Tạo function API

1. Tạo Lambda thứ ba tên `review-sentiment-analyzer-api`.
2. Dùng Python 3.11 và role `api-handler-role`.
3. Dán cùng package và deploy.
4. Set handler thành `lambda_function.lambda_handler_api`.
5. Timeout 30 giây, memory 256 MB.
6. Thêm `REVIEWS_TABLE`, `PRODUCTS_TABLE`, `USERS_TABLE`, `RAW_BUCKET`, `CORS_ALLOWED_ORIGIN`.
7. Dùng cùng DLQ.

### Luồng xử lý hoàn thành phân tích (đã cập nhật)

Function analyzer hiện thực hiện luồng này khi xử lý reviews:
1. Xử lý một review từ stream
2. Cập nhật bản ghi review với kết quả phân tích cảm xúc
3. Tăng các bộ đếm phân tích (ProcessedReviews, Positive/Neutral/Negative)
4. Kiểm tra xem tất cả reviews cho một analysis đã được xử lý chưa (ProcessedReviews == TotalReviews)
5. Nếu CHƯA hoàn thành: Dừng xử lý
6. Nếu HOÀN THÀNH:
   - Cập nhật trạng thái analysis thành COMPLETED
   - Đặt timestamp CompletedAt
   - Gửi email hoàn thành qua Amazon SES tới địa chỉ email của người dùng
   - Dừng xử lý

### Ghi chú

1. Giữ toàn bộ handler trong một source file để triển khai đơn giản.
2. Processor ghi review sau khi upload từ S3.
3. Analyzer chạy Comprehend và có thể gọi OpenRouter, sau đó gửi email hoàn thành qua SES.
4. API function phục vụ REST request và digest hằng ngày.

### Kết quả mong đợi

Ba Lambda function phải tồn tại, dùng đúng role, và sẵn sàng cho bước nối event source tiếp theo. Function analyzer nên được cấu hình để gửi email qua Amazon SES khi analysis hoàn thành.
