---
title: "Blog 1: Kiến trúc Failover Đa Vùng (Multi-Region) cho Event-Driven với Amazon EventBridge và Route 53: Đảm bảo High Availability trên AWS"
date: 2026-06-03
weight: 1
chapter: false
pre: " <b> 3.1. </b> "
---

Bài blog mới từ AWS Compute Blog chia sẻ cách xây dựng kiến trúc failover tự động giữa nhiều Region cho các ứng dụng event-driven, được xây dựng dựa trên Amazon EventBridge, Amazon API Gateway và Amazon Route 53. Đây là giải pháp cực kỳ quan trọng giúp đảm bảo High Availability (HA) và khả năng Disaster Recovery (DR) cho hệ thống.

**Một số điểm đáng chú ý:**

* **Thiết lập mô hình Active-Passive Multi-Region**: Amazon Route 53 sử dụng kiểm tra sức khỏe (health checks) để tự động điều hướng traffic sang region thứ cấp khi region chính gặp sự cố, mà không cần can thiệp thủ công.
* **Đảm bảo tính độc lập theo vùng (Regional Independence)**: Sự kiện được xử lý hoàn toàn tại Region nơi nó được khởi tạo, các region hoạt động độc lập không phụ thuộc lẫn nhau khi bình thường, giúp tối ưu độ trễ (latency).
* **Đồng bộ dữ liệu thời gian thực**: Sử dụng Amazon DynamoDB Global Tables để tự động sao chép dữ liệu giữa các region, đảm bảo không mất mát dữ liệu hoặc gián đoạn khi failover.
* **Triển khai hạ tầng một cách đồng nhất**: Sử dụng AWS SAM và CloudFormation để mô đun hóa stack hạ tầng (API Gateway, EventBridge, SQS, Lambda), giúp dễ dàng nhân bản ra nhiều region.

**Luồng Triển Khai Thực Tế:**

* **Deploy Primary Stack**: Khởi tạo API Gateway, EventBus, Route 53 Health Check với failover routing type là PRIMARY và bảng DynamoDB Global.
* **Deploy Secondary Stack**: Khởi tạo hạ tầng tương tự tại region thứ cấp, đặt Route 53 routing type là SECONDARY và liên kết chung tới bảng DynamoDB Global.
* **Test Event Processing**: Luồng xử lý sự kiện: API Gateway tiếp nhận → EventBridge định tuyến → SQS lưu hàng đợi → Lambda tiêu thụ và xử lý → ghi kết quả vào DynamoDB.
* **Giả lập Tự Động Failover**: Chủ động xóa API Gateway base path/stage ở primary region, đợi khoảng 90 giây để Route 53 health check phát hiện sự cố, sau đó quan sát traffic được tự động điều hướng hoàn toàn sang region thứ cấp.

**Kết Luận:**

Route 53 health-based failover là một công cụ mạnh mẽ mang đến sự linh hoạt tối đa, hỗ trợ tốt cả hai tình huống: bảo trì hệ thống có chủ đích hoặc region bị downtime ngoài ý muốn, phục vụ tốt cho các ứng dụng enterprise.

Những ai đang xây dựng kiến trúc event-driven yêu cầu tính sẵn sàng cao hoặc tìm giải pháp HA/DR đa vùng trên AWS có thể tham khảo hướng tiếp cận này.

![Solution Diagram](/Workshop/images/3-BlogsTranslated/Blog1.png)

[Facebook Post (AWS Study Group)](https://www.facebook.com/photo?fbid=2216858689065550&set=gm.2174291026669191&idorvanity=660548818043427)

[Original Post (AWS Compute Blog)](https://aws.amazon.com/blogs/compute/multi-region-event-driven-failover-architecture-with-amazon-eventbridge-and-route-53/)