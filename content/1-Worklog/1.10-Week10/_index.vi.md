---
title: "Worklog Tuần 10"
date: 2026-07-06
weight: 10
chapter: false
pre: " <b> 1.10. </b> "
---

### Mục tiêu tuần 10:

* Tìm hiểu dịch vụ AWS Managed Microsoft AD và cách triển khai môi trường Active Directory trên AWS.
* Thực hành xây dựng các tác vụ tự động hóa bằng AWS Lambda kết hợp với IAM và EC2.
* Làm quen với việc giám sát tài nguyên AWS bằng Amazon CloudWatch và Grafana.

### Các công việc cần triển khai trong tuần này:

| Công việc | Ngày bắt đầu | Ngày hoàn thành | Nguồn tài liệu |
| --- | ------------ | --------------- | -------------- |
| Tìm hiểu AWS Managed Microsoft AD <br> - Triển khai AWS Managed Directory Service <br> - Tạo và cấu hình Amazon EC2 <br> - Kiểm tra khả năng giao tiếp giữa các máy chủ (Server Communication) | 06/07/2026 | 06/07/2026 | <https://000095.awsstudygroup.com/> |
| Tìm hiểu AWS Lambda <br> - Tạo VPC, Security Group, EC2 và Incoming Webhooks với Slack <br> - Gắn Tag cho EC2 Instance <br> - Tạo IAM Role cho Lambda <br> - Xây dựng Lambda Function để tự động Start/Stop EC2 <br> - Kiểm tra kết quả thực thi | 07/07/2026 | 07/07/2026 | <https://000022.awsstudygroup.com/> |
| Tìm hiểu Amazon CloudWatch và Grafana <br> - Tạo VPC, Subnets, Security Group, EC2, IAM User và IAM Role <br> - Gán IAM Role cho EC2 <br> - Cài đặt Grafana <br> - Thực hành giám sát tài nguyên AWS bằng Grafana | 08/07/2026 | 08/07/2026 | <https://000029.awsstudygroup.com/> |

### Kết quả đạt được tuần 10:

* Hiểu quy trình triển khai AWS Managed Microsoft AD, cấu hình Amazon EC2 và kiểm tra khả năng giao tiếp giữa các máy chủ trong cùng môi trường mạng trên AWS.
* Thực hành xây dựng AWS Lambda Function để tự động hóa việc khởi động và dừng EC2, đồng thời nắm được cách sử dụng IAM Role, VPC và Security Group nhằm đảm bảo Lambda có quyền truy cập phù hợp đến các tài nguyên AWS.
* Làm quen với việc tích hợp AWS Lambda cùng Slack Webhooks để hỗ trợ tự động hóa và gửi thông báo khi thực hiện các tác vụ quản trị.
* Thực hành cài đặt và cấu hình Grafana kết hợp với Amazon CloudWatch để trực quan hóa dữ liệu, theo dõi hiệu năng hệ thống và giám sát trạng thái hoạt động của các tài nguyên AWS thông qua Dashboard.
* Nâng cao kỹ năng triển khai, quản trị và giám sát hạ tầng AWS bằng cách kết hợp nhiều dịch vụ như Directory Service, Lambda, CloudWatch, IAM và Grafana trong cùng một môi trường thực hành.