---
title: "5.5.2 Giám sát và cảnh báo"
weight: 2
---

# Giám sát và cảnh báo

## Tổng quan

Trong phần này, bạn sẽ thiết lập hệ thống giám sát (Monitoring) để theo dõi tình trạng hoạt động của ReviewSentinal.

Bạn sẽ tạo **CloudWatch Dashboard** cùng các **CloudWatch Alarm** nhằm giám sát các Lambda function, API và hoạt động của DynamoDB.

### Những thành phần cần tạo

- CloudWatch Dashboard
- CloudWatch Alarm cho lỗi của Lambda
- CloudWatch Alarm cho độ trễ của API
- Widget theo dõi hoạt động của DynamoDB

### Các chỉ số quan trọng

- Lambda `Errors`
- Lambda `Duration`
- DynamoDB `ConsumedWriteCapacityUnits`
- API `Latency`

## Các bước thực hiện

### 1. Tạo CloudWatch Dashboard

1. Mở **Amazon CloudWatch** → **Dashboards**.
2. Chọn **Create dashboard**.
3. Đặt tên dashboard `ReviewAnalyzerDashboard`.

![Guide](/Workshop/images/5-Workshop/monitor-1.PNG)

4. Thêm một widget **Metrics → Metrics console → Line** cho ba Lambda function.
5. Thêm các metric:
   - `Invocations`
   - `Errors`
   - `Duration`

![Guide](/Workshop/images/5-Workshop/monitor-2.PNG)

![Guide](/Workshop/images/5-Workshop/monitor-3.PNG)

![Guide](/Workshop/images/5-Workshop/monitor-4.PNG)

6. Thêm widget thứ hai với loại **Metrics → Metrics console → Data table** cho DynamoDB.
7. Thêm metric `ConsumedWriteCapacityUnits` của bảng `Reviews`.

![Guide](/Workshop/images/5-Workshop/monitor-5.PNG)

8. Thêm widget **Logs → Line query** để thống kê số lượng thông báo lỗi theo thời gian.

```sql
SOURCE logGroups(namePrefix: [], class: "STANDARD") START=-604800s END=0s |
filter @message like /(?i)error/
| stats count(*) as errorCount by bin(5m)
```

9. Lưu Dashboard.

![Guide](/Workshop/images/5-Workshop/monitor-6.PNG)

### 2. Tạo Alarm cho lỗi của từng Lambda

1. Mở **Amazon CloudWatch** → **Alarms** → **All alarms**.
2. Tạo Alarm cho Lambda `review-sentiment-analyzer-processor`.
3. Giới hạn Alarm theo đúng tên Lambda function.
4. Thiết lập:
   - Period: **5 minutes**
   - Điều kiện kích hoạt: **Errors > 5**


![Guide](/Workshop/images/5-Workshop/monitor-7.PNG)

![Guide](/Workshop/images/5-Workshop/monitor-8.PNG)

5. Gửi thông báo đến địa chỉ email đã xác minh của bạn. (Tạo một SNS Topic mới và sử dụng Topic này cho các Alarm còn lại.)

![Guide](/Workshop/images/5-Workshop/monitor-9.PNG)

6. Lặp lại các bước trên cho Lambda `review-sentiment-analyzer-analyzer`.
7. Tiếp tục lặp lại cho Lambda `review-sentiment-analyzer-api`.

![Guide](/Workshop/images/5-Workshop/monitor-10.PNG)

### 3. Tạo Alarm cho độ trễ của API

1. Tạo Alarm cho Lambda `review-sentiment-analyzer-api`.
2. Chọn metric `Duration`.
3. Thiết lập:
   - Statistic: **Average**
   - Period: **5 minutes**
4. Kích hoạt Alarm khi `Duration` lớn hơn **5000 ms**.
5. Gửi thông báo đến địa chỉ email đã xác minh của bạn.

![Guide](/Workshop/images/5-Workshop/monitor-11.PNG)

### 4. Tạo cảnh báo ngân sách (Budget Alerts)

1. Mở **Billing and Cost Management** → **Budgets**.
2. Tạo **Monthly Cost Budget**.
3. Tạo **Daily Cost Budget**.
4. Thiết lập cảnh báo tại:
   - 80% chi phí thực tế (Actual Spend)
   - 100% chi phí dự báo (Forecasted Spend)
5. Sử dụng địa chỉ email của bạn để nhận thông báo.

![Guide](/Workshop/images/5-Workshop/monitor-13.PNG)

### Lưu ý

1. Mỗi Lambda Alarm cần được cấu hình cho **từng Lambda function cụ thể**, không sử dụng metric chung của toàn bộ dịch vụ Lambda.
2. **Sử dụng thông báo qua email trực tiếp bằng Amazon SES thay vì SNS Topic** để gửi cảnh báo.
3. Giữ các widget trên Dashboard đơn giản để dễ theo dõi trong quá trình kiểm thử và xác thực hệ thống.

### Kết quả mong đợi

Sau khi hoàn thành:

- Bạn có thể mở **CloudWatch Dashboard** để theo dõi tình trạng hoạt động của toàn bộ hệ thống.
- Các CloudWatch Alarm sẽ tự động theo dõi lỗi và hiệu năng của Lambda cũng như API.
- Cảnh báo về chi phí AWS sẽ được gửi khi vượt các ngưỡng đã cấu hình.
- Thông báo cảnh báo sẽ được gửi trực tiếp qua email bằng **Amazon SES** thay vì thông qua SNS.