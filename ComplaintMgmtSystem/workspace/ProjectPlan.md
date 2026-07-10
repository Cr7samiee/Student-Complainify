# 🛠 Technology Stack

The AI-Based Student Complaint Analysis & Management System is developed using modern web technologies and Artificial Intelligence techniques to provide an efficient and intelligent complaint management platform.

---

## Frontend

The client-side interface is developed using:

- HTML5
- CSS3
- JavaScript (ES6)

These technologies provide a responsive and interactive user interface for both students and administrators.

---

## Backend

The server-side application is developed using:

- Python 3.x
- Flask Framework

Flask manages:

- User Authentication
- Complaint Management
- AI Integration
- Email Notifications
- Database Connectivity
- File Upload Handling

---

## Database

The system uses:

- MySQL

The database stores:

- Student Information
- Administrator Accounts
- Complaint Details
- AI Prediction Results
- Complaint Status
- Resolution Notes
- File Attachments

---

# 🤖 Artificial Intelligence Module

The AI module automatically analyzes every complaint submitted by students.

The complaint title and description undergo text preprocessing before being analyzed using machine learning and natural language processing techniques.

The AI module performs:

- Complaint Category Prediction
- Complaint Priority Prediction
- Sentiment Analysis

---

## Complaint Classification

The project implements the **Multinomial Naive Bayes Classification Algorithm** completely **from scratch**, without using machine learning libraries such as Scikit-learn.

The implementation includes:

- Text Cleaning
- Tokenization
- Stopword Removal
- Vocabulary Creation
- Word Frequency Calculation
- Prior Probability Calculation
- Likelihood Estimation
- Laplace Smoothing
- Posterior Probability Calculation
- Final Class Prediction

The classifier predicts:

### Complaint Category

- Academics
- IT Support
- Administration
- Hostels
- Fees / Finance
- Library
- Maintenance
- Transport
- Security / Discipline

### Complaint Priority

- High
- Medium
- Low

Implementing Naive Bayes manually provides a better understanding of probability-based classification algorithms and satisfies academic learning objectives in Artificial Intelligence and Data Mining.

---

# 😊 Sentiment Analysis

The project uses **VADER (Valence Aware Dictionary and sEntiment Reasoner)** for sentiment analysis.

VADER is a rule-based Natural Language Processing (NLP) model specifically designed to analyze sentiment in short textual content such as comments, reviews, and complaint messages.

For every complaint, VADER calculates sentiment scores and classifies the complaint into one of three categories:

- Positive
- Neutral
- Negative

The sentiment information helps administrators quickly identify dissatisfied students and prioritize complaints that require immediate attention.

---

# 📊 Training Dataset

The project uses **two labeled datasets** combined into a unified training set:

### Dataset Sources

| File | Source | Rows | Labels |
|------|--------|------|--------|
| `TrainDataset/university_complaint_triage_dataset.csv` | Primary complaint triage data | 800 | category + priority |
| `TrainDataset/university_query_test.csv` | Student query data | 1000 | category + priority |

### Combined Dataset (`workspace/train/training_dataset.csv`)

- **Total rows**: 1800 cleaned, labeled complaints
- **9 categories**: Academics, IT Support, Administration, Hostels, Fees / Finance, Library, Maintenance, Transport, Security / Discipline
- **3 priority levels**: High (547), Medium (589), Low (664)
- **Pipeline**: `workspace/train/preprocess_dataset.py` handles loading, cleaning, category normalization, text cleaning, and deduplication

### Preprocessing Steps

The preprocessing script (`workspace/train/preprocess_dataset.py`) performs:
1. Column standardization (complaint_text, category, priority)
2. Category name normalization across datasets (e.g., "Academic Office" → "Academics", "Finance Office" → "Fees / Finance")
3. Text cleaning (remove URLs, special characters, lowercase)
4. Empty row removal
5. Final CSV export

---

# 📊 Data Handling (Pandas)

The project uses **Pandas** for data processing and dataset management post-preprocessing.

Pandas is responsible for:

- Reading the preprocessed Training Dataset
- Cleaning New Complaint Data
- Feature Preparation for Naive Bayes
- CSV File Management
- Report Generation

---

# ✉️ Email Integration

The system automatically sends email notifications using Python.

Emails are sent when:

- Complaint Submitted Successfully
- Complaint Status Updated
- Complaint Resolved

Each email contains:

- Ticket ID
- Complaint Status
- Resolution Summary (if available)

This feature improves transparency and keeps students informed throughout the complaint resolution process.

---

# 🔄 AI Workflow

```text
Student Submits Complaint
           │
           ▼
Text Preprocessing
(Cleaning, Tokenization, Stopword Removal)
           │
           ▼
Naive Bayes Classifier
(Implemented From Scratch)
           │
     ┌─────┴─────┐
     ▼           ▼
Category     Priority
Prediction   Prediction
           │
           ▼
VADER Sentiment Analysis
           │
           ▼
Store Results in MySQL
           │
           ▼
Display on Admin Dashboard
```

---

# 📁 Project Structure

```text
ComplaintMgmtSystem/
│
├── TrainDataset/
│   ├── training_dataset.csv
│   ├── university_complaint_triage_dataset.csv
│   ├── university_query_test.csv
│   └── university_queries_test.csv
│
├── workspace/
│   ├── ProjectPlan.md
│   └── train/
│       ├── preprocess_dataset.py
│       └── training_dataset.csv
│
└── ProjectPlan.md (moved inside workspace/)
```

---

# 📚 Python Libraries

The project uses the following Python libraries:

| Library | Purpose |
|----------|---------|
| Flask | Backend Web Framework |
| Pandas | Data Processing |
| NLTK | Text Preprocessing |
| VADER Sentiment | Sentiment Analysis |
| PyMySQL | MySQL Database Connection |
| Flask-Mail | Email Notifications |
| NumPy | Numerical Operations |
| Regex (re) | Text Cleaning |
| Collections | Word Frequency Calculation |
| Math | Probability Computation |

---

# 🎯 Development Tools

- Visual Studio Code
- Python 3.x
- Flask
- MySQL
- HTML5
- CSS3
- JavaScript
- Git
- GitHub

---

# 🎓 AI & Data Mining Concepts Used

- Text Mining
- Natural Language Processing (NLP)
- Text Preprocessing
- Tokenization
- Stopword Removal
- Bag of Words
- Multinomial Naive Bayes Classification
- Laplace Smoothing
- Probability-Based Prediction
- Sentiment Analysis using VADER
- Data Cleaning
- Data Visualization (Reports & Dashboard)
- Database Management

---

# 💡 Project Highlights

- Responsive Web Application
- Student & Admin Modules
- Complaint Tracking with Ticket ID
- AI-Based Complaint Categorization
- Priority Prediction using Naive Bayes
- Sentiment Analysis using VADER
- Email Notification System
- File Upload Support
- Dashboard Analytics
- Report Generation
- MySQL Database Integration
- Manual Implementation of Naive Bayes (Without Scikit-learn)

This should support:
1.	User Registration and Authentication: Secure multi-role registration and login system for Students and Administrators, with email-based password reset and account verification features.
2.	Complaint Submission System: Students can submit complaints related to academics, examinations, infrastructure, administration, or faculty issues by providing complaint details and supporting information through an online portal.
3.	Anonymous Complaint Submission: Students can choose to submit complaints anonymously, ensuring privacy and encouraging the reporting of sensitive issues without fear of identification.
4.	AI-Based Complaint Classification: The system automatically analyzes complaint text using Artificial Intelligence and Natural Language Processing techniques to classify complaints into appropriate categories and departments.
5.	Sentiment Analysis: The system performs sentiment analysis on complaint content and identifies whether the complaint expresses positive, neutral, or negative sentiments to better understand the severity of issues.
6.	Automatic Priority Assignment: Based on complaint content, sentiment, and predefined rules, the system automatically assigns priority levels such as High, Medium, or Low to assist administrators in handling urgent complaints efficiently.
7.	Complaint Status Tracking: Students can monitor the status of their complaints, including Submitted, Under Review, In Progress, Resolved, or Rejected, ensuring transparency throughout the complaint resolution process.
8.	Search and Filter Functionality: Administrators can search and filter complaints based on category, department, priority, status, date, or student information for efficient complaint management.
9.	Dashboard and Analytics: Role-specific dashboards provide complaint statistics, category-wise distributions, monthly trends, priority analysis, and graphical reports to support data-driven decision-making.
10.	Email Notification System: Automated email notifications are sent for complaint submission confirmations, status updates, high-priority complaint alerts, and resolution notifications using Flask-Mail and SMTP services.
11.	PDF and Excel Report Generation: Administrators can generate and export complaint reports in PDF and Excel formats containing complaint summaries, statistics, and analytical insights.
12.	Decision Support System: The system utilizes Data Mining and AI techniques to identify complaint patterns, frequently occurring issues, and departmental performance trends, assisting management in making informed decisions.

# 💻 Development Environment

The project is developed using **Visual Studio Code** as the primary code editor and **Anaconda** for managing the Python environment and project dependencies. The backend application runs on the **Flask development server**, while **MySQL** (via XAMPP) is used solely as the database management system.

The application is **not developed inside the XAMPP `htdocs` directory**, as it is a Python Flask application rather than a PHP application. Instead, the project is maintained in a dedicated workspace, allowing better project organization and easier management of Python libraries.

**Development Setup:**

- Code Editor: Visual Studio Code
- Python Environment: Anaconda
- Backend Framework: Flask
- Frontend: HTML5, CSS3, JavaScript
- Database Server: MySQL (XAMPP)
- Version Control: Git & GitHub