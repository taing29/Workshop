---
title: "5.5.1 Auth and API"
weight: 1
---
# Auth and API setup

## Overview

Create the Cognito and API Gateway surface that exposes ReviewSentinal to users. This page covers the authentication boundary and the REST API that fronts the Lambda handler.

### What to configure

- Cognito user pool and app client
- API Gateway REST API
- Cognito authorizer
- CORS on all public resources

### Key endpoints

- `GET /products`
- `POST /products`
- `POST /upload`
- `POST /analyze`

## Step-by-step

### 1. Create the Cognito user pool

1. Open **Cognito** → **Create user pool**.
2. Choose **Single-page application (SPA)** as the application type.
3. Name the application `review-sentiment-analyzer-client`.
4. Use **Email** only for sign-in identifiers.
5. Enable self-registration for the demo build.
6. Require both `email` and `name` at sign-up.
7. Set the callback/return URL to `http://localhost:3000/callback`.
8. Choose a Hosted UI domain prefix and create the user directory.
9. After creation, open the app client settings and add `http://localhost:3000/logout` as a sign-out URL.
10. Enable `ALLOW_ADMIN_USER_PASSWORD_AUTH` if you plan to use the CLI test flow later.

### 2. Record the identifiers you will reuse

1. Copy the User Pool ID from the overview page.
2. Copy the App Client ID from the app client list.
3. Copy the Cognito Hosted UI domain from the domain page.

### 3. Create the REST API

1. Open **API Gateway** and choose **Create API**.
2. Select **REST API** and create a **New API**.
3. Name the API `review-sentiment-analyzer-api`.
4. Keep the endpoint type **Regional**.
5. Create the API.

### 4. Add the Cognito authorizer

1. In the left sidebar, open **Authorizers**.
2. Create a new authorizer named `cognito-authorizer`.
3. Choose **Cognito** as the type.
4. Attach the user pool you just created.
5. Set the token source to `Authorization`.

### 5. Build the resource tree

1. Create the `/products` resource.
2. Under `/products`, create `{id}`.
3. Under `{id}`, create `reviews` and `analytics`.
4. Under `reviews`, create `{review_id}`.
5. Create the top-level `/upload` and `/analyze` resources.

### 6. Add methods and integrations

1. Add the required methods for each resource listed in the workshop.
2. Use Lambda proxy integration.
3. Point every method at `review-sentiment-analyzer-api`.
4. Keep the authorization on the product, upload, and analysis routes set to `cognito-authorizer`.

### 7. Configure CORS

1. Enable CORS on every public resource.
2. Allow `Content-Type`, `Authorization`, `X-Api-Key`, and `X-Amz-Security-Token` headers.
3. Add `Default 4XX` and `Default 5XX` gateway responses.
4. Confirm the console creates the `OPTIONS` methods automatically.

### 8. Deploy the API

1. Deploy a new `dev` stage.
2. Copy the Invoke URL from the stage page.

### Notes

1. Keep the callback and sign-out URLs aligned with the frontend domain.
2. Use the user pool ID, not the app client ID, when attaching the authorizer.
3. Grant Lambda invoke permission from API Gateway while you create each method.

### Expected result

The app should have a working login flow and a deployed REST API stage ready for the dashboard and upload flow.