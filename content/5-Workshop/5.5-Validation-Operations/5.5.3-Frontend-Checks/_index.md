---
title: "5.5.3 Frontend checks"
weight: 3
---

# Frontend validation

## Overview

Use the deployed backend values to verify the frontend configuration and basic user flow. This page keeps the final UI checks focused on real integration points instead of visual polish.

### What to verify

- API URL points to the deployed stage
- Cognito authority and client ID are correct
- Redirect and logout URLs match the frontend domain
- Browser upload flow can reach S3 directly

## Step-by-step

### 1. Create the (empty) Amplify app

1. Console → **Amplify** → **Create new app**
2. Choose **Deploy without a Git provider** (no repo for this study/demo build)

![Guide](/Workshop/images/5-Workshop/frontend-1.PNG)

3. App name: `review-sentiment-analyzer-frontend`
4. Environment name: `production`
5. Deploy a throwaway placeholder now; you'll redeploy the real build later:
```bash
echo "<h1>Coming soon</h1>" > index.html
7z a placeholder.zip index.html
```

![Guide](/Workshop/images/5-Workshop/frontend-2.PNG)

Method: **Drag and drop** → **Choose .zip folder** → select `placeholder.zip` → **Save and deploy**. You just need the app to exist so it has a default domain.
6. Note the **default domain** shown on the app's overview page (looks like `https://production.dXXXXXXXXXXXXX.amplifyapp.com`)

### 2. SPA routing on Amplify

1. Amplify console → your app → **Hosting** → **Rewrites and redirects** → **Add rewrite**
```json
  {
    "source": "/<*>",
    "status": "404-200",
    "target": "/index.html"
  }
```
2. Save

![Guide](/Workshop/images/5-Workshop/frontend-3.PNG)

**Your public URL is the Amplify domain directly**: `https://<branch>.<app-id>.amplifyapp.com` (already valid HTTPS). Copy it from the app's overview page.

### 3. Optional: custom domain via Amplify's own domain management

If you have (or plan to register) a domain, this is the correct, supported way to get `Route 53 → Amplify` — unlike the manually-built CloudFront approach, Amplify provisions and manages its own internal CloudFront distribution and ACM certificate for this; you never create or touch either directly.

**Prerequisite: the domain's DNS needs to be in a Route 53 public hosted zone in this same AWS account.** If you registered the domain through Route 53 itself, this already exists. If it's registered elsewhere (a registrar, a free domain service like DigitalPlat FreeDomain's `.dpdns.org`, Cloudflare, etc.), migrate it first:

1. Route 53 → **Hosted zones** → **Create hosted zone** → enter the **full registered domain name** → Type: **Public hosted zone** → Create
2. Route 53 generates 4 NS records for the new zone — copy all 4 (they look like `ns-123.awsdns-12.com`)
3. Go to wherever the domain is currently registered (your registrar's dashboard) and replace its nameservers with those 4 Route 53 ones
4. Wait for propagation (minutes to a few hours, depends on the registrar) — confirm it's actually taken effect before continuing:

```bash
nslookup -type=NS yourdomain.com 8.8.8.8
```

Once the hosted zone is confirmed authoritative (or already was, if registered through Route 53):

5. Amplify console → your app → **App settings** → **Domain management** → **Add domain**
6. Enter your domain (e.g. `reviews.example.com`, or a subdomain of it)
7. Amplify detects the matching Route 53 hosted zone automatically (since it's in the same account) — confirm it
8. Choose which branch maps to which subdomain (map `main`/`production` to the domain you want to serve the app from)
9. **Save** — Amplify writes the ACM validation record and the alias record into Route 53 for you, no manual DNS step needed
10. Wait for the status to go from **Pending verification** → **Available** (a few minutes to ~30 minutes for cert validation + propagation)

**Cognito:**
11. **Applications → App clients** → `review-sentiment-analyzer-client` → **Login pages** → **Managed login pages configuration** → **Edit**
12. Add to **Allowed callback URLs**: `https://<your-custom-domain>/callback`
13. Add to **Allowed sign-out URLs**: `https://<your-custom-domain>/logout`
14. Keep the existing `*.amplifyapp.com` and `localhost` entries too — no need to remove them
15. Save

**S3** (easy to miss — the upload flow PUTs directly to S3, bypassing API Gateway entirely, so S3's own CORS config needs every origin the app might be served from, not just the Amplify domain):
16. `raw-reviews-<ACCOUNT_ID>-ap-southeast-1` → **Permissions** → **Cross-origin resource sharing (CORS)** → **Edit**
17. Add `"https://<your-custom-domain>"` to the `AllowedOrigins` array, alongside the existing entries
18. Save

**Rebuild and redeploy the frontend** with the custom domain in `.env`:
```bash
VITE_COGNITO_REDIRECT_URI=https://<your-custom-domain>/callback
VITE_COGNITO_LOGOUT_URI=https://<your-custom-domain>/logout
```
```bash
npm run build
cd dist && zip -r ../build.zip . && cd ..
```
Then Amplify manual deploy, same as always.

### 4. Build the React app locally

You'll need Node.js installed on your machine for this step (the actual `npm run build` can't happen inside the AWS console).

```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
npm install recharts lucide-react react-oidc-context oidc-client-ts
npm install tailwindcss @tailwindcss/vite
```

![Guide](/Workshop/images/5-Workshop/frontend-4.PNG)

**`vite.config.ts`** — add the Tailwind plugin:
```ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
})
```

**`src/index.css`** — replace its contents with just:
```css
@import "tailwindcss";
```

Replace `src/App.tsx` with the updated `03_react_dashboard.tsx`, then create a `.env` file in the project root with the 6 variables below. **None of these are secrets** — they're all public client-side identifiers — but they are specific to *your* deployment, so every value here needs to come from what you actually built in the earlier phases, not copied from an example.

| Variable | What it is | Where to find it |
|---|---|---|
| `VITE_API_URL` | Base URL of the deployed REST API, **including the stage** | API Gateway → your API → **Stages** → click the stage (`dev`) → **Invoke URL** at the top. Format: `https://<api-id>.execute-api.<region>.amazonaws.com/<stage>` |
| `VITE_COGNITO_AUTHORITY` | The OIDC issuer URL for your user pool | Built from two values you already have: `https://cognito-idp.<region>.amazonaws.com/<user-pool-id>`. Find the User Pool ID on the pool's **Overview** page. |
| `VITE_COGNITO_CLIENT_ID` | The app client's ID (not its name) | Cognito → your user pool → **Applications → App clients** → the app client's ID column (a 26-character alphanumeric string) |
| `VITE_COGNITO_DOMAIN` | The Hosted UI's domain, **without** `https://` | Cognito → your user pool → **Branding → Domain** page. Format: `<prefix>.auth.<region>.amazoncognito.com` |
| `VITE_COGNITO_REDIRECT_URI` | Where Cognito sends the user back after a successful sign-in | `https://<your-amplify-domain>/callback` — the Amplify app domain from 8.2/8.3, **must exactly match** an entry in the app client's Allowed callback URLs (Phase 8.6) or Cognito will refuse the redirect |
| `VITE_COGNITO_LOGOUT_URI` | Where Cognito sends the user after logging out | `https://<your-amplify-domain>/logout` — same domain, same exact-match requirement against Allowed sign-out URLs |

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

> Two things worth double-checking before you build: the `region` in the first two variables must match wherever you actually created these resources (this guide uses `ap-southeast-1` throughout), and the callback/logout URIs must be an **exact string match** — including trailing slashes and http vs https — against what's registered on the Cognito app client, or sign-in will fail with a redirect-mismatch error.

### 5. Deploy the build to Amplify

1. Amplify console → your app → the `production` branch
2. Look for **Deploy updates** / manual deploy → **Start a manual deployment**

![Guide](/Workshop/images/5-Workshop/frontend-6.PNG)

3. Zip the files of `frontend/dist/` folder's *contents* (not the folder itself)

![Guide](/Workshop/images/5-Workshop/frontend-7.PNG)

4. Method: **Drag and drop** → **Choose .zip folder** → select `build.zip`

![Guide](/Workshop/images/5-Workshop/frontend-8.PNG)

5. Once it finishes, visit the Amplify domain — you should see the sign-in gate.

### 6. Add the real domain to Cognito and S3

Two places still only know about `localhost:3000` — both need the real Amplify domain now that it exists:

**Cognito:**
1. Cognito → your user pool → **Applications → App clients** → click `review-sentiment-analyzer-client` → **Login pages** tab → **Managed login pages configuration** → **Edit**
2. Add to **Allowed callback URLs**: `https://<your-amplify-domain>/callback`
3. Add to **Allowed sign-out URLs**: `https://<your-amplify-domain>/logout`
4. Keep the `localhost:3000` ones too — handy for local dev later
5. Save

![Guide](/Workshop/images/5-Workshop/frontend-9.PNG)

**S3:**
6. S3 → `raw-reviews-<ACCOUNT_ID>-ap-southeast-1` → **Permissions** → **Cross-origin resource sharing (CORS)** → **Edit**
7. Add `"https://<your-amplify-domain>"` to the `AllowedOrigins` array, alongside the existing `http://localhost:3000` entry
8. Save

![Guide](/Workshop/images/5-Workshop/frontend-10.PNG)

### 7. Test end-to-end

1. Visit `https://<your-amplify-domain>` — should show the sign-in gate
2. Click **Sign in / Sign up** → redirected to Cognito's Hosted UI → sign up a real account (self-registration is on) → confirm the emailed code
3. Should redirect back to `/callback` → briefly loading → then the actual dashboard, showing products from `GET /products`
4. Try uploading `test_reviews.json` through the UI
5. Click **Logout** — should bounce through Cognito's logout endpoint and land back at the sign-in gate

![Guide](/Workshop/images/5-Workshop/frontend-11.PNG)

### Expected result

The frontend should be able to authenticate, upload data, and fetch results without redirect or CORS errors.
