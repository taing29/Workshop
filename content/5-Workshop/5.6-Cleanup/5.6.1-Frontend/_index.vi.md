---
title: "5.6.1 Dọn dẹp frontend"
weight: 1
---

# Dọn dẹp frontend

## Tổng quan

Xóa frontend đã triển khai trước để người dùng không còn điểm vào công khai cho ứng dụng workshop.

### Những gì cần xóa

- Amplify app hoặc static hosting deployment
- Cấu hình custom domain nếu bạn đã tạo
- Build artifact của frontend nếu đã upload thủ công

## Từng bước

1. Mở Amplify console.
2. Chọn app frontend của ReviewSentinal.
3. Xóa app từ console.
4. Nếu đã thêm custom domain, hãy gỡ domain association.
5. Nếu dùng hosted zone DNS riêng, chỉ giữ lại khi bạn còn cần domain đó cho mục đích khác.

## Ghi chú

1. Xóa frontend trước backend để không còn người dùng nào tiếp tục gọi ứng dụng trong lúc các phần khác đang bị gỡ.
2. Nếu đã cấu hình custom domain, hãy gỡ luôn liên kết DNS trong bước dọn dẹp frontend.

## Kết quả mong đợi

Sau bước này, điểm truy cập trình duyệt của ReviewSentinal không còn khả dụng.
