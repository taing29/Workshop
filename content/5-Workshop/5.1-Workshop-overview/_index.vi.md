---
title: "Tổng quan workshop"
date: 2024-01-01
weight: 1
chapter: false
pre: " <b> 5.1. </b> "
---

# Tổng Quan Workshop ReviewSentinal

ReviewSentinal là một ứng dụng AWS serverless được thiết kế để nhập và phân tích các bài đánh giá sản phẩm bằng cách sử dụng các dịch vụ AWS native. Ứng dụng nhập các bài đánh giá sản phẩm, lưu trữ chúng trong DynamoDB, thực hiện phân tích cảm xúc bằng Amazon Comprehend, và tùy chọn tăng cường các insight bằng phân tích OpenRouter/LLM. Kết quả được cung cấp thông qua các endpoint API an toàn và có thể được trực quan hóa thông qua bảng điều khiển React.

## Các Thành Phần Chính

**Lưu Trữ & Sự Kiện**
- **S3 Buckets**: Lưu trữ tải lên bài đánh giá thô với cấu hình CORS cho tải lên trực tiếp từ trình duyệt
- **DynamoDB**: Mô hình thiết kế bảng đơn với ba bảng logic (Reviews, Products, Users) sử dụng khóa phân vùng dựa trên tên người dùng và nhiều chỉ mục GSI
- **SQS**: Hàng đợi chữ không được gửi (`lambda-dlq`) để xử lý lỗi không đồng bộ
- **Secrets Manager**: Lưu trữ tùy chọn cho khóa API OpenRouter để phân tích LLM nâng cao

**Lớp Xử Lý**
- **Ba Hàm Lambda** (tất cả Python 3.11, x86_64, chia sẻ cùng gói triển khai):
  1. **Review Processor** (`review-sentiment-analyzer-processor`): Xử lý tải lên S3, ghi các bản ghi bài đánh giá ban đầu vào DynamoDB
  2. **Sentiment Analyzer** (`review-sentiment-analyzer-analyzer`): Xử lý luồng DynamoDB, chạy phân tích cảm xúc Comprehend, tăng cường OpenRouter tùy chọn, gửi thông báo SES
  3. **API Handler** (`review-sentiment-analyzer-api`): Phục vụ các yêu cầu API REST và email tóm tắt hàng ngày theo lịch

**Lớp Truy Cập & Bảo Mật**
- **API Gateway**: REST API với giai đoạn `dev`, tài nguyên được bật CORS cho các endpoint products, reviews, uploads, và analysis
- **Cognito**: Nhóm người dùng và ứng dụng khách cho xác thực, với các trigger Lambda cho các luồng tùy chỉnh nếu cần
- **WAF**: AWS WAF khu vực cho bảo vệ API Gateway (được đề cập trong ghi chú giám sát)
- **Mã Hóa**: Mã hóa KMS cho dữ liệu khi lưu trữ ở nơi có thể áp dụng

**Giám Sát & Khả Quan Sát**
- **CloudWatch Dashboard**: `ReviewAnalyzerDashboard` với các chỉ số cho lệnh gọi Lambda, lỗi, thời lượng và tiêu thụ DynamoDB
- **CloudWatch Alarms**: Cảnh báo lỗi cho mỗi hàm (>5 lỗi/5 phút) và cảnh báo độ trễ API (>5000ms thời lượng)
- **Logs Insights**: Truy vấn theo dõi lỗi
- **Budget Alerts**: Ngân sách chi phí hàng tháng và hàng ngày với thông báo ngưỡng 80%/100%
- **Thông Báo SES Trực Tiếp**: Thông báo báo động được gửi trực tiếp qua SES (bỏ qua SNS)

## Sơ Đồ Kiến Trúc

![ReviewSentinal Architecture](/Workshop/images/2-Proposal/architecture-diagram.png)

## Luồng Workshop

Workshop này tuân theo một quy trình triển khai ứng dụng serverless hoàn chỉnh:

1. **Tổng Quan Workshop** - Hiểu kiến trúc và các thành phần của ReviewSentinal
2. **Điều Kiện Tiên Quyết & Thiết Lập** - Cấu hình tài khoản AWS, cài đặt công cụ (AWS CLI, Node.js), ghi lại ID tài khoản và khu vực (`ap-southeast-1`)
3. **Cơ Sở Hạ Tầng Cốt Lõi** - Tạo tài nguyên nền tảng:
   - Bucket S3 cho tải lên bài đánh giá thô (với CORS)
   - Bảng DynamoDB (Reviews, Products, Users) với các luồng và PITR được bật
   - Cấu hình SES cho thông báo email
   - Hàng đợi dead letter SQS
   - Trình giữ chỗ Secrets Manager cho khóa API OpenRouter (tùy chọn)
4. **Xử Lý & Tích Hợp** - Xây dựng logic xử lý:
   - Tạo vai trò IAM có đặc quyền tối thiểu cho mỗi hàm Lambda
   - Triển khai ba hàm Lambda từ gói `01_lambda_functions.py` được chia sẻ
   - Cấu hình kích hoạt S3→Processor (ObjectCreated)
   - Cấu hình kích hoạt DynamoDB Stream→Analyzer
   - Cấu hình DLQ cho tất cả các hàm Lambda
   - Cấu hình truy cập bí mật OpenRouter tùy chọn cho các hàm analyzer và API
5. **Xác Thực & Hoạt Động** - Cấu hình các thành phần hướng đến người dùng và giám sát:
   - Tạo nhóm người dùng Cognito và ứng dụng khách
   - Cấu hình tài nguyên và phương thức API Gateway (products, reviews, uploads, analysis)
   - Bật CORS và triển khai giai đoạn `dev`
   - Triển khai bảng điều khiển CloudWatch với các widget Lambda và DynamoDB
   - Cấu hình cảnh báo lỗi Lambda và cảnh báo độ trễ API (thông báo SES trực tiếp)
   - Thiết lập cảnh báo ngân sách chi phí
6. **Xác Thực Frontend** - Xây dựng và kiểm tra bảng điều khiển React:
   - Cấu hình với URL API được triển khai và cài đặt Cognito
   - Kiểm tra luồng tải lên bài đánh giá → phân tích → trực quan hóa
7. **Dọn Dẹp** - Phần tùy chọn để loại bỏ tài nguyên nhằm tránh chi phí liên tục

## Những Gì Bạn Sẽ Học

**Mẫu Cơ Sở Hạ Tầng Dưới Dạng Mã**
- Quy ước đặt tên tài nguyên AWS cho tham chiếu ARN có thể dự đoán
- Thiết kế vai trò IAM có đặc quyền tối thiểu cho các hàm Lambda
- Thiết kế bảng đơn DynamoDB với các chiến lược GSI
- Cấu hình bucket S3 cho tải lên trực tiếp từ trình duyệt an toàn

**Mẫu Ứng Dụng Serverless**
- Xử Lý Đồng Bộ/Không Đồng Bộ
  - Xử lý đồng bộ được kích hoạt S3 (tiếp nhận bài đánh giá)
  - Xử lý không đồng bộ được kích hoạt DynamoDB Stream (phân tích cảm xúc)
  - Xử lý đồng bộ được kích hoạt API Gateway (truy vấn người dùng)
- Triển khai Dead Letter Queue để xử lý lỗi
- Các mẫu tăng cường tùy chọn (Comprehend → dự phòng OpenRouter)

**Tích Hợp Dịch Vụ AWS**
- Amazon Comprehend để phân tích xử lý ngôn ngữ tự nhiên cảm xúc
- Amazon SES cho thông báo email giao dịch (tóm tắt hoàn thành xử lý)
- Amazon Cognito cho xác thực và ủy quyền người dùng
- API Gateway cho các API REST an toàn, có phiên bản
- CloudWatch để quan sát (chỉ số, nhật ký, cảnh báo, bảng điều khiển)

**Sự Xuất Sắc Hoạt Động**
- Ghi nhật ký có cấu trúc và theo dõi lỗi với CloudWatch Logs Insights
- Phạm vi cảnh báo thích hợp (chỉ số dành riêng cho hàm so với dịch vụ)
- Thông báo SES trực tiếp cho cảnh báo hoạt động (tránh chi phí SNS)
- Giám sát chi phí và cảnh báo ngân sách cho chi phí máy chủ có thể dự đoán
- Thiết kế bảng điều khiển để hiển thị hoạt động

**Phát Triển Toàn Ngăn Xếp Serverless**
- Backend: Các hàm Lambda với gói triển khai được chia sẻ
- Cơ Sở Hạ Tầng: Tài nguyên AWS có thể tiêu thụ với các ranh giới rõ ràng
- Frontend: Bảng điều khiển React tiêu thụ các API an toàn
- Xác Thực: Kiểm tra từ đầu đến cuối từ tải lên đến trực quan hóa

Workshop này minh họa cách xây dựng một ứng dụng serverless sẵn sàng cho sản xuất, tiết kiệm chi phí để xử lý nội dung do người dùng tạo ra với các insight được tăng cường bằng AI trong khi duy trì bảo mật, khả năng quan sát và các thực tiễn tốt nhất hoạt động.