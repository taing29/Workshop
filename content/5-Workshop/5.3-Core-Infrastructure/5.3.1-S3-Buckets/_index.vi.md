---
title: "5.3.1 S3 buckets"
weight: 1
---

# S3 buckets cho ReviewSentinal

## Tổng quan

Tạo bucket upload thô trước. Ứng dụng upload file review trực tiếp lên S3, nên bucket này là điểm bắt đầu của toàn bộ pipeline.

### Bucket cần tạo

- `raw-reviews-<ACCOUNT_ID>-ap-southeast-1`

### Các bước thực hiện

1. Mở S3 console và chọn **Create bucket**.
2. Nhập tên bucket theo đúng AWS account ID của bạn.
3. Chọn **Asia Pacific (Singapore) ap-southeast-1**.
4. Giữ **ACLs disabled**.

![Guide](/Workshop/images/5-Workshop/s3-bucket-1.PNG)

5. Để **Block all public access** bật.
6. Bật **Bucket Versioning**.

![Guide](/Workshop/images/5-Workshop/s3-bucket-2.PNG)

7. Bật mã hóa mặc định với **SSE-S3**.
8. Tạo bucket.

### Lifecycle rule

1. Mở bucket và vào tab **Management**.
2. Tạo lifecycle rule tên `delete_old_files`.
3. Áp dụng cho toàn bộ object.
4. Expire current versions sau 90 ngày.
5. Xóa noncurrent versions vĩnh viễn sau 30 ngày.

![Guide](/Workshop/images/5-Workshop/s3-bucket-4.PNG)

### Cấu hình CORS

1. Mở tab **Permissions** của bucket.
2. Chỉnh **Cross-origin resource sharing (CORS)**.
3. Dán chính sách CORS sau đây cho môi trường local:
```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["PUT", "GET", "HEAD"],
    "AllowedOrigins": ["http://localhost:3000"],
    "ExposeHeaders": ["ETag"],
    "MaxAgeSeconds": 3000
  }
]
```
4. Lưu lại.

![Guide](/Workshop/images/5-Workshop/s3-bucket-5.PNG)

### Ghi chú

- Giữ bucket ở chế độ private.
- Luồng upload dùng presigned S3 URL, nên CORS vẫn quan trọng dù hệ thống là serverless.
- Sau này bạn sẽ quay lại đây để thêm origin của frontend đã deploy.

### Kết quả mong đợi

Bucket phải tồn tại, versioning phải bật, encryption phải bật, và CORS phải cho phép upload từ local.
