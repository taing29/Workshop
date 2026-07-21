---
title: "Meet up - 2026/07/11"
date: 2026-07-11
weight: 3
chapter: false
pre: " <b> 4.3. </b> "
---

![Ảnh](/Workshop/images/4-EventParticipated/Event3.jpg)

### **Speaker 1: Nguyễn Huỳnh Sơn**  
#### **Topic:** SLA and Monitoring - From SLA to Monitoring: What Really Matters

### Main Objectives of the Talk

- Help students understand the difference between “healthy” infrastructure and real user experience.
- Explain the role of SLA and how Monitoring supports risk management.
- Emphasize that monitoring only the infrastructure layer is not enough — business metrics and user journeys must also be monitored.

### Key Highlights

- **Opening Story**: The AWS Console can be green, servers may be running, but users still cannot log in.
- **What is SLA?**: Service Level Agreement — a commitment between the provider and the customer. SLA is like a “conditional warranty”. AWS is responsible for its services, but user experience is the responsibility of the system you build.
- **Risk Management**: Monitoring is part of the risk management process (Identify → Monitor → Respond → Improve). It helps detect risks early before they violate SLA and affect customers.
- **The Gap between Healthy Infrastructure & Happy Users**:
  - Infrastructure (CPU, Memory, Disk…)
  - Application (Latency, Errors…)
  - Business Metrics (Login success rate, Order success…)
  - Customer Experience (Can login? Can checkout?)

- **Monitoring Pyramid**:
  - Customer Experience (top layer)
  - Business Metrics
  - Application
  - Infrastructure
  - Cloud Provider

- **Live Demo**:
  - Two endpoints: `/health` (still OK) and `/login` (fails when DB is blocked).
  - Dashboard shows completely “green” at the infrastructure layer, but users cannot log in.

- **Alerting Flow**: From custom metric (LoginFailure) → CloudWatch Alarm → SNS Notification.

### What I Learned

- Healthy Infrastructure ≠ Happy Users. A running server does not mean the system is usable for end users.
- Monitoring only infrastructure metrics (CPU, Memory…) is insufficient. Business metrics and user journeys (Login Success Rate, Order Success…) must also be monitored.
- SLA is the provider’s commitment, while delivering a good user experience is the responsibility of the development team.
- Custom metrics + CloudWatch Alarms + SNS is an effective way to detect and respond to issues before customers complain.
- Monitoring is truly valuable when it helps detect problems before they impact end users.

---

### **Speaker 2: Ngo Le Tan Huy**  
#### **Topic:** Inside The Exam: AWS Cloud Practitioner

### Main Objectives of the Talk

- Provide an overview and effective study strategy for the AWS Certified Cloud Practitioner (CLF-C02) exam.
- Help students understand the exam structure, key domains, and the right mindset to answer questions.
- Share real experience, tips & tricks, and useful study resources.

### Key Highlights

- **Exam Overview**:
  - Number of questions: 65 (multiple choice, may have more than one correct answer).
  - Duration: 90 minutes (additional 30 minutes for non-native English speakers).
  - Passing score: 700/1000.
  - Certification validity: 3 years.

- **Exam Structure**:
  - Domain 1: Cloud Concepts (24%)
  - Domain 2: Security and Compliance (30%)
  - Domain 3: Cloud Technology and Services (34%)
  - Domain 4: Billing, Pricing, and Support (12%)

- **Important Concepts**:
  - 6 Benefits of AWS Cloud.
  - AWS Well-Architected Framework (6 pillars).
  - AWS Cloud Adoption Framework (CAF).
  - Shared Responsibility Model.
  - IAM, Security Groups, NACLs, AWS Shield, WAF, Artifact.
  - Global Infrastructure, Compute, Storage, Database, and Networking services.
  - EC2 pricing models, cost management tools, and Support plans.

- **Tips & Tricks**:
  - Elimination technique for answer choices.
  - Don’t overthink — choose the simplest and most logical answer.
  - Pay attention to negative keywords (Not, Least, Most…).
  - Use “Flag for Review” and prepare mentally before the exam.

### What I Learned

- The Cloud Practitioner exam focuses on big-picture understanding and real-world use cases rather than deep coding or configuration.
- Shared Responsibility Model and AWS Well-Architected Framework are extremely important topics.
- Understanding each service’s role and linking it to business problems helps answer questions more effectively.
- Effective exam preparation is not about rote memorization but about understanding concepts and analyzing wrong answers.
- Mental preparation, proper materials, and exam procedures are key to achieving good results.

---

### **Speaker 3: Thinh Nguyen**  
#### **Topic:** Securing Your Web Apps With AWS Security Agent

### Main Objectives of the Talk

- Introduce AWS Security Agent — an autonomous AI Agent for securing web applications.
- Highlight the limitations of traditional manual security testing (pentest).
- Guide how to use the Frontier Agent across the entire application development lifecycle (Design → Code → Production).

### Key Highlights

- **The Security Bottleneck**: Traditional security testing is time-consuming, expensive, inconsistent, and heavily dependent on human expertise.
- **Meet the Frontier Agent**:
  - Autonomous reasoning powered by Amazon Bedrock.
  - Covers the full lifecycle: Design Review, Code Security Review, and Automated Penetration Testing.
  - Produces verifiable findings by actually attempting exploitation.

- **Key Features**:
  - **Design Security Review**: Analyzes architecture documents and Terraform code against standards (PCI DSS, NIST CSF, AWS Well-Architected).
  - **Code Security Review**: Integrated into GitHub/GitLab Pull Requests with automatic fix suggestions.
  - **Automated Pentesting**: Performs complex multi-step attack chains with real-user authentication and detailed attack graphs.

- **Pricing & Reality**:
  - Free Trial: 2 months, 400 Task-Hours/month.
  - Pricing: $50 per Task-Hour.
  - Real case: Total cost typically ranges from $1,500 – $2,500 per project.

- **Critical Limitations**: Struggles with MFA, biometrics, complex business logic flaws, and high Task-Hour consumption on large applications.

### What I Learned

- Traditional manual security processes are a major bottleneck in terms of time and cost.
- AWS Security Agent represents a major advancement, enabling automated, continuous, and verifiable security testing.
- The Agent can support from design phase through to production pentesting, making DevSecOps much more efficient.
- Despite its strengths, the Agent still has limitations (MFA, logic flaws…) and should be combined with human oversight.
- Monitoring Task-Hour usage is crucial for cost control.
