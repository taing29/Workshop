---
title: "5.5.3 Kiểm tra Frontend"
weight: 3
---

# Kiểm tra Frontend

## Tổng quan

Trong phần này, bạn sẽ sử dụng các tài nguyên backend đã triển khai để cấu hình và kiểm tra frontend của ReviewSentinal.

Mục tiêu là xác nhận frontend đã được kết nối chính xác với các dịch vụ AWS, bao gồm Amazon Cognito, API Gateway và Amazon S3.

### Những nội dung cần kiểm tra

- API URL trỏ đúng đến API Gateway
- Cognito Authority và App Client ID được cấu hình chính xác
- Callback URL và Sign-out URL khớp với domain của frontend
- Chức năng tải tệp lên Amazon S3 hoạt động bình thường

## Các bước thực hiện

### 1. Tạo ứng dụng Amplify

1. Mở **Amazon Amplify** và chọn **Create new app**.
2. Chọn **Deploy without a Git provider**.

![Guide](/Workshop/images/5-Workshop/frontend-1.PNG)

3. Đặt tên ứng dụng `review-sentiment-analyzer-frontend`.
4. Đặt **Environment name** là `production`.
5. Triển khai một trang placeholder đơn giản để Amplify tạo domain mặc định.

```bash
echo "<h1>Coming soon</h1>" > index.html
7z a placeholder.zip index.html
```

![Guide](/Workshop/images/5-Workshop/frontend-2.PNG)

Sau đó triển khai bằng:

- **Method:** Drag and drop
- **Choose .zip folder**
- Chọn `placeholder.zip`
- Chọn **Save and deploy**

6. Sau khi triển khai thành công, ghi lại **Default domain** của ứng dụng (ví dụ: `https://production.dXXXXXXXXXXXXX.amplifyapp.com`).

### 2. Cấu hình SPA Routing

1. Mở **Amplify Console** → ứng dụng của bạn → **Hosting** → **Rewrites and redirects** → **Add rewrite**.

```json
{
  "source": "/<*>",
  "status": "404-200",
  "target": "/index.html"
}
```

2. Chọn **Save**.

![Guide](/Workshop/images/5-Workshop/frontend-3.PNG)

URL công khai của ứng dụng sẽ có dạng:

`https://<branch>.<app-id>.amplifyapp.com`

### 3. (Tùy chọn) Sử dụng tên miền riêng

Nếu bạn sở hữu hoặc dự định đăng ký một tên miền riêng, Amplify có thể quản lý tên miền trực tiếp thông qua **Amazon Route 53**.

Amplify sẽ tự động tạo và quản lý:

- CloudFront Distribution
- Chứng chỉ SSL (AWS Certificate Manager)

Bạn không cần cấu hình thủ công.

#### Điều kiện

Tên miền phải nằm trong **Route 53 Public Hosted Zone** của cùng tài khoản AWS.

Nếu tên miền được đăng ký ở nhà cung cấp khác:

1. Mở **Route 53** → **Hosted zones** → **Create hosted zone**.
2. Nhập tên miền.
3. Chọn **Public hosted zone**.
4. Sao chép bốn bản ghi NS được tạo.
5. Thay thế Nameserver tại nhà đăng ký tên miền bằng các bản ghi này.
6. Chờ DNS cập nhật.

Có thể kiểm tra bằng:

```bash
nslookup -type=NS yourdomain.com 8.8.8.8
```

Sau khi Hosted Zone hoạt động:

7. Mở **Amplify** → **App settings** → **Domain management** → **Add domain**.
8. Nhập tên miền.
9. Amplify sẽ tự động phát hiện Hosted Zone.
10. Chọn branch cần ánh xạ.
11. Chọn **Save**.

Đợi trạng thái chuyển từ **Pending verification** sang **Available**.

#### Cập nhật Cognito

1. Mở **Applications → App clients → review-sentiment-analyzer-client → Login pages → Managed login pages configuration → Edit**.
2. Thêm Callback URL `https://<your-custom-domain>/callback`.
3. Thêm Sign-out URL `https://<your-custom-domain>/logout`.
4. Giữ nguyên các URL `localhost` và `*.amplifyapp.com`.
5. Chọn **Save**.

#### Cập nhật S3 CORS

1. Mở bucket `raw-reviews-<ACCOUNT_ID>-ap-southeast-1`.
2. Chọn **Permissions → Cross-origin resource sharing (CORS) → Edit**.
3. Thêm `https://<your-custom-domain>` vào `AllowedOrigins`.
4. Lưu thay đổi.

#### Build lại frontend

Cập nhật tệp `.env`:

```bash
VITE_COGNITO_REDIRECT_URI=https://<your-custom-domain>/callback
VITE_COGNITO_LOGOUT_URI=https://<your-custom-domain>/logout
```

Sau đó build lại:

```bash
npm run build
cd dist && zip -r ../build.zip . && cd ..
```

Triển khai lại bằng **Manual Deploy** trên Amplify.

### 4. Build ứng dụng React

Khởi tạo dự án:

```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
npm install recharts lucide-react react-oidc-context oidc-client-ts
npm install tailwindcss @tailwindcss/vite
```

![Guide](/Workshop/images/5-Workshop/frontend-4.PNG)

#### Cấu hình `vite.config.ts`

```ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
})
```

#### Cấu hình `src/index.css`

```css
@import "tailwindcss";
```

Thay thế `src/App.tsx` bằng nội dung của tệp `03_react_dashboard.tsx`.

Tạo tệp `.env` với các biến sau:

| Biến | Ý nghĩa | Vị trí lấy |
|------|----------|------------|
| `VITE_API_URL` | URL của REST API | API Gateway → Stages → Invoke URL |
| `VITE_COGNITO_AUTHORITY` | URL OIDC của User Pool | `https://cognito-idp.<region>.amazonaws.com/<user-pool-id>` |
| `VITE_COGNITO_CLIENT_ID` | App Client ID | Cognito → App clients |
| `VITE_COGNITO_DOMAIN` | Hosted UI Domain | Cognito → Branding → Domain |
| `VITE_COGNITO_REDIRECT_URI` | Callback URL | Domain Amplify + `/callback` |
| `VITE_COGNITO_LOGOUT_URI` | Sign-out URL | Domain Amplify + `/logout` |

```bash
cat > .env << 'EOF'
VITE_API_URL=https://<api-id>.execute-api.<region>.amazonaws.com/<stage>
VITE_COGNITO_AUTHORITY=https://cognito-idp.<region>.amazonaws.com/<user-pool-id>
VITE_COGNITO_CLIENT_ID=<app-client-id>
VITE_COGNITO_DOMAIN=<cognito-domain-prefix>.auth.<region>.amazoncognito.com
VITE_COGNITO_REDIRECT_URI=https://<your-branch>.<your-app-id>.amplifyapp.com/callback
VITE_COGNITO_LOGOUT_URI=https://<your-branch>.<your-app-id>.amplifyapp.com/logout
EOF

npm run build
```

![Guide](/Workshop/images/5-Workshop/frontend-5.PNG)

> **Lưu ý:** Region trong `VITE_API_URL` và `VITE_COGNITO_AUTHORITY` phải trùng với Region đã triển khai. Callback URL và Sign-out URL cũng phải khớp hoàn toàn với cấu hình trong Cognito để tránh lỗi `redirect_mismatch`.

### 5. Triển khai frontend lên Amplify

1. Mở **Amplify Console** → ứng dụng → branch `production`.
2. Chọn **Deploy updates** hoặc **Start a manual deployment**.

![Guide](/Workshop/images/5-Workshop/frontend-6.PNG)

3. Nén **toàn bộ nội dung** của thư mục `frontend/dist/` (không nén chính thư mục `dist`).

![Guide](/Workshop/images/5-Workshop/frontend-7.PNG)

4. Chọn:
   - **Drag and drop**
   - **Choose .zip folder**
   - Chọn `build.zip`

Điều này sẽ thay thế trang placeholder đã triển khai trước đó.

![Guide](/Workshop/images/5-Workshop/frontend-8.PNG)

5. Sau khi hoàn tất, truy cập domain Amplify.

Bạn sẽ thấy màn hình đăng nhập.

### 6. Cập nhật Cognito và S3

#### Cognito

1. Mở **Cognito → User Pool → Applications → App clients → review-sentiment-analyzer-client → Login pages → Managed login pages configuration → Edit**.
2. Thêm Callback URL `https://<your-amplify-domain>/callback`.
3. Thêm Sign-out URL `https://<your-amplify-domain>/logout`.
4. Giữ nguyên các URL `localhost`.
5. Chọn **Save**.

![Guide](/Workshop/images/5-Workshop/frontend-9.PNG)

#### Amazon S3

1. Mở bucket `raw-reviews-<ACCOUNT_ID>-ap-southeast-1`.
2. Chọn **Permissions → Cross-origin resource sharing (CORS) → Edit**.
3. Thêm `https://<your-amplify-domain>` vào `AllowedOrigins`.
4. Lưu thay đổi.

![Guide](/Workshop/images/5-Workshop/frontend-10.PNG)

### 7. Kiểm tra toàn bộ hệ thống

1. Truy cập `https://<your-amplify-domain>` — ứng dụng sẽ hiển thị màn hình đăng nhập.
2. Chọn **Sign in / Sign up**.
3. Người dùng sẽ được chuyển đến Cognito Hosted UI để đăng ký tài khoản và xác nhận email.
4. Sau khi đăng nhập thành công, trình duyệt sẽ chuyển về `/callback`, sau đó hiển thị Dashboard và tải dữ liệu từ endpoint `GET /products`.
5. Thử tải lên tệp `test_reviews.json`.
6. Chọn **Logout**.
7. Người dùng sẽ được chuyển đến Cognito Logout Endpoint rồi quay trở lại màn hình đăng nhập.

![Guide](/Workshop/images/5-Workshop/frontend-11.PNG)

## Kết quả mong đợi

- Frontend có thể xác thực người dùng thông qua Amazon Cognito.
- Có thể tải tệp trực tiếp lên Amazon S3.
- Có thể gọi REST API để lấy dữ liệu.
- Toàn bộ quy trình hoạt động bình thường, không gặp lỗi Redirect hoặc CORS.