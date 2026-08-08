# Rebuild `notebook/Complainify_AI_Study.ipynb` (self-contained, error-free)

## Goal
Rewrite the notebook from scratch, keeping the 10-part teaching structure, fixing every bug found by executing all 21 cells in order.

## Verified diagnosis (ran all cells top-to-bottom in a simulated kernel)
- All cells execute — but with these real defects + misleading outputs:
  1. **Cell 9**: hardcoded `E:/Project-VI/...` CSV path → FileNotFoundError on any other machine/CWD.
  2. **Cell 24**: claims `"bad" is in lexicon` but `bad` was missing from `NEGATIVE_WORDS` → demo prints "score 0.0, Neutral" while text says otherwise.
  3. **Cell 26**: unknown-word log pollutes with stopwords (`the`, `and`, `are`).
  4. **Cell 28**: `analyze_sentiment_fuzzy` = empty `def ...: pass` stub — runs but teaches nothing.
  5. **Cell 6**: printed "Bigrams: wifi_not_work …" — wrong; `not` is a stopword, real bigrams are `wifi_work`, `work_librari`.
  6. **Cells 33-35**: duplicate log-load code, matplotlib import inside try in cell 34 relies on cell 33 having run.
  7. **Cell 20/30**: sentiment engine and PART 8 priority don't match production (`ml/priority.py` compute_priority with reason string).
  8. Stray garbage lines in cell 32 area ("from ml import priority" duplicates) from earlier partial edits.

## Rebuild plan (35 cells, kernel python3, no outputs)
Same order/structure as current (Parts 1-10), all code self-contained, fixes:

### Part 1 — Dataset structure
- `CAT_DECODER` (10 cats) as-is; add a comment that it mirrors `data/encoders/category_decoder.json`.

### Part 2 — Preprocessing (cells: STOPWORDS / stemmer / clean_and_tokenize)
- Keep code; fix the printed bigram example to use the real computed tokens.

### Part 3 — Load & 80/20 split (replaces buggy cell 9)
- Portable path probe: `data/train_dataset.csv`, `../data/`, `../../data/`, `../../../data/` — error message lists candidates.
- Read CSV, distribution printout, `CAT_NAME_TO_ID` encode, `random.seed(42)` shuffle, 80/20, 200-row `sample_data`.

### Part 4 — MultinomialNB from scratch
- `MultinomialNB` class (same math: prior log, Laplace smoothing `(c+α)/(N+α|V|)`, log-space sums, softmax proba), train on `sample_data`, `predict()` helper printing all 10 class probabilities.

### Part 5 — Evaluation metrics
- Mini labeled test set → accuracy, per-class P/R/F1, macro-F1.

### Part 6 — Sentiment: lexicons + engine + demo
- Lexicons: ADD missing `'bad': -1`, `'poor': -1`, `'foul': -2`, `'appalling': -3` so demos are truthful.
- Engine with negation/intensifier state machine; demo table.

### Part 7 — New-word handling
- Cell 24: fix example text to match real results (`bad` now known; `atrocious`/`deplorable` stay unknown).
- Solution 1: `unknown_log` now filtered (skip stopwords) — only real unknowns listed.
- Solution 2: replace `pass` stub with real `SYNONYM_MAP` + `analyze_sentiment_synonym()` fallback (`atrocious→terrible` etc.) + demo.

### Part 8 — Complete pipeline (sentiment → priority)
- `RISK/URGENT/APPRECIATION` regexes + `compute_priority(text, label, score, anomaly=False)` → `(priority, score, reason)` — mirrors `ml/priority.py`.
- `show_pipeline()` runs category + sentiment + priority on 2-3 complaints.

### Part 9 — Real performance (training_log.json)
- ONE loader cell: portable probe (incl. absolute fallback), stores `LOG` (+raise if missing).
- Accuracy-over-time chart (matplotlib if present, else text bars); per-class P/R/F1 + samples chart; confusion-matrix-style text summary — each uses `LOG` from loader (markdown notes "run loader cell first").
- Fix: matplotlib imported once in a single cell guarded by try/except.

### Part 10 — Live status
- Re-reads `ml/training_log.json` fresh (independent of Part 9), prints admin-dashboard-identical line, history trend bars.

### Final summary cell (markdown) — alive, accurate, no hardcoded numbers.

## Files changed
1. `workspace/ComplaintMgmtSystem/notebook/Complainify_AI_Study.ipynb` — regenerated (nbformat 4.5, python3 kernel, cells rebuilt; execution outputs kept empty).

## Out of scope
- Other notebooks (Complainify_AI_7120/9782...) untouched.
- `ml/`, `backend/`, DB — untouched. (Part 8 mirrors ml/priority.py behavior but stays self-contained per your choice.)
- No external libraries added (matplotlib only *if installed*).

## Notes
- Path probe works from any CWD; the absolute E:/ fallback stays because that's this repo's location.
- Teacher-friendly: keeps from-scratch NB + lexicon demo style, now accurate and runnable in one pass.