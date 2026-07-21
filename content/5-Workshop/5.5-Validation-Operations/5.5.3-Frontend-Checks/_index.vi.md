---
title: "5.5.3 Kiểm tra frontend"
weight: 3
---

# Kiểm tra frontend

## Tổng quan

Dùng các giá trị backend đã triển khai để kiểm tra cấu hình frontend và luồng người dùng cơ bản. Trang này giữ cho bước kiểm tra cuối cùng tập trung vào các điểm tích hợp thật thay vì chỉ nhìn giao diện.

### Những gì cần xác minh

- API URL trỏ đúng vào stage đã deploy
- Cognito authority và client ID chính xác
- Redirect và logout URL khớp với domain frontend
- Luồng upload từ trình duyệt có thể gọi trực tiếp đến S3

## Từng bước

### 1. Chuẩn bị frontend local

1. Tạo ứng dụng Vite React TypeScript nếu chưa có.
2. Cài các dependencies cần thiết.
3. Cấu hình Tailwind nếu dùng dashboard đã style.
4. Cập nhật favicon và title trong `index.html`.

### 2. Thiết lập biến môi trường

1. Tạo file `.env` ở root frontend.
2. Thêm API URL từ API Gateway.
3. Thêm Cognito authority và client ID.
4. Thêm Cognito Hosted UI domain.
5. Thêm redirect và logout URI cho domain đã deploy.

### 3. Build và deploy

1. Chạy build local.
2. Zip output build.
3. Upload thủ công lên Amplify.
4. Xác nhận app phục vụ từ domain Amplify.

### 4. Cập nhật Cognito và S3

1. Thêm domain đã deploy vào callback và sign-out URLs của Cognito.
2. Thêm domain đã deploy vào CORS allowed origins của bucket S3.
3. Lưu lại cả hai thay đổi.

### 5. Kiểm tra trên trình duyệt

1. Mở frontend đã deploy.
2. Đăng nhập qua Cognito Hosted UI.
3. Xác nhận dashboard tải thành công.
4. Upload file review mẫu.
5. Xác nhận review xuất hiện sau khi processor và analyzer hoàn tất.
6. Đăng xuất và kiểm tra app quay lại sign-in gate.

### Kết quả mong đợi

Frontend cần có thể xác thực, upload dữ liệu và lấy kết quả mà không gặp lỗi redirect hay CORS.
