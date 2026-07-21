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

### 1. Prepare the local frontend

1. Create a Vite React TypeScript app if you have not already.
2. Install the dependencies as specified in the workshop.
3. Configure Tailwind if you are using the styled dashboard component.
4. Add the favicon and title changes in `index.html`.

### 2. Set the environment values

1. Create a `.env` file in the frontend project root.
2. Add the API URL from API Gateway.
3. Add the Cognito authority and client ID.
4. Add the Hosted UI domain.
5. Add the redirect and logout URIs for the deployed domain.

### 3. Build and deploy

1. Run the local build.
2. Zip the build output.
3. Upload it to the Amplify app manually.
4. Confirm the app serves from the Amplify domain.

### 4. Update Cognito and S3 for the deployed domain

1. Add the deployed frontend URL to the Cognito callback and sign-out URLs.
2. Add the deployed frontend URL to the S3 bucket CORS allowed origins.
3. Save both changes.

### 5. Run the browser checks

1. Open the deployed frontend.
2. Sign in through Cognito Hosted UI.
3. Verify the dashboard loads.
4. Upload a sample review file.
5. Confirm the review appears after the processor and analyzer complete.
6. Log out and make sure the app returns to the sign-in gate.

### Expected result

The frontend should be able to authenticate, upload data, and fetch results without redirect or CORS errors.
