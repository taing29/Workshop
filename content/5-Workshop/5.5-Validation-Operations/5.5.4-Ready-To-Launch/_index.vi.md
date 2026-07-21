---
title: "5.5.4 Sẵn sàng triển khai"
weight: 4
---

# Sẵn sàng triển khai

## Tổng quan

Dùng trang này như checkpoint cuối cùng trước khi coi workshop hoàn tất. Nó tóm tắt những gì cần đang hoạt động và điều kiện phải đúng trước khi dọn dẹp.

### Danh sách sẵn sàng cuối cùng

- Bucket S3 upload đã tồn tại và bật CORS.
- Các bảng DynamoDB đã có và stream đang chạy.
- Lambda function đã nối đúng trigger.
- API Gateway và Cognito đã tích hợp.
- Dashboard và alarm đã hiển thị.

## Từng bước

### 1. Chạy luồng end-to-end

1. Dùng dữ liệu test từ hướng dẫn mẫu.
2. Đăng ký user trong Cognito.
3. Đăng nhập vào frontend.
4. Upload review file.
5. Xác nhận processor và analyzer đã cập nhật dữ liệu.
6. Kiểm tra dashboard có phản ánh activity mới.

### 2. Bật luồng phân tích sâu nếu muốn

1. Lưu API key OpenRouter thật vào Secrets Manager.
2. Xác nhận analyzer Lambda đọc được secret.
3. Kích hoạt luồng phân tích tùy chọn từ upload hoặc analyze flow.

### 3. Quyết định handoff hoặc tiếp tục

1. Nếu mọi kiểm tra đều đạt, chuyển sang cleanup.
2. Nếu có bước nào thất bại, quay lại section tương ứng và sửa trước khi xóa tài nguyên.

### Ghi chú

1. Nếu có bước kiểm tra nào chưa đạt, hãy quay lại đúng subpage tương ứng thay vì đoán cách sửa.
2. Giữ đường OpenRouter tùy chọn ở trạng thái tắt trừ khi bạn thật sự cần.
3. Coi trang này là điểm sign-off trước khi chuyển sang dọn dẹp.

### Kết quả mong đợi

Đến lúc này, triển khai nên sẵn sàng bàn giao và an toàn để dọn dẹp.
