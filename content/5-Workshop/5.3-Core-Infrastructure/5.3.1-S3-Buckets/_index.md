---
title: "5.3.1 S3 buckets"
weight: 1
---

# S3 buckets for ReviewSentinal

## Overview

Create the raw upload bucket first. The application uploads review files directly to S3, so this bucket is the starting point for the whole pipeline.

### Bucket to create

- `raw-reviews-<ACCOUNT_ID>-ap-southeast-1`

### Step-by-step

1. Open the S3 console and choose **Create bucket**.
2. Enter the bucket name using your actual AWS account ID.
3. Select **Asia Pacific (Singapore) ap-southeast-1**.
4. Keep **ACLs disabled**.

![Guide](/Workshop/images/5-Workshop/s3-bucket-1.PNG)

5. Leave **Block all public access** enabled.
6. Enable **Bucket Versioning**.

![Guide](/Workshop/images/5-Workshop/s3-bucket-2.PNG)

7. Enable default encryption with **SSE-S3**.
8. Create the bucket.



### Lifecycle rule

1. Open the bucket and go to the **Management** tab.
2. Create a lifecycle rule named `delete_old_files`.
3. Apply it to all objects.
4. Expire current versions after 90 days.
5. Permanently delete noncurrent versions after 30 days.

![Guide](/Workshop/images/5-Workshop/s3-bucket-4.PNG)

### CORS configuration

1. Open the bucket's **Permissions** tab.
2. Edit the **Cross-origin resource sharing (CORS)** configuration.
3. Paste the following CORS configuration for local development:
```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["PUT", "GET", "HEAD"],
    "AllowedOrigins": ["http://localhost:3000"],
    "ExposeHeaders": ["ETag"],
    "MaxAgeSeconds": 3000
  }
]
```
4. Save the configuration.

![Guide](/Workshop/images/5-Workshop/s3-bucket-5.PNG)

### Notes

- Keep the bucket private.
- The upload path uses a presigned S3 URL, so CORS matters even though the API is otherwise serverless.
- You will return here later in the workshop to add the deployed frontend origin.

### Expected result

The bucket should exist, versioning should be on, encryption should be on, and CORS should allow local uploads.
