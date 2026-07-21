---
title: "Blog 2: Automating data quality control in a Lakehouse architecture with AWS"
date: 2026-06-30
weight: 2
chapter: false
pre: " <b> 3.2. </b> "
---

In modern data systems, data is no longer used just for reporting — it also powers analytics and AI/ML applications. As data volumes grow larger and come from an increasing number of sources, ensuring **data quality** becomes essential to maintaining the reliability of the entire system. Even a small amount of incorrect or missing data can affect dashboards, Machine Learning models, or business decisions.

In this article, AWS introduces how to combine **Amazon S3 Tables**, **Apache Iceberg**, **AWS Glue Data Quality**, and **Amazon SageMaker Unified Studio** to build an automated data quality checking process within a Lakehouse architecture.

**Data quality is no longer a final checkpoint — it is integrated directly into the data processing pipeline.**

## Automating Data Quality Checks

**AWS Glue Data Quality** allows you to define data validation rules and run them automatically every time new data enters the system.

Some common rules include:

- Values must not be NULL.
- No duplicate data.
- Correct data types.
- Values fall within an allowed range.
- Compliance with business rules.

Checks are performed directly within the pipeline, helping to catch issues before the data is used for reporting or analysis.

## Amazon S3 Tables and Apache Iceberg

AWS uses **Amazon S3 Tables** and **Apache Iceberg** to store and manage data using the Lakehouse model.

**Apache Iceberg** provides features such as:

- ACID Transactions
- Schema Evolution
- Time Travel

Meanwhile, **Amazon S3 Tables** simplifies the management of data tables on Amazon S3.

## AWS Glue Data Catalog

**AWS Glue Data Catalog** serves as the centralized metadata management hub for all data.

This allows other services within the AWS ecosystem to access the same metadata source, making data management more consistent and unified.

## Amazon SageMaker Unified Studio

Once data has passed quality checks, **SageMaker Unified Studio** supports the process of exploring, analyzing, and preparing data for AI/ML use cases — all within a single working environment.

## Benefits of Integrating Data Quality into the Pipeline

Under AWS's approach, data quality checks are performed during processing rather than as a final step.

This helps to:

- **Detect errors earlier.**
- **Reduce the risk** of inaccurate data being used.
- **Increase the reliability** of reports and AI models.
- **Simplify** the management of data validation rules.

## CONCLUSION

The combination of **Amazon S3 Tables**, **Apache Iceberg**, **AWS Glue Data Quality**, **AWS Glue Data Catalog**, and **Amazon SageMaker Unified Studio** helps build a more reliable data pipeline, while reducing manual review effort and providing strong support for both analytics and AI/ML systems.

![Solution architecture](/Workshop/images/3-BlogsTranslated/Blog2.jpg)

[Facebook Post (AWS Study Group)](https://www.facebook.com/photo/?fbid=2529147894181976&set=gm.2199841160780844&idorvanity=660548818043427)

[Original Post (AWS Big Data Blog)](https://aws.amazon.com/vi/blogs/big-data/accelerate-your-data-quality-journey-for-lakehouse-architecture-with-amazon-sagemaker-apache-iceberg-on-aws-amazon-s3-tables-and-aws-glue-data-quality/)