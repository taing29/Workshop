---
title: "5.3.2 DynamoDB tables"
weight: 2
---

# Các bảng DynamoDB cho ReviewSentinal

## Tổng quan

Tạo bốn bảng lưu review, sản phẩm, người dùng và theo dõi các công việc phân tích. Bảng `Reviews` là bảng chính và cần stream cùng GSI.

### Các bảng cần tạo

- `Analyses`
- `Reviews`
- `Products`
- `Users`

### Bảng Analyses

1. Mở DynamoDB và chọn **Create table**.
2. Tên bảng: `Analyses`.
3. Partition:analysisAustin
3. Khóa **On-demand**.
5. Để Default encryption key do DynamoDB quản lý5. Tạo t1. Mở 3.6. Chọn **Customize**.
7. Đặt capacity là **On-demand**.
8. Để encryption theo key do DynamoDB quản lý mặc định.
9. Tạo bảng.

### Bảng Reviews

1. Mở DynamoDB và chọn **Create table**.
2. Tên bảng: `Reviews`.
3. Khóa phân vùng: `ProductID` kiểu String.
4. Khóa sắp xếp: `ReviewID` kiểu String.
5. Chọn **Customize**.
6. Đặt capacity là **On-demand**.
7. Để encryption theo key do DynamoDB quản lý mặc định.
8. Tạo bảng.

Sau khi tạo xong:

1. Mở bảng `Reviews`.
2. Bật **DynamoDB Streams** ở tab **Exports and streams**.
3. Chọn stream view type là **New image**.
4. Vào tab **Backups** và bật **Point-in-time recovery**.
5. Tạo GSI tên `SentimentIndex`.
6. Dùng `ProductID` làm partition key và `Sentiment` làm sort key.
7. Chỉ project các thuộc tính `ReviewText`, `Rating`, `CreatedAt`, `KeyPhrases`, và `UserID`.
8. **Cập nhật tăng dần (không cần sửa đổi dữ liệu hiện có)**: Khi đặt mục mới, bao gồm thuộc tính `AnalysisID` (là thuộc tính thường, không phải phần của khóa).
9. **Tạo GSI cho truy vấn phân tích**: Tạo chỉ mục phụ.global lần tên `AnalysisIndex` trên bảng `Reviews`:
   - Khóa phân vùng: `AnalysisID` (String)
   - Khóa sắp xếp: Để trống (hoặc sử dụng `ReviewID` nếu cần sắp xếp trong phân tích)
   - Thuộc tính đượcฉาย: `KEYS_ONLY` (hoặc `ALL` nếu cần cho các truy vấn của bạn)

### Bảng Products

1. Tạo bảng tên `Products`.
2. Dùng `ProductID` làm partition key.
3. Không dùng sort key.
4. Chọn **On-demand**.
5. Bật point-in-time recovery sau khi tạo.

### Bảng Users

1. Tạo bảng tên `Users`.
2. Dùng `UserID` làm partition key.
3. Không dùng sort key.
4. Chọn **On-demand**.
5. Bật point-in-time recovery sau khi tạo.

### Ghi chú

- Stream của bảng `Reviews` cần cho trigger của Lambda sentiment analyzer.
- Giữ đúng tên bảng vì biến môi trường và IAM policy phía sau sẽ tham chiếu trực tiếp.
- GSI được giữ tối giản để chỉ trả chi phí cho những gì code thực sự dùng.
- Thuộc tính `AnalysisID` trong `Reviews` là additive - nó không thay đổi cấu trúc bảng hiện có, vì vậy dữ liệu hiện tại không bị ảnh hưởng.

### Kết quả mong đợi

Bốn bảng phải tồn tại: `Analyses`, `Reviews`, `Products`, và `Users`.
- Bảng `Reviews` và `Analyses` phải bật streams (cho `Reviews` - cần cho trigger Lambda)
- Tất cả bảng phải là on-demand với bật point-in-time recovery
- Bảng `Reviews` có:
  * Khóa chính gốc (ProductID, ReviewID)
  * GSIs: `SentimentIndex` và `AnalysisIndex`
  * Các mục bao gồm thuộc tính `AnalysisID` (được thêm vào)
