---
title: "5.4.3 Cấu hình Event Trigger"
weight: 3
---

# Cấu hình Event Trigger cho ReviewSentinal

## Tổng quan

Trong phần này, bạn sẽ kết nối các sự kiện từ dịch vụ lưu trữ và cơ sở dữ liệu với các hàm Lambda để toàn bộ quy trình xử lý được thực hiện tự động.

Đây là bước liên kết hạ tầng AWS đã tạo ở các phần trước với logic xử lý của ứng dụng được cấu hình ở phần trước.

### Các trigger cần cấu hình

- Sự kiện **S3 Object Created** cho Lambda **Processor**
- **DynamoDB Streams** cho Lambda **Analyzer**

## Các bước thực hiện

### 1. Cấu hình S3 Trigger

1. Mở Lambda `review-sentiment-analyzer-processor`.
2. Chọn **Add trigger**.
3. Chọn **S3**.
4. Chọn bucket lưu trữ dữ liệu gốc (Raw Upload Bucket).
5. Đặt **Event type** là **All object create events**.
6. Thêm tiền tố (Prefix) `uploads/`.
7. Xác nhận cảnh báo về **recursive invocation** rồi chọn **Add** để tạo trigger.

![Guide](/Workshop/images/5-Workshop/event-1.PNG)

### 2. Cấu hình DynamoDB Stream Trigger

1. Mở Lambda `review-sentiment-analyzer-analyzer`.
2. Chọn **Add trigger**.
3. Chọn **DynamoDB**.
4. Chọn bảng `Reviews`.
5. Giữ nguyên:
   - **Batch size:** `100`
   - **Starting position:** **Latest**

![Guide](/Workshop/images/5-Workshop/event-2.PNG)

6. Thêm **Filter criteria** để Lambda chỉ được kích hoạt khi xảy ra sự kiện `INSERT` và trường `ProcessingStatus` có giá trị `PENDING`.

```json
[
  {
    "Pattern": "{  \"eventName\": [\"INSERT\"],  \"dynamodb\": {    \"NewImage\": {      \"ProcessingStatus\": {        \"S\": [\"PENDING\"]      }    }  }}"
  }
]
```

![Guide](/Workshop/images/5-Workshop/event-3.PNG)

7. Bật tùy chọn **Split batch on error**.
8. Chọn **Add** để tạo trigger.

### Lưu ý

1. S3 Trigger là điểm bắt đầu của toàn bộ quy trình tiếp nhận và xử lý dữ liệu.
2. DynamoDB Streams Trigger cần lọc các sự kiện cập nhật do chính Lambda **Analyzer** tạo ra để tránh kích hoạt lại Lambda không cần thiết.

   Hiện tại, Lambda **Analyzer** sẽ:

   - Xử lý các bản ghi review mới.
   - Cập nhật kết quả phân tích cảm xúc cho từng review.
   - Cập nhật bộ đếm của bản ghi phân tích tương ứng (`ProcessedReviews`, `Positive`, `Neutral`, `Negative`).
   - Khi tất cả review của một phiên phân tích đã được xử lý, Lambda sẽ:
     - Cập nhật trạng thái phân tích thành `COMPLETED`.
     - Ghi thời điểm hoàn thành vào trường `CompletedAt`.
     - Gửi email thông báo hoàn thành thông qua **Amazon SES** đến địa chỉ email của người dùng.

### Kết quả mong đợi

Sau khi hoàn thành cấu hình:

- Quy trình xử lý sẽ tự động bắt đầu khi có tệp mới được tải lên Amazon S3.
- Dữ liệu sẽ tiếp tục được xử lý thông qua **DynamoDB Streams**.
- Lambda **Analyzer** sẽ tự động:
  - Cập nhật kết quả phân tích cho từng review.
  - Cập nhật trạng thái và thống kê của bản ghi phân tích.
  - Gửi email thông báo hoàn thành qua **Amazon SES** khi toàn bộ quá trình phân tích kết thúc.