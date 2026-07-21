---
title: "Worklog Tuần 12"
date: 2026-07-20
weight: 12
chapter: false
pre: " <b> 1.12. </b> "
---

### Mục tiêu tuần 12:

* Hoàn thành việc triển khai toàn bộ hệ thống ReviewSentinel trên nền tảng AWS.
* Tích hợp đầy đủ các dịch vụ backend, frontend và các thành phần hạ tầng.
* Kiểm thử quy trình xử lý dữ liệu từ đầu đến cuối và hoàn thiện hệ thống trước khi kết thúc dự án.

### Các công việc cần triển khai trong tuần này:

| Công việc | Ngày bắt đầu | Ngày hoàn thành | Nguồn tài liệu |
| --- | ------------ | --------------- | -------------- |
| Triển khai AWS Lambda <br> - Triển khai các Lambda Function: review_processor, sentiment_analyzer và api_handler <br> - Cấu hình IAM Role theo nguyên tắc Least Privilege <br> - Thiết lập Environment Variables và kiểm tra hoạt động của Lambda | 20/07/2026 | 20/07/2026 | AWS Study Group |
| Cấu hình Amazon API Gateway <br> - Tích hợp Amazon Cognito Authorizer <br> - Cấu hình CORS <br> - Triển khai REST API và cấp quyền Invoke Lambda | 20/07/2026 | 20/07/2026 | AWS Study Group |
| Cấu hình Event-driven Architecture <br> - Thiết lập S3 Event Notification kích hoạt Lambda <br> - Cấu hình DynamoDB Streams Trigger <br> - Kiểm tra luồng xử lý dữ liệu tự động | 21/07/2026 | 21/07/2026 | AWS Study Group |
| Triển khai Frontend và kiểm thử hệ thống <br> - Triển khai ứng dụng React lên AWS Amplify <br> - Cấu hình kết nối với API Gateway và Cognito <br> - Thực hiện kiểm thử toàn bộ quy trình và giám sát bằng Amazon CloudWatch | 21/07/2026 | 21/07/2026 | AWS Study Group |

### Kết quả đạt được tuần 12:

* Hoàn thành triển khai các **AWS Lambda Functions** gồm **review_processor**, **sentiment_analyzer** và **api_handler**, đồng thời cấu hình IAM Role và Environment Variables để các hàm có thể hoạt động an toàn và đúng chức năng.

* Hoàn tất cấu hình **Amazon API Gateway** kết hợp với **Amazon Cognito** để xác thực người dùng, thiết lập CORS và triển khai các REST API phục vụ frontend cũng như các chức năng xử lý dữ liệu của hệ thống.

* Xây dựng thành công kiến trúc **Event-driven** bằng cách kết nối **Amazon S3**, **AWS Lambda** và **Amazon DynamoDB Streams**, giúp tự động xử lý dữ liệu đánh giá ngay sau khi người dùng tải tệp lên hệ thống.

* Triển khai ứng dụng **React** trên **AWS Amplify**, tích hợp với Amazon Cognito và API Gateway, đồng thời hoàn thiện cấu hình callback URL, CORS và các biến môi trường để frontend có thể giao tiếp với backend.

* Thực hiện kiểm thử toàn bộ quy trình từ đăng ký, đăng nhập, tải dữ liệu, xử lý đánh giá, phân tích cảm xúc và lưu kết quả vào Amazon DynamoDB. Đồng thời sử dụng **Amazon CloudWatch** để theo dõi Logs, Metrics và kiểm tra trạng thái hoạt động của toàn bộ hệ thống.

* Hoàn thiện dự án **ReviewSentinel**, xây dựng thành công một hệ thống **Serverless** trên AWS, tích hợp các dịch vụ Amazon S3, AWS Lambda, Amazon DynamoDB, Amazon API Gateway, Amazon Cognito, Amazon CloudWatch và AWS Amplify để tạo nên một quy trình xử lý đánh giá sản phẩm hoàn chỉnh từ đầu đến cuối.