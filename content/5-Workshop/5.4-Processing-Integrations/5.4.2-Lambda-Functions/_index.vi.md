---
title: "5.4.2 Các hàm Lambda"
weight: 2
---

# Tạo các hàm Lambda cho ReviewSentinal

## Tổng quan

Trong phần này, bạn sẽ tạo ba hàm **AWS Lambda** đảm nhiệm quy trình tiếp nhận dữ liệu, phân tích cảm xúc và cung cấp API cho ReviewSentinal.

Cả ba Lambda đều sử dụng cùng một **deployment package**, tuy nhiên mỗi hàm sẽ có **handler**, **runtime settings**, **environment variables** và **trigger** riêng.

### Các hàm cần tạo

1. `review-sentiment-analyzer-processor`
2. `review-sentiment-analyzer-analyzer`
3. `review-sentiment-analyzer-api`

### Cấu hình chung

- Runtime: **Python 3.11**
- Architecture: **x86_64**
- Source package: tệp `01_lambda_functions.py`
- Dead-letter queue (DLQ): `lambda-dlq`

## Các bước thực hiện

### 1. Tạo hàm Processor

1. Mở **AWS Lambda** và chọn **Create function**.
2. Chọn **Author from scratch**.
3. Đặt tên hàm `review-sentiment-analyzer-processor`.
4. Chọn **Python 3.11** và kiến trúc mặc định **x86_64**.

![Guide](/Workshop/images/5-Workshop/lambda-1.PNG)

5. Sử dụng IAM role hiện có `review-processor-role`.
6. Chọn **Create function**.
7. Thay thế toàn bộ mã mặc định bằng nội dung của tệp `01_lambda_functions.py`.
8. Chọn **Deploy**.

![Guide](/Workshop/images/5-Workshop/lambda-2.PNG)

9. Mở **Runtime settings** và đặt **Handler** thành `lambda_function.lambda_handler_review_processor`.

![Guide](/Workshop/images/5-Workshop/lambda-3.PNG)

10. Đặt **Timeout** là **1 minute** và **Memory** là **512 MB**.

![Guide](/Workshop/images/5-Workshop/lambda-4.PNG)

11. Thêm các biến môi trường `REVIEWS_TABLE`, `PRODUCTS_TABLE`, `USERS_TABLE` và `RAW_BUCKET`.

![Guide](/Workshop/images/5-Workshop/lambda-5.PNG)

12. Cấu hình **Asynchronous invocation** để sử dụng **Dead-letter queue (DLQ)** là `lambda-dlq`.

![Guide](/Workshop/images/5-Workshop/lambda-6.PNG)

### 2. Tạo hàm Analyzer

1. Tạo Lambda thứ hai với tên `review-sentiment-analyzer-analyzer`.
2. Chọn **Python 3.11** và sử dụng IAM role hiện có `sentiment-analyzer-role`.
3. Dán lại cùng deployment package và chọn **Deploy**.
4. Đặt **Handler** thành `lambda_function.lambda_handler_sentiment_analyzer`.
5. Đặt **Timeout** là **2 minutes** và **Memory** là **1024 MB**.
6. Thêm các biến môi trường `REVIEWS_TABLE`, `PRODUCTS_TABLE`, `OPENROUTER_MODEL` và `OPENROUTER_API_KEY_SECRET_NAME`.
7. Cấu hình **Asynchronous invocation** để sử dụng **Dead-letter queue (DLQ)** là `lambda-dlq`.

### 3. Tạo hàm API

1. Tạo Lambda thứ ba với tên `review-sentiment-analyzer-api`.
2. Chọn **Python 3.11** và sử dụng IAM role hiện có `api-handler-role`.
3. Dán cùng deployment package và chọn **Deploy**.
4. Đặt **Handler** thành `lambda_function.lambda_handler_api`.
5. Đặt **Timeout** là **30 seconds** và **Memory** là **256 MB**.
6. Thêm các biến môi trường `REVIEWS_TABLE`, `PRODUCTS_TABLE`, `USERS_TABLE`, `RAW_BUCKET` và `CORS_ALLOWED_ORIGIN`.
7. Cấu hình **Asynchronous invocation** để sử dụng **Dead-letter queue (DLQ)** là `lambda-dlq`.

![Guide](/Workshop/images/5-Workshop/lambda-7.PNG)

### Quy trình hoàn thành phân tích

Sau khi được kích hoạt, Lambda **Analyzer** sẽ thực hiện quy trình sau:

1. Xử lý tất cả các bản ghi review từ batch của **DynamoDB Streams**.
2. Với mỗi review:
   - Thực hiện phân tích cảm xúc bằng **Amazon Comprehend**.
   - Nếu được yêu cầu, lấy thêm phân tích chuyên sâu từ **OpenRouter**.
   - Cập nhật kết quả phân tích vào bản ghi review.
   - Xác định người tải lên review thông qua trường `UploadedBy`.
   - Cập nhật bộ đếm số lượng review theo từng nhóm cảm xúc (**Positive**, **Neutral**, **Negative**, **Mixed**).
3. Sau khi xử lý toàn bộ bản ghi:
   - Ghi log tổng kết quá trình phân tích.
   - Nhóm các review theo người tải lên, sau đó theo từng sản phẩm.
   - Tính số lượng review thuộc từng nhóm cảm xúc cho mỗi cặp người dùng và sản phẩm.
   - Gửi email tổng kết riêng cho từng người dùng thông qua **Amazon SES** đối với mỗi sản phẩm mà họ đã tải lên.
   - Email sẽ bao gồm kết quả phân tích theo đúng định dạng yêu cầu.

### Lưu ý

1. Giữ cả ba **handler** trong cùng một tệp mã nguồn để việc triển khai được đơn giản hơn.
2. Lambda **Processor** ghi các bản ghi review sau khi dữ liệu được tải lên Amazon S3.
3. Lambda **Analyzer** thực hiện phân tích bằng **Amazon Comprehend**, có thể gọi thêm **OpenRouter**, sau đó gửi email thông báo hoàn thành thông qua **Amazon SES**.
4. Lambda **API** phục vụ các yêu cầu REST API và tác vụ gửi báo cáo tổng hợp hằng ngày (Daily Digest).

### Kết quả mong đợi

Sau khi hoàn thành, cả ba Lambda function sẽ được tạo thành công, sử dụng đúng IAM role và sẵn sàng để cấu hình **Event Source Mapping** ở phần tiếp theo.

Lambda **Analyzer** cũng sẽ được cấu hình để gửi email thông báo hoàn thành quá trình phân tích thông qua **Amazon SES**.