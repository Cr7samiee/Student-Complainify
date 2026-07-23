# 4 System Design and Analysis

## 4.1 Requirements Analysis

Complainify was developed to address the growing need for efficient complaint management and resolution tracking across university campuses. The requirements were gathered through analysis of existing complaint handling systems, consultation with the multi-role user ecosystem — students and administrators — and study of real-world challenges faced by students filing grievances across academic, hostel, infrastructure, and other campus domains. The system aims to bridge the gap between students and university administration by offering a centralized, role-based platform for complaint submission, AI-powered categorization, sentiment analysis, priority management, and resolution tracking.

### 4.1.1 Requirement Gathering

Requirements were gathered through analysis of student complaint handling challenges, identification of communication gaps between students and administration, and review of existing manual and digital complaint management practices. The gathered requirements emphasize role-based access control, automated AI categorization, sentiment-based priority boosting, real-time complaint tracking, OTP-based password recovery, email notifications, and transparent resolution workflows between students and administrators. Table 4.1 summarizes the gathered requirements.

**Table 4.1: Requirement Gathering**

| Requirement ID | Description |
|---------------|-------------|
| R1 | The system shall provide separate authentication mechanisms for Students and Admins using email and password. |
| R2 | Students shall be able to register, submit complaints, view their own complaint history, and manage their profile and account settings. |
| R3 | Students shall be able to submit a complaint with subject, description, and optional manual category selection. The system shall AI-auto-classify if no category is chosen. |
| R4 | The system shall automatically categorize complaints into one of 12 categories (Academics, Hostels, IT Support, Infrastructure, Financial Services, Administrative, Security, Maintenance, Transport, Canteen, Library, Other) using a Multinomial Naive Bayes classifier trained from scratch. |
| R5 | The system shall analyze the emotional tone of each complaint using a lexicon-based sentiment analyzer and return Positive, Neutral, or Negative with a numeric score. |
| R6 | The system shall auto-boost complaint priority when Negative sentiment is detected (Low → Medium, Medium → High). |
| R7 | Students shall be able to track the real-time status of their complaints (Pending, In Progress, Resolved) using a unique ticket ID. |
| R8 | Admins shall be able to view a live analytics dashboard showing total complaints, resolution rate, average resolution time, category breakdown with percentages, and sentiment distribution. |
| R9 | Admins shall be able to view, filter (by status, category, priority, sentiment), and paginate through all complaints. |
| R10 | Admins shall be able to assign complaints to departments, update status with resolution notes, attach files, and mark complaints as validated. |
| R11 | The system shall send automated email notifications for complaint submission, assignment, and status updates when SMTP is configured. |
| R12 | The system shall support OTP-based forgot/reset password flow with 6-digit codes and 10-minute expiry stored in the database. |
| R13 | Both Students and Admins shall be able to change their own passwords securely from Settings. |
| R14 | Admins shall be able to generate CSV exports of all complaints and view a detailed analytics report page with training dataset statistics. |
| R15 | The system shall provide a REST API endpoint for external integration to auto-categorize complaint text. |
| R16 | The system shall ensure students can only view their own complaints and admins can view all complaints. |
| R17 | The system shall provide AI confidence tiers (Auto ≥90%, Suggest 60–89%, Unknown <60%) to indicate classification reliability. |

### 4.1.2 Functional Requirements

The functional requirements define the specific behaviors and operations the system must perform to meet user needs and business objectives. Each functional requirement is mapped to one or more gathered requirements to ensure full coverage. Table 4.2 details all functional requirements for Complainify.

**Table 4.2: Functional Requirements**

| Function ID | Description | Cross Reference |
|-------------|-------------|----------------|
| F1 | User Authentication: The system shall validate login credentials for Students and Admins using email and password with SHA-256 hashing. Role-based redirection ensures each user lands on the correct dashboard after login. | R1 |
| F2 | Student Registration: New students shall register with full name, email, phone, and password. The system validates email uniqueness before account creation. | R1, R2 |
| F3 | Complaint Submission: Students shall submit complaints with subject, description, and optional manual category. The system auto-categorizes using AI when no category is chosen. | R2, R3 |
| F4 | AI Auto-Categorization: The system shall classify complaint text into 12 categories using a from-scratch Multinomial Naive Bayes classifier with custom stemmer, bigram features, and Laplace smoothing. Returns category, confidence score, and tier. | R4, R17 |
| F5 | Sentiment Analysis: The system shall analyze complaint text using a lexicon-based analyzer with ~150 words, negation handling, and intensifier amplification. Returns Positive/Neutral/Negative with numeric score. | R5 |
| F6 | Sentiment Priority Boost: The system shall auto-promote complaint priority when Negative sentiment is detected (Low → Medium, Medium → High). | R6 |
| F7 | Complaint Tracking: Students shall track complaint status using a unique ticket ID (CMP-XXXX format) on a dedicated track page. | R7 |
| F8 | Admin Live Dashboard: Admins shall view a real-time analytics dashboard with total complaints, resolved count, pending count, in-progress count, average resolution time (hours), critical alerts count, category breakdown bar chart with percentages, and sentiment distribution bars with hover counts. | R8 |
| F9 | Complaint Filtering and Pagination: Admins shall filter complaints by status (Pending/In Progress/Resolved), category (12 categories), priority (High/Medium/Low), and sentiment (Positive/Neutral/Negative). Results paginated at 20 per page with Prev/Next and page number navigation. | R9 |
| F10 | Complaint Assignment: Admins shall assign complaints to departments (Academic Affairs, Hostel Administration, IT Support, etc.) which updates status to In Progress and sends email notification. | R10 |
| F11 | Status Update with Resolution Message: Admins shall update complaint status with optional resolution notes and file attachment (PDF, Excel, Image, etc.). Status changes to Resolved with timestamp when marked resolved. | R10 |
| F12 | Complaint Validation: Admins shall mark complaints as legitimate (validated) to distinguish verified issues. | R10 |
| F13 | File Upload: Admins shall attach files (PDF, SVG, PNG, JPG, DOC, DOCX, XLS, XLSX, CSV, TXT, ZIP) to complaints during status updates. Files stored with unique names. Students can download attachments from complaint detail page. | R10 |
| F14 | Email Notifications: The system shall send email notifications for complaint submission (to student), assignment (to student), and status updates (to student) via SMTP when configured. Gracefully skips if SMTP is unset. | R11 |
| F15 | OTP-Based Password Recovery: The system shall generate 6-digit OTP, store in database with 10-minute expiry, send via email or display in console, and verify before allowing password reset. | R12 |
| F16 | Password Management: Both Students and Admins shall change passwords from Settings after validating current password. New passwords must be at least 6 characters and match confirmation. | R13 |
| F17 | CSV Export: Admins shall download all complaints as CSV with columns: Ticket ID, Student Name, Email, Category, Priority, Status, Subject, Description, Assigned To, Validated, Submitted At, Resolved At. | R14 |
| F18 | Analytics Report Page: Admins shall view a detailed report page with complaint statistics and training dataset analysis (total samples, unique texts, text length distribution, category distribution). | R14 |
| F19 | REST API: The system shall expose a POST /api/predict endpoint accepting JSON with `text` field and returning category, confidence, and tier. | R15 |
| F20 | Privacy Enforcement: Students can only view their own complaints. Admins can view all complaints. Complaint detail pages show full history including assignment and resolution timeline. | R16 |
| F21 | Role-Based Sidebar Navigation: The Complainify brand in the sidebar links to role-appropriate dashboard — admin_dashboard for admins, student_dashboard for students, landing page for unauthenticated users. | R1 |

## 4.2 Feasibility Study

### 4.2.1 Technical Feasibility

The technical feasibility analysis confirms that Complainify can be developed effectively with the technology stack and skills available to the development team. The system is built on widely adopted and well-documented technologies including Python, Flask, MySQL, HTML5, CSS3, and JavaScript — all of which are free to use and supported by large developer communities. The team possesses the required knowledge of full-stack web development, machine learning algorithm implementation, relational database management, and REST API design.

The custom Multinomial Naive Bayes classifier and lexicon-based sentiment analyzer were implemented entirely from scratch without external ML libraries, demonstrating the team's deep understanding of underlying algorithms. The custom stemmer (25 rules), bigram feature extraction, Laplace smoothing, and three-tier confidence system all operate without dependency on NLTK or scikit-learn.

Additional integrations such as SMTP for email notifications are well-documented and straightforward to configure. The system is designed to run on standard hosting infrastructure (XAMPP for development, any WSGI server for production) without requiring specialized hardware. MySQL handles structured data efficiently, and the modular Flask architecture ensures that individual components — the classifier engine, sentiment analyzer, web routes, notification system, and reporting module — can be developed, tested, and maintained independently. Therefore, Complainify is technically feasible.

### 4.2.2 Operational Feasibility

The operational feasibility analysis shows that Complainify will be readily accepted and effectively used by its two primary user groups. The system resolves critical pain points: students often struggle to file complaints through proper channels, lose track of their submissions, and receive no feedback; administrators lack a centralized view of campus-wide complaints and have no data-driven insights into recurring issues. Complainify addresses each of these with an intuitive AI-powered submission flow, real-time tracking, live analytics dashboards, and automated notifications.

The interface uses familiar web UI patterns (Tailwind CSS, Material Symbols) requiring minimal training for first-time users. The two-role architecture means that students and administrators each see only what is relevant to them, reducing cognitive overhead. Privacy controls ensure that students can only view their own complaints while admins have full system visibility, building trust across the user base.

The system is browser-based and does not require installation, making adoption straightforward across devices including mobile phones. Auto-categorization reduces manual effort for administrators, sentiment-based priority boosting ensures urgent negative-toned complaints are flagged appropriately, and the CSV export and report pages support data-driven decision making. Overall, Complainify fits naturally into existing university complaint management workflows and is operationally feasible.

### 4.2.3 Economic Feasibility

Complainify is economically feasible and demonstrates strong financial viability. The project requires an initial investment covering labor, documentation, hardware, API setup, training, and contingency. Annual operating costs cover hosting, maintenance, technical support, and email API fees. The system generates measurable annual benefits by reducing manual complaint sorting effort, improving resolution times, eliminating paper-based tracking, and reducing administrative overhead.

**Table 4.3: Initial Development Cost**

| Cost Component | Description | Estimated Cost (NPR) |
|---------------|-------------|---------------------|
| Labor Cost (Development) | 2 developers × 2 months × NPR 20,000 | 80,000 |
| System Design & Documentation | Diagrams, reports, and testing documents | 15,000 |
| Hardware & Utilities | Laptop usage, hosting, internet, electricity | 20,000 |
| AI Model Training & API Setup | Dataset preparation, SMTP configuration | 10,000 |
| Training & Deployment | Admin and student orientation, setup | 15,000 |
| Contingency Cost | Unexpected or miscellaneous expenses | 15,000 |
| **Total Initial Investment** | | **155,000** |

**Table 4.4: Net Cash Flow Analysis**

| Year | Annual Benefits (NPR) | Operating Costs (NPR) | Net Cash Flow (NPR) |
|------|----------------------|---------------------|-------------------|
| 1 | 110,000 | 28,000 | 82,000 |
| 2 | 125,000 | 30,000 | 95,000 |
| 3 | 140,000 | 32,000 | 108,000 |
| 4 | 155,000 | 35,000 | 120,000 |
| 5 | 175,000 | 38,000 | 137,000 |

**Payback Period (PBP)**

The Payback Period determines how quickly the initial investment is recovered.

Formula:
PBP = Year before recovery + (Remaining Investment / Next Year NCF)

Cumulative Cash Flow:
- Year 1 = 82,000
- Year 2 = 177,000

Calculation:
PBP = 1 + (155,000 − 82,000) / 95,000
PBP = 1.77 years ≈ **1 year 9 months**

The investment is recovered in less than 2 years, indicating low financial risk.

**Net Present Value (NPV)**

Formula:
PV = NCF / (1 + r)ᵗ
NPV = ΣPV − Initial Investment
(Discount Rate = 12%)

**Table 4.5: Calculation of NPV**

| Year | NCF (NPR) | Present Value (NPR) |
|------|-----------|-------------------|
| 1 | 82,000 | 73,214 |
| 2 | 95,000 | 75,732 |
| 3 | 108,000 | 76,873 |
| 4 | 120,000 | 76,263 |
| 5 | 137,000 | 77,751 |

NPV Calculation:
NPV = 73,214 + 75,732 + 76,873 + 76,263 + 77,751 − 155,000
NPV ≈ **NPR 224,833**

Positive NPV confirms the project is financially viable.

**Internal Rate of Return (IRR)**

The IRR is the discount rate at which NPV = 0. Using financial calculation methods:
IRR ≈ **46.3%**

This is significantly higher than the required return (12–15%), indicating high profitability.

**Table 4.6: Summary of Financial Metrics**

| Metric | Value |
|--------|-------|
| Payback Period | 1 year 9 months |
| Net Present Value | NPR 224,833 |
| Internal Rate of Return | 46.3% |

**Commercial Value and Selling Price**

From a commercial perspective, Complainify has strong market potential. Its key features include:
- AI-powered auto-categorization of complaints
- Sentiment analysis with priority boosting
- Real-time analytics dashboard
- Email notification system
- CSV report export
- Improved university administration workflow efficiency

The system can be marketed to:
- Universities and colleges
- Schools and educational institutions
- Government education departments
- Corporate HR departments

**Estimated Selling Price:** NPR 125,000 per system

### Conclusion

The economic analysis shows that Complainify is financially sound. It offers:
- Short payback period (1 year 9 months)
- High NPV (NPR 224,833)
- Strong IRR (46.3%)
- Low operational cost

Thus, the system ensures quick investment recovery, low financial risk, and long-term sustainability, making it a highly feasible and profitable solution for educational institutions.
