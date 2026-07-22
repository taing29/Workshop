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
4. Use **Email** and **Username** for sign-in identifiers.
5. Enable self-registration for the demo build.
6. Require both `email` and `name` at sign-up.

![Guide](/Workshop/images/5-Workshop/auth-1.PNG)

7. Set the callback/return URL to `http://localhost:3000/callback`.

![Guide](/Workshop/images/5-Workshop/auth-2.PNG)

8. Choose a Hosted UI domain prefix and create the user directory.
9. After creation, open the app client settings and add `http://localhost:3000/logout` as a sign-out URL.
10. Enable `ALLOW_ADMIN_USER_PASSWORD_AUTH` if you plan to use the CLI test flow later.

![Guide](/Workshop/images/5-Workshop/auth-3.PNG)

![Guide](/Workshop/images/5-Workshop/auth-4.PNG)

### 2. Record the identifiers you will reuse

1. Copy the User Pool ID from the overview page.
2. Copy the App Client ID from the app client list.
3. Copy the Cognito Hosted UI domain from the domain page.

### 3. Create the REST API

1. Open **API Gateway** and choose **Create API**.
2. Select **REST API** and create a **New API**.

![Guide](/Workshop/images/5-Workshop/auth-6.PNG)

3. Name the API `review-sentiment-analyzer-api`.
4. Keep the endpoint type **Regional**.
5. Create the API.

![Guide](/Workshop/images/5-Workshop/auth-7.PNG)

### 4. Add the Cognito authorizer

1. In the left sidebar, open **Authorizers**.

![Guide](/Workshop/images/5-Workshop/auth-8.PNG)

2. Create a new authorizer named `cognito-authorizer`.
3. Choose **Cognito** as the type.
4. Attach the user pool you just created.
5. Set the token source to `Authorization`.

![Guide](/Workshop/images/5-Workshop/auth-9.PNG)

### 5. Build the resource tree

1. Create the `/products` resource.
2. Under `/products`, create `{id}`.
3. Under `{id}`, create `reviews` and `analytics`.
4. Under `reviews`, create `{review_id}`.
5. Create the top-level `/upload` and `/analyze` resources.

![Guide](/Workshop/images/5-Workshop/auth-10.PNG)

### 6. Add methods and integrations
```
/
└── products                       (GET, POST)
    └── {id}                       (DELETE)
        ├── reviews                 (GET)
        │   └── {review_id}         (DELETE)
        └── analytics               (GET)
/upload                            (POST)
/analyze                           (POST)
```

For **every** method (`GET /products`, `POST /products`, `DELETE /products/{id}`, `GET /products/{id}/reviews`, `DELETE /products/{id}/reviews/{review_id}`, `GET /products/{id}/analytics`, `POST /upload`, `POST /analyze`):
1. On the resource, **Create method**
2. Method type: as above
3. Integration type: **Lambda function**
4. **Lambda proxy integration**: toggle **ON**
5. Response transfer mode: **Buffered**
6. Lambda function: `review-sentiment-analyzer-api`
7. Leave Method request settings (query params/headers/body) empty
8. **Create method**

![Guide](/Workshop/images/5-Workshop/auth-11.PNG)

9. Open the method afterward → find **Authorization** under its method request settings → set to `cognito-authorizer`

![Guide](/Workshop/images/5-Workshop/auth-12.PNG)

![Guide](/Workshop/images/5-Workshop/auth-13.PNG)

### 7. Configure CORS

1. Enable CORS on every public resource.
2. Allow `Content-Type`, `Authorization`, `X-Api-Key`, and `X-Amz-Security-Token` headers.
3. Add `Default 4XX` and `Default 5XX` gateway responses.
4. Confirm the console creates the `OPTIONS` methods automatically.

![Guide](/Workshop/images/5-Workshop/auth-14.PNG)

### 8. Deploy the API

1. Deploy a new `dev` stage.

![Guide](/Workshop/images/5-Workshop/auth-15.PNG)

2. Copy the Invoke URL from the stage page.

![Guide](/Workshop/images/5-Workshop/auth-16.PNG)

### Notes

1. Keep the callback and sign-out URLs aligned with the frontend domain.
2. Use the user pool ID, not the app client ID, when attaching the authorizer.
3. Grant Lambda invoke permission from API Gateway while you create each method.

### Expected result

The app should have a working login flow and a deployed REST API stage ready for the dashboard and upload flow.