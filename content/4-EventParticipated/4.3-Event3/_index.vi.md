---
title: "Meet up - 2026/07/11"
date: 2026-07-11
weight: 3
chapter: false
pre: " <b> 4.3. </b> "
---

![Ảnh](/Workshop/images/4-EventParticipated/Event3.jpg)

### **Diễn giả 1: Nguyễn Huỳnh Sơn**  
#### **Chủ đề:** SLA and Monitoring - From SLA to Monitoring: What Really Matters

### Mục đích chính của bài chia sẻ

- Giúp sinh viên hiểu rõ sự khác biệt giữa hạ tầng “healthy” và trải nghiệm người dùng thực tế.
- Giải thích vai trò của SLA và cách Monitoring hỗ trợ quản trị rủi ro.
- Nhấn mạnh rằng việc chỉ monitor tầng hạ tầng là chưa đủ, cần monitor cả business metrics và user journey.

### Nội dung nổi bật

- **Câu chuyện mở đầu**: AWS Console có thể xanh, server vẫn chạy bình thường, nhưng người dùng vẫn không thể login được.
- **SLA là gì?**: Service Level Agreement – cam kết mức dịch vụ giữa nhà cung cấp và khách hàng. SLA giống như “bảo hành có điều kiện”. AWS chịu trách nhiệm cho dịch vụ của họ, còn trải nghiệm người dùng là trách nhiệm của hệ thống bạn xây dựng.
- **Risk Management**: Monitoring nằm trong quy trình quản trị rủi ro (Identify → Monitor → Respond → Improve). Monitoring giúp phát hiện rủi ro sớm trước khi vi phạm SLA và gây ảnh hưởng đến khách hàng.
- **Khoảng cách giữa Healthy Infrastructure & Happy Users**: 
  - Infrastructure (CPU, Memory, Disk…)
  - Application (Latency, Errors…)
  - Business Metrics (Login success rate, Order success…)
  - Customer Experience (Can login? Can checkout?)

- **Monitoring Pyramid**:
  - Customer Experience (tầng trên cùng)
  - Business Metrics
  - Application
  - Infrastructure
  - Cloud Provider

- **Live Demo**: 
  - Hai endpoint: `/health` (vẫn OK) và `/login` (thất bại khi DB bị chặn).
  - Dashboard “xanh” hoàn toàn ở tầng hạ tầng nhưng người dùng không thể login được.

- **Alerting Flow**: Từ custom metric (LoginFailure) → CloudWatch Alarm → SNS Notification.

### Những gì tôi học được

- Healthy Infrastructure ≠ Happy Users. Server chạy tốt không có nghĩa là người dùng đang sử dụng được hệ thống.
- Chỉ monitor tầng hạ tầng (CPU, Memory…) là chưa đủ. Cần monitor cả business metrics và user journey (Login Success Rate, Order Success…).
- SLA là cam kết của nhà cung cấp, còn trách nhiệm mang lại trải nghiệm tốt cho người dùng thuộc về đội ngũ xây dựng hệ thống.
- Custom metrics + CloudWatch Alarms + SNS là cách hiệu quả để phát hiện và phản ứng kịp thời trước khi khách hàng khiếu nại.
- Monitoring thực sự có giá trị khi nó giúp phát hiện vấn đề trước khi ảnh hưởng đến người dùng cuối.

### **Diễn giả 2: Ngo Le Tan Huy**  
#### **Chủ đề:** Inside The Exam: AWS Cloud Practitioner

### Mục đích chính của bài chia sẻ

- Cung cấp cái nhìn tổng quan và chiến lược ôn thi hiệu quả cho kỳ thi AWS Certified Cloud Practitioner (CLF-C02).
- Giúp sinh viên hiểu rõ cấu trúc đề thi, các domain trọng tâm và cách tư duy để trả lời câu hỏi.
- Chia sẻ kinh nghiệm thực tế, tips & tricks và tài liệu ôn thi hữu ích.

### Nội dung nổi bật

- **Thông tin chung về kỳ thi**:
  - Số câu hỏi: 65 (multiple choice, có thể có nhiều đáp án đúng).
  - Thời gian: 90 phút (người không phải native English được cộng thêm 30 phút).
  - Điểm đậu: 700/1000.
  - Hiệu lực chứng chỉ: 3 năm.

- **Cấu trúc đề thi**:
  - Domain 1: Cloud Concepts (24%)
  - Domain 2: Security and Compliance (30%)
  - Domain 3: Cloud Technology and Services (34%)
  - Domain 4: Billing, Pricing, and Support (12%)

- **Các khái niệm quan trọng**:
  - 6 lợi ích của AWS Cloud.
  - AWS Well-Architected Framework (6 pillars).
  - AWS Cloud Adoption Framework (CAF).
  - Shared Responsibility Model.
  - IAM, Security Groups, NACLs, AWS Shield, WAF, Artifact.
  - Global Infrastructure, Compute, Storage, Database, Networking services.
  - Các mô hình pricing của EC2, công cụ quản lý chi phí, và các gói Support.

- **Tips & Tricks**:
  - Kỹ thuật loại trừ đáp án.
  - Không overthink – chọn đáp án đơn giản nhất.
  - Chú ý từ khóa tiêu cực (Not, Least, Most…).
  - Sử dụng Flag for Review và chuẩn bị tâm lý trước khi thi.

### Những gì tôi học được

- Kỳ thi Cloud Practitioner tập trung vào tư duy tổng quan và use case thực tế chứ không đòi hỏi code hay cấu hình sâu.
- Shared Responsibility Model và AWS Well-Architected Framework là hai nội dung cực kỳ quan trọng.
- Việc hiểu rõ vai trò của từng service và liên hệ với bài toán kinh doanh giúp trả lời câu hỏi tốt hơn.
- Ôn thi hiệu quả không nằm ở việc học thuộc lòng mà nằm ở việc hiểu bản chất và luyện tập phân tích đáp án.
- Chuẩn bị tâm lý, tài liệu và quy trình thi là yếu tố quan trọng để đạt kết quả tốt.

### **Diễn giả 3: Thinh Nguyen**  
#### **Chủ đề:** Securing Your Web Apps With AWS Security Agent

### Mục đích chính của bài chia sẻ

- Giới thiệu giải pháp AWS Security Agent – một AI Agent tự động giúp bảo mật ứng dụng web.
- Làm rõ những hạn chế của phương pháp bảo mật truyền thống (manual pentest).
- Hướng dẫn cách sử dụng Frontier Agent trong toàn bộ vòng đời phát triển ứng dụng (Design → Code → Production).

### Nội dung nổi bật

- **The Security Bottleneck**: Quy trình kiểm tra bảo mật truyền thống tốn thời gian, chi phí cao, kết quả không đồng đều và phụ thuộc nhiều vào con người.
- **Meet the Frontier Agent**: 
  - Tự chủ lập kế hoạch và thực thi (Powered by Amazon Bedrock).
  - Hỗ trợ toàn vòng đời: Design Review, Code Security Review và Automated Penetration Testing.
  - Kết quả có thể kiểm chứng thực tế (thực hiện khai thác lỗ hổng).

- **Các tính năng chính**:
  - **Design Security Review**: Phân tích tài liệu thiết kế và Terraform, kiểm tra theo các chuẩn (PCI DSS, NIST CSF, AWS Well-Architected).
  - **Code Security Review**: Tích hợp trực tiếp vào Pull Request trên GitHub/GitLab, gợi ý fix code tự động.
  - **Automated Pentesting**: Thực hiện chuỗi tấn công phức tạp, xác thực như người dùng thật và cung cấp attack graph chi tiết.

- **Chi phí và thực tế**:
  - Free Trial: 2 tháng, 400 Task-Hours/tháng.
  - Giá: $50/Task-Hour.
  - Case study: Chi phí thực tế thường từ $1,500 – $2,500 cho một dự án.

- **Hạn chế quan trọng**: Khó vượt qua MFA, biometrics, logic flaws, và dễ tốn Task-Hours với ứng dụng phức tạp.

### Những gì tôi học được

- Phương pháp bảo mật truyền thống đang là nút thắt lớn về thời gian và chi phí.
- AWS Security Agent là bước tiến mạnh mẽ, cho phép thực hiện bảo mật tự động, liên tục và có khả năng kiểm chứng thực tế.
- Agent có thể hỗ trợ từ giai đoạn thiết kế đến pentest production, giúp DevSecOps trở nên hiệu quả hơn.
- Dù mạnh mẽ, Agent vẫn có những hạn chế (MFA, business logic flaws…) nên cần kết hợp với quy trình con người.
- Giám sát Task-Hour là rất quan trọng để kiểm soát chi phí khi sử dụng Agent.