---
title: "5.6.1 Frontend cleanup"
weight: 1
---

# Frontend cleanup

## Overview

Remove the deployed frontend first so users no longer have a public entry point into the workshop application.

### What to remove

- Amplify app or static hosting deployment
- Custom domain configuration if you created one
- Frontend build artifacts if they were uploaded manually

## Step-by-step

1. Open the Amplify console.
2. Select the ReviewSentinal frontend app.
3. Delete the app from the console.
4. If you added a custom domain, remove the domain association.
5. If you used a separate DNS hosted zone, leave it only if you still need the domain for something else.

## Notes

1. Delete the frontend before the backend so no users can keep calling the app while the rest of the stack is going away.
2. If you configured a custom domain, remove the DNS association as part of the frontend teardown.

## Expected result

The browser entry point for ReviewSentinal should no longer be available after this step.
