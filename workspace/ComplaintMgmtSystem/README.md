# Student-Complainify

AI-powered Student Complaint Classification and Management System. A Flask web app that automatically categorizes complaints into 10 categories using a from-scratch Multinomial Naive Bayes classifier, detects emotional tone using a lexicon-based sentiment analyzer, and provides role-based dashboards for both students and admins.

---

## How It Works

```
Student submits complaint
        |
        v
[Flask app.py] --> [Classifier] --> category + confidence + tier
                --> [Sentiment]   --> sentiment + score
        |
        v
Priority boosted if negative sentiment detected
        |
        v
Admin dashboard shows classified + sentiment-tagged complaints
```

### Core Components

#### 1. Naive Bayes Classifier (`train/classifier.py`)
- Multinomial Naive Bayes written from scratch (no sklearn)
- Custom stemmer with 25 rules (no nltk)
- Bigram features (e.g. "wifi_router", "exam_schedule")
- Laplace smoothing (alpha=1.0), min_df=3
- Trained on 7204 samples, tested on 1806 (80/20 stratified split)
- Three-tier confidence:
  - **Auto** (>=90%): confident classification
  - **Suggest** (60-89%): probable but uncertain
  - **Unknown** (<60%): too ambiguous
- Rule-based override: complaints mentioning hackathon/event keywords auto-classify to Hackathon/Event

#### 2. Sentiment Analyzer (`train/sentiment.py`)
- Lexicon-based approach — no training needed
- ~150 words with intensity scores (negative: -1 to -3, positive: +1 to +3)
- Negation handling: words like "not", "never" flip polarity
- Intensifier amplification: "very", "extremely" boost intensity 1.5x
- Returns: Positive, Neutral, or Negative with a numeric score
- Priority boost: Negative tone auto-promotes Low→Medium, Medium→High

#### 3. Flask App (`backend/app.py`)
- Student routes: register, login, submit complaint, view own complaints
- Admin routes: dashboard with charts, manage complaints, assign, resolve
- Auto-detects category + sentiment on complaint submission
- Sentiment priority boost applied before saving to DB
- REST API endpoints for integration

#### 4. Database (`complainify.sql`)
- MySQL via XAMPP
- Tables: `users` (students + admins), `complaints` (with category, sentiment, priority, assigned_to, admin_notes, etc.)
- Sample data included with 15 test complaints

---

## Performance

| Metric | Value |
|--------|-------|
| Algorithm | Multinomial Naive Bayes (from scratch) |
| Training samples | 7204 (80%) |
| Test samples | 1806 (20%) |
| Vocabulary | ~3600 unique tokens + bigrams |
| Accuracy | ~96% |
| Macro F1 | ~96% |
| Sentiment method | Lexicon-based (150+ words) |

---

## Project Structure

```
Student-Complainify/
├── backend/
│   ├── app.py                    # Flask server (routes, auth, DB)
│   └── __init__.py
├── frontend/
│   └── templates/
│       ├── admin/                # Admin pages (dashboard, complaints)
│       ├── student/              # Student pages (dashboard, submit)
│       ├── auth/                 # Login / Register
│       └── complaint_detail.html # Detail view with sentiment badge
├── train/
│   ├── classifier.py             # Naive Bayes (from scratch)
│   ├── sentiment.py              # Lexicon sentiment analyzer
│   └── predict.py                # CLI predictor tool
├── TrainDataset/
│   ├── naive_bayes_training.ipynb            # Full training pipeline
│   ├── naive_bayes_training_executed.ipynb   # Executed with outputs
│   ├── sentiment_analysis.ipynb              # Sentiment distribution
│   ├── sentiment_analysis_executed.ipynb     # Executed with outputs
│   ├── train_dataset.csv         # 7204 labeled complaints (training)
│   ├── test_dataset.csv          # 1806 labeled complaints (testing)
│   └── processed_dataset_4500.csv # Full dataset with added examples
├── complainify.sql               # DB schema + sample data
└── README.md
```

---

## Setup Instructions

### Prerequisites
- Python 3.10+ (or Anaconda)
- XAMPP (for MySQL)
- Git

### 1. Clone & Set Up
```bash
git clone https://github.com/Cr7samiee/Student-Complainify.git
cd Student-Complainify
conda create -n complaint-system python=3.10
conda activate complaint-system
pip install flask pymysql pandas numpy matplotlib jupyter
```

### 2. Start MySQL (XAMPP)
- Open XAMPP Control Panel → Start MySQL

### 3. Import Database
```bash
mysql -u root < complainify.sql
```

### 4. (Optional) Train the Classifier
Notebooks are pre-executed, but to retrain:
```bash
jupyter notebook TrainDataset/naive_bayes_training.ipynb
jupyter notebook TrainDataset/sentiment_analysis.ipynb
```

### 5. Run the App
```bash
cd backend
python app.py
```
Visit **http://127.0.0.1:5000**

### 6. (Optional) Email Notifications
Set environment variables for SMTP:
```powershell
$env:SMTP_USER = "your@email.com"
$env:SMTP_PASS = "your-app-password"
```
If unset, email sending is silently skipped.

---

## Test Credentials

| Role | Email | Password |
|------|-------|----------|
| Student | `ram@gmail.com` | `pass123` |
| Admin | `admin@complainify.edu` | `admin123` |

---

## Notebooks

### `naive_bayes_training.ipynb`
Full ML pipeline from scratch:
1. Loads `train_dataset.csv` + `test_dataset.csv`
2. Custom stemmer + tokenizer + bigram feature extraction
3. Multinomial Naive Bayes implementation (log-space, Laplace smoothing)
4. Confusion matrix, precision, recall, F1 calculated manually
5. Bar charts for per-category accuracy
6. Tests 24 sample complaints — 22/24 pass (~92%)

### `sentiment_analysis.ipynb`
Sentiment distribution analysis:
1. Lexicon-based scoring on complaint text
2. Distribution charts (bar + pie) showing Positive/Neutral/Negative split
3. Examples from each sentiment category
4. Priority boost mapping table

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Redirect based on role |
| GET/POST | `/auth/login` | Login page |
| GET/POST | `/auth/register` | Student registration |
| GET | `/student/dashboard` | Student complaint list |
| GET/POST | `/student/submit` | Submit complaint (auto-classify + auto-sentiment) |
| GET | `/admin/dashboard` | Admin analytics dashboard |
| GET | `/admin/complaints` | All complaints with filters |
| POST | `/admin/assign` | Assign complaint to admin |
| POST | `/admin/resolve` | Mark complaint resolved |
| POST | `/admin/notes` | Update admin notes |
| GET | `/api/categories` | Category distribution (JSON) |
| GET | `/api/priorities` | Priority distribution (JSON) |
