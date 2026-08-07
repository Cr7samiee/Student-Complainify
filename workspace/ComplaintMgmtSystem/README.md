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

#### 1. Naive Bayes Classifier (`ml/classifier.py`)
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

#### 2. Sentiment Analyzer (`ml/sentiment.py`)
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
│   ├── app.py                    # Flask server (routes, auth, DB, ML APIs)
│   └── mcp_server.py             # MCP tools (predict, search)
├── frontend/
│   └── templates/
│       ├── admin/                # Admin pages (dashboard, complaints, training)
│       ├── student/              # Student pages (dashboard, submit)
│       └── base.html             # Shared layout
├── ml/                           # Machine-learning package (production pipeline)
│   ├── classifier.py             # MultinomialNB (from scratch) + categorize()
│   ├── sentiment.py              # Lexicon sentiment analyzer
│   ├── predict.py                # CLI predictor tool
│   ├── validate_data.py          # Data validation gate (before training)
│   ├── model_registry.py        # Model versioning: save/load/list latest
│   ├── retrain.py               # Full pipeline: collect → validate → append → train → version
│   ├── models/                   # Versioned models + manifest.json (registry)
│   └── reports/                  # Validation reports (JSON)
├── data/                         # ★ Training data + encoders
│   ├── train_dataset.csv         # Collected, labeled complaints (source of truth)
│   ├── test_dataset.csv          # Held-out test set
│   ├── model_params.json         # Active model copy (back-compat)
│   └── encoders/                 # category + priority encoders/decoders
├── notebook/                      # Companion notebooks for each ML topic
├── complainify.sql               # DB schema + sample data (idempotent)
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
Notebooks are pre-executed, but to retrain from the CLI:
```bash
python ml/retrain.py            # collect CSV + confirmed DB rows → validate → train → new model version
python ml/predict.py "WiFi slow" # test the active model
```
Or trigger a retrain from the admin UI (Training page → Retrain Model), or schedule it
by setting `RETRAIN_SCHEDULE_HOURS` (e.g. `168` for weekly) in `.env`.

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

## Notebooks (`notebook/subfunctions/`)

Study notebooks, each focused on one ML topic and **executed** so outputs are visible:

| Notebook | Topic |
|----------|-------|
| `01_dataset_structure.ipynb` | CSV columns + category decoder |
| `02_preprocessing.ipynb` | Stopwords, stemmer, tokenizer/normalization |
| `03_train_test_split.ipynb` | Load real data + 80/20 split |
| `04_naive_bayes.ipynb` | MultinomialNB from scratch (fit/predict) |
| `05_evaluation_metrics.ipynb` | Accuracy, precision, recall, F1 on the test set |
| `06_sentiment_analysis.ipynb` | Lexicon sentiment → priority pipeline |
| `07_model_performance.ipynb` | Live `training_log.json` accuracy + per-class charts |
| `08_model_lifecycle.ipynb` | **Production data lifecycle**: validation gate → registry → versioned retraining |

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
