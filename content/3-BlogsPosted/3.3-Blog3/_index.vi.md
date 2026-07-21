---
title: "Blog 3: Artera và bài toán ứng dụng AWS để tăng tốc chẩn đoán ung thư tuyến tiền liệt"
date: 2026-06-18
weight: 3
chapter: false
pre: " <b> 3.2. </b> "
---

Bài blog từ AWS Architecture Blog giới thiệu cách **Artera** – một công ty trong lĩnh vực y học – xây dựng nền tảng AI phân tích ảnh sinh thiết để dự đoán mức độ nguy hiểm của ung thư tuyến tiền liệt cũng như khả năng đáp ứng điều trị của bệnh nhân. Sản phẩm **ArteraAI Prostate Test** đã được FDA cấp phép De Novo, trở thành phần mềm AI đầu tiên được công nhận cho mục đích này.

## Vấn đề trước khi có AI

Trước đây, việc xác định phác đồ điều trị chủ yếu dựa trên xét nghiệm hóa học đo mức biểu hiện của một số ít gene và tồn tại nhiều hạn chế:

* **Thời gian xử lý kéo dài**: Toàn bộ quy trình có thể mất đến **6 tuần** mới trả kết quả.
* **Khả năng phân tích hạn chế**: Chỉ đánh giá được một số lượng nhỏ gene liên quan đến nguy cơ ung thư.
* **Tiêu hao mẫu sinh thiết**: Mẫu mô bị sử dụng hoàn toàn trong quá trình xét nghiệm, khiến bệnh nhân không còn cơ hội thực hiện thêm các xét nghiệm khác hoặc tham gia thử nghiệm lâm sàng.

Ngoài ra, hệ thống còn gặp nhiều thách thức về kỹ thuật:

* Ảnh sinh thiết có độ phân giải rất lớn, có thể lên tới **8 GB** mỗi ảnh.
* Mỗi ảnh phải được chia thành hàng chục nghìn **image patch** để mô hình AI xử lý.
* Hệ thống phải đáp ứng các yêu cầu bảo mật và tuân thủ dữ liệu y tế như **HIPAA** tại nhiều quốc gia.

## Giải pháp: Kiến trúc AI Inference kết hợp Amazon ECS và Amazon EKS

Để giải quyết các vấn đề trên, Artera xây dựng kiến trúc AI trên AWS với nhiều dịch vụ phối hợp:

* **AWS Global Accelerator** và **Application Load Balancer** tiếp nhận lưu lượng truy cập từ cổng thông tin dành cho bác sĩ và định tuyến vào VPC.
* **Amazon ECS** vận hành web portal phục vụ người dùng.
* **Amazon EKS** đảm nhận toàn bộ workload AI/ML inference để phân tích ảnh sinh thiết bằng mô hình Computer Vision.
* **Amazon EFS** lưu trữ file dùng chung để cả ECS và EKS cùng truy cập trong quá trình xử lý dữ liệu.
* **Amazon RDS** lưu trữ dữ liệu bệnh nhân và kết quả chẩn đoán.
* **Amazon ElastiCache** giảm độ trễ khi truy cập các dữ liệu được sử dụng thường xuyên.
* **Amazon S3** lưu trữ ảnh sinh thiết gốc và kết quả phân tích.
* **AWS IAM** quản lý quyền truy cập người dùng và dịch vụ.
* **AWS KMS** quản lý khóa mã hóa nhằm bảo vệ dữ liệu.
* **Amazon CloudWatch** giám sát toàn bộ hạ tầng và các dịch vụ đang hoạt động.

Một điểm nổi bật của kiến trúc là khả năng giải quyết bài toán **Data Locality**. Nhờ sử dụng **Amazon EFS** trong cùng Region với ứng dụng, Artera có thể triển khai tài nguyên theo từng khu vực địa lý, đảm bảo dữ liệu bệnh nhân luôn được lưu trữ đúng phạm vi pháp lý yêu cầu, đồng thời vẫn có thể mở rộng nhanh sang các thị trường mới.

## Kết quả đạt được

Sau khi triển khai kiến trúc trên AWS, hệ thống đạt được nhiều cải thiện đáng kể:

* **Rút ngắn thời gian trả kết quả** từ khoảng **6 tuần xuống còn 1–2 ngày**.
* **Tăng tốc xử lý ảnh sinh thiết**: hàng chục nghìn image patch cho mỗi lát cắt chỉ mất vài giờ để xử lý thay vì nhiều tuần.
* **Workflow orchestration** giúp chia nhỏ các ảnh có kích thước lớn và xử lý song song trên các cluster Amazon EKS, tối ưu hiệu năng của toàn hệ thống.

## Góc nhìn cá nhân

Điều mình ấn tượng nhất là cách Artera cân bằng giữa ba yếu tố quan trọng của một hệ thống AI trong lĩnh vực y tế:

* Hiệu năng xử lý khối lượng dữ liệu ảnh khổng lồ.
* Tuân thủ các quy định lưu trữ dữ liệu theo từng khu vực địa lý.
* Rút ngắn thời gian trả kết quả để hỗ trợ bác sĩ đưa ra quyết định điều trị nhanh hơn.

Việc kết hợp **Amazon ECS** cho tầng ứng dụng web và **Amazon EKS** cho AI inference là một kiến trúc thực tế rất đáng tham khảo đối với các hệ thống AI xử lý dữ liệu lớn trên nền tảng Cloud.

Nếu quan tâm đến kiến trúc AI trong lĩnh vực y tế hoặc các giải pháp xử lý dữ liệu ảnh quy mô lớn trên AWS, đây là một bài viết rất đáng đọc.

![Solution Diagram](/Workshop/images/3-BlogsTranslated/Blog3.png)

Facebook Post (AWS Study Group - Chờ duyệt - Ngày đăng 18/07/2026)

[Original Post (AWS Architecture Blog)](https://aws.amazon.com/blogs/architecture/how-artera-enhances-prostate-cancer-diagnostics-using-aws/)