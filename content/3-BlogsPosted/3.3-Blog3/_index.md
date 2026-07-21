---
title: "Blog 3: How Artera Uses AWS to Accelerate Prostate Cancer Diagnosis"
date: 2026-06-18
weight: 3
chapter: false
pre: " <b> 3.3. </b> "
---

This blog from the AWS Architecture Blog explains how **Artera**, a healthcare technology company, built an AI-powered platform to analyze biopsy images for predicting prostate cancer severity and patient response to treatment. Its **ArteraAI Prostate Test** has received FDA De Novo authorization, making it the first AI software approved for this purpose.

## Challenges Before AI

Traditionally, treatment decisions relied on chemical assays that measured the expression of only a limited number of genes, resulting in several major challenges:

* **Long turnaround time**: The entire diagnostic process could take up to **6 weeks**.
* **Limited analysis capability**: Only a small subset of genes associated with cancer risk could be evaluated.
* **Biopsy sample consumption**: Tissue samples were completely consumed during testing, preventing patients from undergoing additional diagnostic tests or participating in future clinical trials.

The system also faced several technical challenges:

* Biopsy images were extremely large, with some files reaching **8 GB** in size.
* Each image had to be divided into tens of thousands of **image patches** before AI models could process them.
* The platform had to comply with healthcare data regulations such as **HIPAA** across multiple countries.

## Solution: AI Inference Architecture with Amazon ECS and Amazon EKS

To overcome these challenges, Artera designed an AI architecture on AWS using multiple integrated services:

* **AWS Global Accelerator** and **Application Load Balancer** route requests from the physician portal into the Amazon VPC.
* **Amazon ECS** hosts the web portal used by healthcare professionals.
* **Amazon EKS** runs AI/ML inference workloads to analyze biopsy images using computer vision models.
* **Amazon EFS** provides shared file storage accessible by both ECS and EKS during image processing.
* **Amazon RDS** stores patient information and diagnostic results.
* **Amazon ElastiCache** reduces latency for frequently accessed data.
* **Amazon S3** stores original biopsy images and analysis outputs.
* **AWS IAM** manages user and service permissions.
* **AWS KMS** protects sensitive healthcare data through encryption key management.
* **Amazon CloudWatch** monitors the entire infrastructure and application environment.

One of the most impressive aspects of the architecture is its approach to **data locality**. By using **Amazon EFS** within the same AWS Region as the application, Artera can deploy resources regionally, ensuring patient data remains within required legal boundaries while still enabling rapid expansion into new markets.

## Results

After deploying the AWS-based architecture, Artera achieved significant improvements:

* **Reduced diagnostic turnaround time** from approximately **6 weeks to just 1–2 days**.
* **Accelerated image processing**, allowing tens of thousands of image patches from each biopsy slide to be analyzed in just a few hours instead of several weeks.
* **Workflow orchestration** breaks down large image files and processes them in parallel across Amazon EKS clusters, maximizing overall system performance.

## Personal Perspective

What impressed me most is how Artera successfully balances three critical requirements of an AI-powered healthcare system:

* Processing massive medical imaging datasets efficiently.
* Complying with regional healthcare data residency and regulatory requirements.
* Delivering faster diagnostic results to support timely clinical decision-making.

The combination of **Amazon ECS** for the web application layer and **Amazon EKS** for AI inference provides an excellent real-world architecture for organizations building large-scale AI solutions on AWS.

For anyone interested in AI-powered healthcare systems or large-scale medical image processing on AWS, this article is definitely worth reading.

![Solution Diagram](/Workshop/images/3-BlogsTranslated/Blog3.png)

Facebook Post (AWS Study Group - Pending Approval - Scheduled for July 18, 2026)

[Original Post (AWS Architecture Blog)](https://aws.amazon.com/blogs/architecture/how-artera-enhances-prostate-cancer-diagnostics-using-aws/)