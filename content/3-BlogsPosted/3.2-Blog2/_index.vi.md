---
title: "Blog 2: TỰ ĐỘNG HÓA KIỂM SOÁT CHẤT LƯỢNG DỮ LIỆU TRONG KIẾN TRÚC LAKEHOUSE VỚI AWS"
date: 2026-06-30
weight: 2
chapter: false
pre: " <b> 3.2. </b> "
---

Trong các hệ thống dữ liệu hiện đại, dữ liệu không chỉ được sử dụng cho báo cáo mà còn phục vụ phân tích và các ứng dụng AI/ML. Khi khối lượng dữ liệu ngày càng lớn và đến từ nhiều nguồn khác nhau, việc đảm bảo **chất lượng dữ liệu (Data Quality)** trở thành một yêu cầu quan trọng để duy trì độ tin cậy của toàn bộ hệ thống. Chỉ cần một lượng nhỏ dữ liệu sai hoặc thiếu cũng có thể ảnh hưởng đến dashboard, mô hình Machine Learning hoặc quyết định kinh doanh.

Trong bài viết này, AWS giới thiệu cách kết hợp **Amazon S3 Tables**, **Apache Iceberg**, **AWS Glue Data Quality** và **Amazon SageMaker Unified Studio** để xây dựng quy trình kiểm tra chất lượng dữ liệu tự động trong kiến trúc LakeHouse.

**Data Quality không còn là bước kiểm tra sau cùng, mà được tích hợp trực tiếp vào pipeline xử lý dữ liệu.**

## Tự động hóa kiểm tra chất lượng dữ liệu

**AWS Glue Data Quality** cho phép định nghĩa các quy tắc kiểm tra dữ liệu và thực hiện chúng tự động mỗi khi dữ liệu mới được đưa vào hệ thống.

Một số quy tắc phổ biến:

- Giá trị không được NULL.
- Không có dữ liệu trùng lặp.
- Đúng kiểu dữ liệu.
- Giá trị nằm trong khoảng cho phép.
- Tuân thủ các quy tắc nghiệp vụ.

Việc kiểm tra được thực hiện ngay trong pipeline, giúp phát hiện các vấn đề trước khi dữ liệu được sử dụng cho báo cáo hoặc phân tích.

## Amazon S3 Tables và Apache Iceberg

AWS sử dụng **Amazon S3 Tables** và **Apache Iceberg** để lưu trữ và quản lý dữ liệu theo mô hình Lakehouse.

**Apache Iceberg** cung cấp các tính năng như:

- ACID Transactions
- Schema Evolution
- Time Travel

Trong khi **Amazon S3 Tables** giúp đơn giản hóa việc quản lý các bảng dữ liệu trên Amazon S3.

## AWS Glue Data Catalog

**AWS Glue Data Catalog** đóng vai trò là nơi quản lý metadata tập trung cho toàn bộ dữ liệu.

Điều này cho phép các dịch vụ khác trong hệ sinh thái AWS có thể truy cập cùng một nguồn metadata, giúp việc quản lý dữ liệu trở nên thống nhất hơn.

## Amazon SageMaker Unified Studio

Sau khi dữ liệu được kiểm tra chất lượng, **SageMaker Unified Studio** hỗ trợ quá trình khám phá, phân tích và chuẩn bị dữ liệu cho các bài toán AI/ML trong cùng một môi trường làm việc.

## Lợi ích của việc tích hợp Data Quality vào Pipeline

Theo cách tiếp cận của AWS, việc kiểm tra chất lượng dữ liệu được thực hiện ngay trong quá trình xử lý thay vì ở bước cuối.

Điều này giúp:

- **Phát hiện lỗi sớm hơn.**
- **Giảm nguy cơ** dữ liệu không chính xác được sử dụng.
- **Nâng cao độ tin cậy** của báo cáo và mô hình AI.
- **Đơn giản hóa** việc quản lý các quy tắc kiểm tra dữ liệu.

## KẾT LUẬN

Sự kết hợp giữa **Amazon S3 Tables**, **Apache Iceberg**, **AWS Glue Data Quality**, **AWS Glue Data Catalog** và **Amazon SageMaker Unified Studio** giúp xây dựng một pipeline dữ liệu đáng tin cậy hơn, đồng thời giảm công sức kiểm tra thủ công và hỗ trợ tốt cho các hệ thống phân tích cũng như AI/ML.

![Solution architecture](/Workshop/images/3-BlogsTranslated/Blog2.jpg)

[Facebook Post (AWS Study Group)](https://www.facebook.com/photo/?fbid=2529147894181976&set=gm.2199841160780844&idorvanity=660548818043427)

[Original Post (AWS Big Data Blog)](https://aws.amazon.com/vi/blogs/big-data/accelerate-your-data-quality-journey-for-lakehouse-architecture-with-amazon-sagemaker-apache-iceberg-on-aws-amazon-s3-tables-and-aws-glue-data-quality/)