---
title: "5.5.1 Cấu hình xác thực và API"
weight: 1
---

# Cấu hình xác thực và API

## Tổng quan

Trong phần này, bạn sẽ tạo **Amazon Cognito** và **Amazon API Gateway** để cung cấp giao diện truy cập của ReviewSentinal cho người dùng.

Phần này bao gồm việc cấu hình hệ thống xác thực người dùng và REST API kết nối đến Lambda API.

### Những thành phần cần cấu hình

- Cognito User Pool và App Client
- API Gateway REST API
- Cognito Authorizer
- CORS cho tất cả các tài nguyên (resource) công khai

### Các endpoint chính

- `GET /products`
- `POST /products`
- `POST /upload`
- `POST /analyze`

## Các bước thực hiện

### 1. Tạo Cognito User Pool

1. Mở **Amazon Cognito** và chọn **Create user pool**.
2. Chọn **Single-page application (SPA)** làm loại ứng dụng.
3. Đặt tên ứng dụng `review-sentiment-analyzer-client`.
4. Chỉ sử dụng **Email** & **Username** làm phương thức đăng nhập.
5. Bật **Self-registration** cho phiên bản demo.
6. Yêu cầu người dùng nhập cả `email` và `name` khi đăng ký.

![Guide](/Workshop/images/5-Workshop/auth-1.PNG)

7. Đặt **Callback URL** là `http://localhost:3000/callback`.

![Guide](/Workshop/images/5-Workshop/auth-2.PNG)

8. Chọn tiền tố cho **Hosted UI domain** rồi tạo User Pool.
9. Sau khi tạo xong, mở **App client settings** và thêm `http://localhost:3000/logout` vào **Sign-out URL**.
10. Bật `ALLOW_ADMIN_USER_PASSWORD_AUTH` nếu bạn dự định sử dụng quy trình kiểm thử bằng AWS CLI ở các phần sau.

![Guide](/Workshop/images/5-Workshop/auth-3.PNG)

![Guide](/Workshop/images/5-Workshop/auth-4.PNG)

### 2. Lưu lại các thông tin định danh

1. Sao chép **User Pool ID** từ trang tổng quan.
2. Sao chép **App Client ID** từ danh sách App Client.
3. Sao chép **Hosted UI Domain** của Cognito từ trang Domain.

### 3. Tạo REST API

1. Mở **Amazon API Gateway** và chọn **Create API**.
2. Chọn **REST API** rồi tạo **New API**.

![Guide](/Workshop/images/5-Workshop/auth-6.PNG)

3. Đặt tên API `review-sentiment-analyzer-api`.
4. Giữ nguyên **Endpoint type** là **Regional**.
5. Chọn **Create API**.

![Guide](/Workshop/images/5-Workshop/auth-7.PNG)

### 4. Tạo Cognito Authorizer

1. Trong thanh điều hướng bên trái, chọn **Authorizers**.

![Guide](/Workshop/images/5-Workshop/auth-8.PNG)

2. Tạo Authorizer mới có tên `cognito-authorizer`.
3. Chọn loại **Cognito**.
4. Liên kết với User Pool vừa tạo.
5. Đặt **Token source** là `Authorization`.

![Guide](/Workshop/images/5-Workshop/auth-9.PNG)

### 5. Tạo cây Resource

1. Tạo resource `/products`.
2. Bên trong `/products`, tạo resource `{id}`.
3. Bên trong `{id}`, tạo hai resource:
   - `reviews`
   - `analytics`
4. Bên trong `reviews`, tạo resource `{review_id}`.
5. Tạo thêm hai resource cấp cao nhất:
   - `/upload`
   - `/analyze`

![Guide](/Workshop/images/5-Workshop/auth-10.PNG)

### 6. Thêm Method và Integration

```
/
└── products                       (GET, POST)
    └── {id}                       (DELETE)
        ├── reviews                (GET)
        │   └── {review_id}        (DELETE)
        └── analytics              (GET)
/upload                            (POST)
/analyze                           (POST)
```

Đối với **mọi method** (`GET /products`, `POST /products`, `DELETE /products/{id}`, `GET /products/{id}/reviews`, `DELETE /products/{id}/reviews/{review_id}`, `GET /products/{id}/analytics`, `POST /upload`, `POST /analyze`):

1. Trên resource tương ứng, chọn **Create method**.
2. Chọn **Method type** theo sơ đồ trên.
3. Chọn **Integration type** là **Lambda function**.
4. Bật **Lambda proxy integration**.
5. Đặt **Response transfer mode** là **Buffered**.
6. Chọn Lambda function `review-sentiment-analyzer-api`.
7. Giữ nguyên phần **Method request settings** (không cần khai báo query parameters, headers hoặc request body).
8. Chọn **Create method**.

![Guide](/Workshop/images/5-Workshop/auth-11.PNG)

9. Sau khi tạo xong, mở lại method → trong phần **Method request** → **Authorization**, chọn `cognito-authorizer`.

![Guide](/Workshop/images/5-Workshop/auth-12.PNG)

![Guide](/Workshop/images/5-Workshop/auth-13.PNG)

### 7. Cấu hình CORS

1. Bật **CORS** cho tất cả các resource công khai.
2. Cho phép các header sau:
   - `Content-Type`
   - `Authorization`
   - `X-Api-Key`
   - `X-Amz-Security-Token`
3. Thêm hai **Gateway Response**:
   - `Default 4XX`
   - `Default 5XX`
4. Xác nhận API Gateway tự động tạo các method `OPTIONS`.

![Guide](/Workshop/images/5-Workshop/auth-14.PNG)

### 8. Triển khai API

1. Triển khai API lên một stage mới có tên `dev`.

![Guide](/Workshop/images/5-Workshop/auth-15.PNG)

2. Sao chép **Invoke URL** từ trang Stage để sử dụng cho frontend.

![Guide](/Workshop/images/5-Workshop/auth-16.PNG)

### Lưu ý

1. Đảm bảo **Callback URL** và **Sign-out URL** khớp với địa chỉ của ứng dụng frontend.
2. Khi cấu hình **Authorizer**, hãy sử dụng **User Pool ID**, không phải **App Client ID**.
3. Trong quá trình tạo từng method, hãy cấp quyền để API Gateway có thể gọi Lambda tương ứng.

### Kết quả mong đợi

Sau khi hoàn thành:

- Người dùng có thể đăng nhập thông qua Amazon Cognito.
- REST API đã được triển khai thành công trên stage `dev`.
- API đã sẵn sàng để frontend sử dụng cho Dashboard, Upload và các chức năng còn lại của ReviewSentinal.