---
title: "5.5.1 Auth và API"
weight: 1
---
# Thiết lập Auth và API

## Tổng quan

Tạo lớp Cognito và API Gateway để public ReviewSentinal cho người dùng. Trang này bao gồm biên xác thực và REST API đứng trước Lambda handler.

### Những gì cần cấu hình

- Cognito user pool và app client
- API Gateway REST API
- Cognito authorizer
- CORS cho tất cả resource public

### Các endpoint chính

- `GET /products`
- `POST /products`
- `POST /upload`
- `POST /analyze`

## Từng bước

### 1. Tạo Cognito user pool

1. Mở Cognito và chọn **Create user pool**.
2. Chọn ứng dụng kiểu SPA.
3. Đặt tên `review-sentiment-analyzer-client`.
4. Chỉ bật sign-in bằng email.
5. Bật self-registration.
6. Bắt buộc `email` và `name` khi sign-up.
7. Đặt callback URL là `http://localhost:3000/callback`.
8. Tạo Hosted UI domain rồi tạo user directory.
9. Thêm `http://localhost:3000/logout` vào sign-out URLs.
10. Bật `ALLOW_ADMIN_USER_PASSWORD_AUTH` nếu cần dùng CLI test flow.

### 2. Ghi lại thông tin định danh

1. Copy User Pool ID.
2. Copy App Client ID.
3. Copy Cognito Hosted UI domain.

### 3. Tạo REST API

1. Mở API Gateway và chọn **Create API**.
2. Chọn **REST API**.
3. Đặt tên `review-sentiment-analyzer-api`.
4. Giữ endpoint type là **Regional**.

### 4. Tạo Cognito authorizer

1. Mở **Authorizers**.
2. Tạo authorizer tên `cognito-authorizer`.
3. Chọn type **Cognito**.
4. Gắn user pool vừa tạo.
5. Token source là `Authorization`.

### 5. Tạo resource tree

1. Tạo `/products`.
2. Tạo `{id}` bên trong `/products`.
3. Tạo `reviews` và `analytics` bên trong `{id}`.
4. Tạo `{review_id}` bên trong `reviews`.
5. Tạo các resource `/upload` và `/analyze`.

### 6. Gắn method và integration

1. Tạo method cần thiết cho từng resource.
2. Bật Lambda proxy integration.
3. Trỏ tất cả method vào `review-sentiment-analyzer-api`.
4. Gắn authorization `cognito-authorizer` cho route protected.

### 7. Bật CORS

1. Bật CORS cho từng resource public.
2. Cho phép các header cần thiết như `Authorization` và `X-Api-Key`.
3. Bật gateway responses cho `Default 4XX` và `Default 5XX`.
4. Xác nhận console tạo `OPTIONS` method tự động.

### 8. Deploy API

1. Deploy stage mới tên `dev`.
2. Copy Invoke URL từ stage.

### Ghi chú

1. Giữ callback và sign-out URL khớp với domain của frontend.
2. Khi gắn authorizer, dùng user pool ID chứ không dùng app client ID.
3. Cấp quyền Lambda invoke từ API Gateway ngay lúc tạo method.

### Kết quả mong đợi

Ứng dụng sẽ có luồng đăng nhập hoạt động và một REST API stage đã deploy để dùng cho dashboard và luồng upload.