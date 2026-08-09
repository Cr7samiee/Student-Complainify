# Student-Complainify

AI-powered Student Complaint Classification and Management System. A Flask web app that automatically categorizes complaints into 10 categories using a from-scratch Multinomial Naive Bayes classifier, detects emotional tone using a lexicon-based sentiment analyzer, and provides role-based dashboards for both students and admins.

---

## How It Works

```
Student submits complaint
        |
        v
[Flask app.py] --> [Classifier]  --> category + confidence + tier
                --> [Sentiment]  --> trained NB (env.py) | rule fallback
                --> [Priority]   --> trained NB (env.py) | keyword fallback
        |
        v
Priority + sentiment stored alongside the complaint
        |
        v
Admin dashboard: complaint lists, sentiment badges, /admin/analysis heatmaps
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

#### 2. Sentiment & Priority (ML-first, `ml/sentiment.py` + `ml/priority.py`)
- **12,000-row dataset** (`data/sentiment_dataset.csv`): hand-written curation + template-driven synthesis where sentiment and priority ground truth are decided at generation time (not by any classifier)
- Two from-scratch Multinomial Naive Bayes models (`data/sentiment_model.json`, `data/priority_model.json`) trained with the same machinery as the category classifier — train with `python ml/train_sentiment_priority.py`
- `ml/env.py` lazy-loads both models; sentiment/priority consult the model **first** and fall back to the previous lexicon/keyword rules when confidence is low or models are absent — the app runs even before training
- Measured on the held-out 20%: sentiment ≈ **99.7%** test accuracy, priority ≈ **99.2%** — priority labels come from a deterministic, explainable text rule (severity/urgency markers for High, deadline/window topics for Medium, appreciation always Low), so the model learns exactly what the rule says
- Admin **Sentiment × Priority** page (`/admin/analysis`): problem heatmap (category × priority), green/positive counter-matrix, and the *closed-but-still-hurting* list (Resolved + Negative + High/Medium)

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
| Category model | Multinomial Naive Bayes (from scratch) |
| Category training samples | 7204 (80%) / 1806 (20%) |
| Category accuracy | ~96% |
| Sentiment dataset | 12,000 rows (claude + synth) — ground truth built in |
| Sentiment model | Multinomial NB, test accuracy ~99.7%, macro-F1 ~0.997 |
| Priority model | Multinomial NB, test accuracy ~99.2%, macro-F1 ~0.992 |
| TF-IDF / sklearn / nltk | Not used — everything from scratch |

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
│   ├── sentiment.py              # ML-first sentiment engine (from-scratch rule fallback, no VADER)
│   ├── validate_data.py          # Data validation gate (before training)
│   ├── model_registry.py        # Model versioning: save/load/list latest
│   ├── retrain.py               # Full pipeline: collect → validate → append → train → version
│   ├── env.py                   # Lazy-load trained sentiment/priority models (fallback wiring)
│   ├── train_sentiment_priority.py # Train sentiment + priority NBs on data/sentiment_dataset.csv
│   ├── gen_analysis.py          # Reads MySQL → live_analysis.json (heatmaps, pink list)
│   ├── sentiment_training_log.json # Single source of truth for report/notebook metrics
│   ├── models/                   # Versioned models + manifest.json (registry)
│   └── reports/                  # Validation reports (JSON)
├── data/                         # ★ Training data + encoders
│   ├── train_dataset.csv         # Collected, labeled complaints (source of truth)
│   ├── sentiment_dataset.csv     # 12k rows, tagged sentiment + priority ground truth
│   ├── sentiment_model.json      # Trained sentiment NB
│   ├── priority_model.json        # Trained priority NB
│   ├── live_analysis.json         # Cached live heatmap snapshot (regenerated by gen_analysis.py)
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
| `09_sentiment_dataset_authoring.ipynb` | How the 12k sentiment/priority dataset was authored (ground truth built in) |
| `10_sentiment_priority_models.ipynb` | Train + per-class evaluation of both models vs the rule-based baseline |
| `11_live_pipeline_heatmap.ipynb` | Live MySQL heatmaps: problem matrix, green zone, closed-but-still-hurting |
| `12_accuracy_dashboard.ipynb` | **Same numbers as the admin dashboard**: category/sentiment/priority accuracy cards + correlation matrix (via `ml/model_stats.py`) |

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
