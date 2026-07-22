---
title: "5.3.2 Bảng DynamoDB"
weight: 2
---

# Tạo các bảng DynamoDB cho ReviewSentinal

## Tổng quan

Trong phần này, bạn sẽ tạo bốn bảng DynamoDB dùng để lưu trữ dữ liệu phân tích, đánh giá sản phẩm, thông tin sản phẩm và người dùng.

Bảng `Reviews` là bảng chính của hệ thống và cần được cấu hình thêm **DynamoDB Streams** cùng với **Global Secondary Index (GSI)**. Ngoài ra, bảng `Analyses` được sử dụng để theo dõi trạng thái và thông tin của các tác vụ phân tích.

## Các bảng cần tạo

- `Analyses`
- `Reviews`
- `Products`
- `Users`

## Tạo bảng Analyses

1. Mở dịch vụ **Amazon DynamoDB** và chọn **Create table**.
2. Nhập tên bảng: `Analyses`.
3. Thiết lập **Partition key**:
   - `AnalysisID`
   - Kiểu dữ liệu: **String**
4. Chọn **Customize**.
5. Chọn chế độ dung lượng **On-demand**.
6. Giữ nguyên tùy chọn mã hóa mặc định (**DynamoDB-managed key**).
7. Chọn **Create table**.

![Guide](/Workshop/images/5-Workshop/dynamodb-1.PNG)

## Tạo bảng Reviews

1. Mở **Amazon DynamoDB** và chọn **Create table**.
2. Nhập tên bảng: `Reviews`.
3. Thiết lập **Partition key**:
   - `ProductID`
   - Kiểu dữ liệu: **String**
4. Thiết lập **Sort key**:
   - `ReviewID`
   - Kiểu dữ liệu: **String**
5. Chọn **Customize**.
6. Chọn chế độ dung lượng **On-demand**.
7. Giữ nguyên tùy chọn mã hóa mặc định (**DynamoDB-managed key**).
8. Chọn **Create table**.

![Guide](/Workshop/images/5-Workshop/dynamodb-2.PNG)

### Cấu hình sau khi tạo bảng

#### Bật DynamoDB Streams

1. Mở bảng `Reviews`.
2. Chuyển sang tab **Exports and streams**.
3. Bật **DynamoDB Streams**.
4. Chọn **New image** làm **Stream view type**.

![Guide](/Workshop/images/5-Workshop/dynamodb-3.PNG)

#### Bật Point-in-Time Recovery (PITR)

1. Chuyển sang tab **Backups**.
2. Bật **Point-in-time recovery**.

![Guide](/Workshop/images/5-Workshop/dynamodb-4.PNG)

#### Tạo Global Secondary Index (GSI)

1. Chuyển sang tab **Indexes**.

##### GSI 1: SentimentIndex

Tạo Global Secondary Index có tên **SentimentIndex** với cấu hình:

- **Partition key:** `ProductID` (String)
- **Sort key:** `Sentiment`

![Guide](/Workshop/images/5-Workshop/dynamodb-5.PNG)

- **Projected attributes:**
  - `ReviewText`
  - `Rating`
  - `CreatedAt`
  - `KeyPhrases`
  - `UserID`

![Guide](/Workshop/images/5-Workshop/dynamodb-6.PNG)

##### GSI 2: AnalysisIndex

Tạo Global Secondary Index có tên **AnalysisIndex** với cấu hình:

- **Partition key:** `AnalysisID` (String)
- **Sort key:** Để trống (hoặc sử dụng `ReviewID` nếu cần sắp xếp các review trong cùng một phiên phân tích)

![Guide](/Workshop/images/5-Workshop/dynamodb-7.PNG)

- **Projected attributes:**
  - `KEYS_ONLY` (hoặc `ALL` nếu ứng dụng của bạn cần truy xuất toàn bộ dữ liệu)

![Guide](/Workshop/images/5-Workshop/dynamodb-8.PNG)

## Tạo bảng Products

1. Tạo bảng có tên `Products`.
2. Sử dụng `ProductID` làm **Partition key**.
3. Không sử dụng **Sort key**.
4. Chọn chế độ dung lượng **On-demand**.
5. Sau khi tạo bảng, bật **Point-in-time recovery**.

## Tạo bảng Users

1. Tạo bảng có tên `Users`.
2. Sử dụng `UserID` làm **Partition key**.
3. Không sử dụng **Sort key**.
4. Chọn chế độ dung lượng **On-demand**.
5. Sau khi tạo bảng, bật **Point-in-time recovery**.

## Lưu ý

- **DynamoDB Streams** của bảng `Reviews` là bắt buộc để kích hoạt Lambda thực hiện phân tích cảm xúc (Sentiment Analysis) mỗi khi có review mới.
- Giữ nguyên chính xác tên các bảng vì các bước cấu hình tiếp theo (Environment Variables và IAM Policies) sẽ tham chiếu trực tiếp đến các tên này.
- Các **Global Secondary Index (GSI)** được thiết kế tối giản nhằm giảm chi phí lưu trữ và truy vấn, chỉ bao gồm những thuộc tính mà ứng dụng thực sự sử dụng.
- Thuộc tính `AnalysisID` trong bảng `Reviews` chỉ là một thuộc tính bổ sung do ứng dụng thêm vào khi ghi dữ liệu. Việc này **không làm thay đổi schema hiện có** của bảng nên sẽ không ảnh hưởng đến dữ liệu đã tồn tại.

## Kết quả mong đợi

Sau khi hoàn thành, bạn sẽ có bốn bảng DynamoDB:

- `Analyses`
- `Reviews`
- `Products`
- `Users`

Trong đó:

- Tất cả các bảng đều sử dụng chế độ **On-demand**.
- Tất cả các bảng đều đã bật **Point-in-time recovery (PITR)**.
- Bảng `Reviews` đã được cấu hình:
  - Khóa chính:
    - `ProductID` (Partition key)
    - `ReviewID` (Sort key)
  - Hai Global Secondary Index:
    - `SentimentIndex`
    - `AnalysisIndex`
  - DynamoDB Streams với chế độ **New image**
  - Mỗi bản ghi review sẽ có thêm thuộc tính `AnalysisID` do ứng dụng tự động thêm vào khi thực hiện phân tích.