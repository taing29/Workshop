---
title: "Xác thực và vận hành"
date: 2024-01-01
weight: 5
chapter: false
pre: " <b> 5.5. </b> "
---

#### Tổng quan

Phần này bao gồm lớp tích hợp phía người dùng: API Gateway, Cognito, CORS, dashboard CloudWatch, và các bước kiểm tra trước khi coi việc triển khai là hoàn tất.

#### Nội dung

1. [Auth và API](5.5.1-auth-api/)
2. [Monitoring](5.5.2-monitoring/)
3. [Kiểm tra frontend](5.5.3-frontend-checks/)
4. [Sẵn sàng triển khai](5.5.4-ready-to-launch/)
5. [Dữ liệu test mẫu](5.5.5-sample-test-data/)

#### Cấu hình truy cập

1. Tạo Cognito user pool và app client cho luồng đăng nhập của frontend.
2. Tạo các REST API method cho products, reviews, upload và analysis.
3. Bật CORS cho các resource API và deploy stage `dev`.
4. Thêm widget và alarm CloudWatch cho Lambda, DynamoDB và độ trễ API.
5. Build và test frontend với API URL và cấu hình Cognito đã triển khai.

#### Danh sách kiểm tra

+ Tải lên một file review mẫu và xác nhận processor ghi dữ liệu vào DynamoDB.
+ Xác nhận sentiment analyzer cập nhật review và có thể gửi cảnh báo.
+ Đăng nhập qua Cognito và thử các API route từ trình duyệt.
+ Kiểm tra dashboard và alarm ở trạng thái ổn định trước khi chuyển sang bước tiếp theo.
