---
title: "5.5.2 Monitoring"
weight: 2
---

# Monitoring và alarm

## Tổng quan

Thêm lớp quan sát để giữ cho quá trình triển khai luôn đúng trạng thái. Trang này gom dashboard CloudWatch và các alarm theo dõi hành vi của Lambda và API.

### Những gì cần tạo

- CloudWatch dashboard
- Lambda error alarm
- API latency alarm
- Widget theo dõi DynamoDB

### Chỉ số hữu ích

- Lambda `Errors`
- Lambda `Duration`
- DynamoDB consumed capacity
- API latency

## Từng bước

### 1. Tạo dashboard

1. Mở CloudWatch → **Dashboards**.
2. Chọn **Create dashboard**.
3. Đặt tên `ReviewAnalyzerDashboard`.
4. Thêm widget dạng line cho ba Lambda function.
5. Bao gồm `Invocations`, `Errors`, và `Duration`.
6. Thêm widget cho DynamoDB table metrics.
7. Thêm log query widget để đếm lỗi.
8. Lưu dashboard.

### 2. Tạo alarm lỗi theo từng function

1. Mở CloudWatch → **Alarms** → **All alarms**.
2. Tạo alarm cho processor.
3. Lặp lại cho analyzer.
4. Lặp lại cho API.
5. Mỗi alarm phải gắn đúng function name.
6. Dùng chu kỳ 5 phút và ngưỡng trên 5 lỗi.
7. **Gửi notification qua địa chỉ email SES đã xác minh** (thay thế SNS topic bằng email SES trực tiếp).

### 3. Tạo alarm độ trễ API

1. Tạo alarm cho `review-sentiment-analyzer-api`.
2. Chọn metric `Duration`.
3. Dùng average 5 phút.
4. Trigger nếu lớn hơn 5000 ms.
5. **Gửi notification qua địa chỉ email SES đã xác minh** (thay thế SNS topic bằng email SES trực tiếp).

### 4. Tạo budget alerts

1. Mở Billing and Cost Management → **Budgets**.
2. Tạo budget tháng.
3. Tạo budget ngày.
4. Thêm threshold ở 80% actual spend và 100% forecasted spend.
5. Dùng email của bạn làm subscriber.

### Ghi chú

1. Gắn alarm Lambda theo từng function cụ thể, không dùng metric chung của service.
2. **Dùng email SES trực tiếp cho thông báo alarm thay vì SNS topic**.
3. Giữ widget đơn giản để dashboard dễ đọc trong giai đoạn kiểm tra.

### Kết quả mong đợi

Bạn sẽ mở dashboard và xác nhận stack đang ở trạng thái ổn định trước khi chạy các bước kiểm tra cuối cùng. Thông báo alarm sẽ đến trực tiếp từ SES thay qua SNS topic.
