# Student-Complainify

AI-Based Student Complaint Analysis & Management System — a Flask web app that classifies complaints, predicts priority, and provides an admin analytics dashboard.

---

## 🚀 Setup Instructions

### Prerequisites
- [Python 3.x](https://www.python.org/) (or [Anaconda](https://www.anaconda.com/))
- [XAMPP](https://www.apachefriends.org/) (for MySQL)
- Git

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/Cr7samiee/Student-Complainify.git
cd Student-Complainify
```

### 2️⃣ Set Up Python Environment
Using conda (recommended):
```bash
conda create -n complaint-system python=3.10
conda activate complaint-system
pip install flask pymysql pandas numpy
```

Or using venv:
```bash
python -m venv venv
venv\Scripts\activate    # Windows
pip install flask pymysql pandas numpy
```

### 3️⃣ Start MySQL (XAMPP)
1. Open **XAMPP Control Panel**
2. Click **Start** on **MySQL**
3. (Optional) Start **Apache** for phpMyAdmin

### 4️⃣ Import Database
Open phpMyAdmin at `http://localhost/phpmyadmin` or run:
```bash
mysql -u root < complainify.sql
```
This creates the `complainify` database with `users` and `complaints` tables + sample data.

### 5️⃣ Run the Application
```bash
cd backend
python app.py
```

### 6️⃣ Open in Browser
Go to **http://127.0.0.1:5000**

---

### 🔑 Test Credentials

| Role | Email | Password |
|------|-------|----------|
| Student | `ram@gmail.com` | `pass123` |
| Admin | `admin@complainify.edu` | `admin123` |

---

### 📂 Project Structure
```
Student-Complainify/
├── backend/app.py              # Flask server
├── frontend/templates/         # HTML pages
├── frontend/static/css/        # Styles
├── TrainDataset/               # Dataset + preprocessing
│   ├── training_dataset.csv    # 1800 labeled complaints
│   ├── preprocess_data.py      # Clean & encode script
│   ├── processed_dataset.csv   # Cleaned + encoded output
│   ├── encoders/               # JSON category/priority maps
│   ├── analysis.py             # Console analysis
│   └── generate_report.py      # HTML chart report
└── complainify.sql             # MySQL schema + sample data
```

---
