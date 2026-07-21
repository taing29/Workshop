---
title: "5.3.2 DynamoDB tables"
weight: 2
---

# DynamoDB tables for ReviewSentinal

## Overview

Create the three tables that hold review data, product data, and user data. The `Reviews` table is the main one and needs streams plus a GSI. Additionally, create an `Analyses` table to track analysis jobs.

### Tables to create

- `Analyses`
- `Reviews`
- `Products`
- `Users`

### Analyses table

1. Open DynamoDB and choose **Create table**.
2. Table name: `Analyses`.
3. Partition key: `AnalysisID` as a String.
4. Choose **Customize**.
5. Set capacity to **On-demand**.
6. Leave encryption as the default DynamoDB-managed key.
7. Create the table.

### Reviews table

1. Open DynamoDB and choose **Create table**.
2. Table name: `Reviews`.
3. Partition key: `ProductID` as a String.
4. Sort key: `ReviewID` as a String.
5. Choose **Customize**.
6. Set capacity to **On-demand**.
7. Leave encryption as the default DynamoDB-managed key.
8. Create the table.

After creation:

1. Open the `Reviews` table.
2. Enable **DynamoDB Streams** from the **Exports and streams** tab.
3. Choose **New image** as the stream view type.
4. Go to the **Backups** tab and enable **Point-in-time recovery**.
5. Create a GSI named `SentimentIndex`.
6. Use `ProductID` as the partition key and `Sentiment` as the sort key.
7. Project only `ReviewText`, `Rating`, `CreatedAt`, `KeyPhrases`, and `UserID`.
8. **Additive update (no existing data modification needed)**: When putting new items, include the `AnalysisID` attribute (as a regular attribute, not part of the key).
9. **Create GSI for analysis queries**: Create a Global Secondary Index named `AnalysisIndex` on the `Reviews` table:
   - Partition key: `AnalysisID` (String)
   - Sort key: `Leave blank` (or use `ReviewID` if sorting within analysis is needed)
   - Projected attributes: `KEYS_ONLY` (or `ALL` if needed for your queries)

### Products table

1. Create a table named `Products`.
2. Use `ProductID` as the partition key.
3. Leave out the sort key.
4. Use **On-demand** capacity.
5. Enable point-in-time recovery after creation.

### Users table

1. Create a table named `Users`.
2. Use `UserID` as the partition key.
3. Leave out the sort key.
4. Use **On-demand** capacity.
5. Enable point-in-time recovery after creation.

### Notes

- The `Reviews` table stream is needed for the sentiment analyzer Lambda trigger.
- Keep the table names exact because later environment variables and IAM policies reference them directly.
- The GSIs are kept minimal on purpose so you only pay for what the code uses.
- The `AnalysisID` attribute in `Reviews` is additive - it doesn't change the existing table schema, so existing data is unaffected.

### Expected result

Four tables should exist: `Analyses`, `Reviews`, `Products`, and `Users`.
- `Reviews` and `Analyses` should have streams enabled (for `Reviews` - needed for Lambda trigger)
- All tables should be on-demand with point-in-time recovery enabled
- `Reviews` table has:
  * Original primary key (ProductID, ReviewID)
  * GSIs: `SentimentIndex` and `AnalysisIndex`
  * Items include an `AnalysisID` attribute (added by the application)