---
title: "Xử lý và tích hợp"
date: 2024-01-01
weight: 4
chapter: false
pre: " <b> 5.4. </b> "
---

#### Tổng quan

Phần này tạo IAM role, Lambda function và trigger sự kiện để kết nối lớp dữ liệu với luồng phân tích. Đây là lúc ReviewSentinal bắt đầu hoạt động như một hệ thống thật thay vì chỉ là các tài nguyên rời rạc.

#### Nội dung

1. [IAM role](5.4.1-iam-roles/)
2. [Lambda function](5.4.2-lambda-functions/)
3. [Trigger sự kiện](5.4.3-event-triggers/)

#### Xây dựng lớp xử lý

1. Tạo một IAM role tối thiểu quyền cho từng Lambda function: review processor, sentiment analyzer và API handler.
2. Tạo ba Lambda function và gán đúng role, handler, timeout, memory và biến môi trường.
3. Nối bucket S3 với review processor bằng trigger khi object được tạo.
4. Nối DynamoDB stream của bảng `Reviews` với sentiment analyzer.
5. Chỉ cấp quyền truy cập Secrets Manager cho analyzer và API handler nếu bạn bật luồng OpenRouter tùy chọn.

#### Ghi chú

+ Tách quyền stream ra khỏi quyền bảng. Analyzer đọc DynamoDB stream nên cần quyền ở mức stream ngoài quyền truy cập bảng.
+ Dùng DLQ cho xử lý lỗi bất đồng bộ để event lỗi không bị mất âm thầm.
+ Nếu bật bước phân tích sâu, hãy lưu raw key trong Secrets Manager và đọc nó lúc runtime.
