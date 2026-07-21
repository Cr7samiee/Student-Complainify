# Project Plan — Complainify

> AI-Based Student Complaint Analysis & Management System
> Project-VI (BIT356CO) | Bachelor in Information Technology | Purbanchal University

---

## ✅ Completed Tasks

### 1. Dataset Preparation
- [x] Combined multiple raw datasets into `processed_dataset_4500.csv` (~9000 rows)
- [x] Added 15 hand-written hackathon/event examples
- [x] Performed stratified 80/20 split → `train_dataset.csv` (7204 rows) + `test_dataset.csv` (1806 rows)
- [x] Encoded categories (10 + Other) and cleaned text (lowercase, punctuation, URLs, stopwords)

### 2. Naive Bayes Classifier (`train/classifier.py`)
- [x] Multinomial Naive Bayes implemented **entirely from scratch** (no sklearn)
- [x] Custom stemmer with **25 rules** (no nltk)
- [x] Bigram features (e.g., `wifi_router`, `exam_schedule`)
- [x] Laplace smoothing (alpha=1.0), min_df=3
- [x] Log-space computation to avoid underflow
- [x] **Three-tier confidence system:**
  - `auto` (≥90%) — confident classification
  - `suggest` (60-89%) — probable but uncertain
  - `unknown` (<60%) — too ambiguous
- [x] Rule-based override: hackathon/event keywords auto-classify
- [x] `categorize(text)` → `{category, confidence, tier}`

### 3. Sentiment Analyzer (`train/sentiment.py`)
- [x] Lexicon-based approach — **no training needed, no VADER**
- [x] ~150 words with intensity scores (negative: -1 to -3, positive: +1 to +3)
- [x] Negation handling: `not`, `never`, `no` flip polarity
- [x] Intensifier amplification: `very`, `extremely` boost 1.5×
- [x] `analyze_sentiment(text)` → `{label, score, sub_label}`
- [x] `sentiment_priority_boost(sentiment, priority)` → auto-promotes Low→Medium, Medium→High for Negative tone

### 4. Flask Backend (`backend/app.py`)
- [x] Student routes: register, login, submit complaint, dashboard, settings
- [x] Admin routes: login, dashboard (live data), complaints list, detail, assign, update status, validate, resend email, report, CSV export, settings
- [x] Complaint submission auto-detects: category (Naive Bayes) + sentiment + priority boost
- [x] AJAX live AI preview during complaint typing
- [x] Forgot/Reset password with OTP system (6-digit, 10-min expiry, stored in DB)
- [x] Email notifications (SMTP) for submission, assignment, status changes + graceful skip if unconfigured
- [x] Session-based authentication with role redirection
- [x] REST API endpoint: `/api/predict`

### 5. Admin Dashboard (Live Data)
- [x] Total complaints, resolved, pending, in-progress (from DB)
- [x] Mean resolution time (avg hours from resolved_at — created_at)
- [x] Critical count (High priority unresolved)
- [x] Category breakdown with real percentages
- [x] Sentiment distribution bar (Positive / Neutral / Negative)
- [x] Critical alerts list (actual high-priority complaints)
- [x] Recent activity table with all real complaints

### 6. Database (`complainify.sql`)
- [x] Tables: `users`, `complaints`, `otps`
- [x] `complaints` includes: ticket_id, category, priority, status, sentiment, sentiment_score, assigned_to, assigned_at, resolved_at, admin_notes, validated, email_sent
- [x] `otps` includes: email, otp, expires_at, used flag
- [x] Sample data with Ram Sharma (student) + Admin User + 3 sample complaints

### 7. Templates (Frontend)
- [x] Landing page (index.html) with features, how-it-works, about sections
- [x] Student login, register, dashboard, complaint detail, settings
- [x] Admin login, register, dashboard, complaints list, complaint detail, report, settings
- [x] Submit complaint form with AI category preview
- [x] Track complaint by ticket ID
- [x] Forgot password + reset password with OTP
- [x] Sentiment badges (green/yellow/red/gray) on all complaint listings
- [x] Flash messages with auto-dismiss animation
- [x] Responsive sidebars and bottom navigation

### 8. Notebooks
- [x] `naive_bayes_training.ipynb` — Full pipeline: load, split, train, evaluate (96% acc, confusion matrix, precision/recall/F1 all from scratch)
- [x] `sentiment_analysis.ipynb` — Distribution charts, per-class examples, priority boost analysis

### 9. Testing & Verification
- [x] All GET routes return 200
- [x] Login/Registration flows work
- [x] Forgot password generates OTP in DB
- [x] Reset password verifies OTP and updates
- [x] Complaint submission auto-classifies and detects sentiment
- [x] Admin dashboard shows live (not fake) data
- [x] No dependency on sklearn, nltk, or VADER

### 10. Documentation
- [x] README.md with architecture, setup, test credentials, API endpoints, performance metrics
- [x] LaTeX report (`report.tex`) — 8 chapters, 22 tables, 60+ test cases
- [x] Notebooks rewritten with human-sounding markdown

---

## 🚧 Remaining Backend & Data Tasks

- [ ] **Unit tests** — pytest/unittest for classifier, sentiment analyzer, and API routes
- [ ] **Deployment** — Deploy on Render / PythonAnywhere / VPS
- [ ] **Prod config** — Move `secret_key`, `DB_CONFIG`, `SMTP_CONFIG` to `.env` or env vars
- [ ] **CSV import for admins** — Bulk upload complaints from CSV file
- [x] **Priority filter on admin complaints page** — Filter by High/Medium/Low
- [x] **Pagination** — Add pagination to admin complaints list (20/page, Prev/Next + page numbers)
- [x] **Category/sentiment filter on dashboard charts** — Click chart segment to filter complaints
- [ ] **Data augmentation** — Generate more training samples for low-represented categories
- [ ] **Model persistence** — Save trained model parameters to JSON (avoid retrain on every restart)
- [ ] **File upload** — Allow students to attach images/docs to complaints

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5, CSS3, JavaScript (ES6), Tailwind CSS (via CDN) |
| Backend | Python 3.12, Flask 3.x |
| Database | MySQL 8.0 (via XAMPP) |
| ML (Classifier) | Multinomial Naive Bayes — from scratch |
| ML (Sentiment) | Lexicon-based — from scratch (no VADER) |
| Email | smtplib + SMTP (Gmail) |
| Data Processing | pandas, numpy |
| Visualization | matplotlib |
| Version Control | Git + GitHub |

---

## Key Files

| File | Purpose |
|------|---------|
| `backend/app.py` | Flask routes, auth, DB, classifier + sentiment integration |
| `train/classifier.py` | Naive Bayes: stemmer, tokenizer, bigrams, categorize() |
| `train/sentiment.py` | Lexicon analyzer: analyze_sentiment(), sentiment_priority_boost() |
| `train/predict.py` | CLI predictor tool |
| `TrainDataset/naive_bayes_training.ipynb` | Training pipeline + evaluation |
| `TrainDataset/sentiment_analysis.ipynb` | Sentiment distribution analysis |
| `TrainDataset/train_dataset.csv` | 7204 training samples |
| `TrainDataset/test_dataset.csv` | 1806 test samples |
| `complainify.sql` | Full DB schema + sample data |
| `report.tex` | LaTeX project report (1318 lines) |
| `README.md` | Setup guide + architecture overview |

---

## Performance

| Metric | Value |
|--------|-------|
| Classifier Algorithm | Multinomial Naive Bayes (from scratch) |
| Training samples | 7204 (80%) |
| Test samples | 1806 (20%) |
| Vocabulary | ~3600 unique tokens + bigrams |
| Accuracy (test) | ~96% |
| Macro F1 | ~96% |
| Sentiment method | Lexicon-based (150+ words, from scratch) |
| Confidence tiers | auto (≥90%), suggest (60-89%), unknown (<60%) |

---

## Test Credentials

| Role | Email | Password |
|------|-------|----------|
| Student | `ram@gmail.com` | `pass123` |
| Admin | `admin@complainify.edu` | `admin123` |
