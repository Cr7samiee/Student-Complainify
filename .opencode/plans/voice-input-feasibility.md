# Feasibility Study — Voice Input with Auto Sentiment + Priority (Complainify)

Status: **STUDY ONLY — no implementation yet.**

## 1. Objective
Let a student *speak* their complaint instead of typing. The transcript should
flow through the existing NLP pipeline so the student immediately sees
predicted **category, sentiment, and priority**, and the final submit stores
all the same columns currently computed from text (`priority_score`,
`priority_reason`, `sentiment`, `sentiment_score`, category).

## 2. Existing plumbing (verified in code — no backend rework needed for analysis)
- `ml/sentiment.py::analyze_sentiment(text)` → `{label, sub_label, score, ...}`
- `ml/priority.py::compute_priority(text, sentiment_label, sentiment_score, anomaly)` → `(priority, score, reason)`
- `ml/classifier.py::categorize / predict_top3` (auto category, AI preview exists)
- Submit flow already stores all of these (`backend/app.py` INSERT, `priority_score`/`priority_reason` columns exist in DB)
- `submit_complaint.html` already has a live "AI Predictions" box driven by `oninput="previewCategory(this.value)"` — mic only needs to *fill the textarea* and re-trigger this

**Only missing pieces:**
1. Speech→text capture (client or server)
2. A small `/api/analyze` endpoint returning sentiment+priority for the live preview
3. UI chips for Sentiment + Priority in the preview box

## 3. Voice-to-text options — comparison

### Option A: Browser Web Speech API (SpeechRecognition) — RECOMMENDED
| Pro | Con |
|---|---|
| Zero server changes, zero packages | Works only in Chrome / Edge / Safari (not Firefox) |
| Free (Google online-only on Chrome) | Needs internet (Google service) |
| Multi-language (`en-IN`, `hi-IN`, `kn-IN`…) via one attribute | Best effort accuracy in noisy environments |
| Instant transcript streaming (`interimResults`) | Not usable on plain `http://` except `localhost`/127.0.0.1 (mic permission requires secure context) |
| ~40 lines of JS in the template | Accent/domain words ("wifi", "charger", "canteen") need dict fallback |

- Implementation shape: `<button id="micBtn">` toggles `webkitSpeechRecognition || SpeechRecognition`,
  `continuous: true`, `interimResults: true`, `lang: 'en-IN'`; onfinal transcript → fill textarea →
  trigger `previewCategory()`; also autopopulate subject from first sentence (optional toggle).
- Feasibility: HIGH. Lowest risk, deployable in a day.

### Option B: Browser STT with language chip (English / Hindi / Kannada…)
- Same Web Speech API, `recognition.lang` switched per chip.
- For this college context (`en-IN` covers most complaint vocab) or as a quick multi-language demo.
- Feasibility: HIGH (still zero backend).

### Option C: OpenAI Whisper, server-side (openai-whisper or faster-whisper)
| Aspect | Con |
|---|---|
| Best accuracy, language coverage incl. Nepali/Hindi dialects | +150 MB model download, heavier CPU use per request |
| Works in every browser | Backend must accept `audio/webm` blob → transcribe → return text |
| Offline capable | Slower (2-10 s per clip on CPU) unless GPU |
| Production-grade | New dependency + async job handling for good UX |

- Deployment must also be HTTPS for mic capture in Safari / non-localhost.
- Feasibility: MEDIUM-HIGH; right if the study later demands accuracy in mixed-language speech.

## 4. Live analysis flow (for the demo)
1. User clicks mic → speaks → transcript fills Description (+ Subject from first ~8 words)
2. Existing `oninput` fires → `previewCategory()` → AI category bars (already live today)
3. **New**: parallel `POST /api/analyze` returns
   `{ category:{name,confidence}, sentiment:{label,sub_label,score}, priority:{label,score,reason}, anomaly:{is_anomaly} }`
   rendered as colored chips under the textarea (e.g. `😠 Angry / Frustrated`, `🔴 High — strong negative tone`)
4. Submit → unchanged server flow stores everything (already implemented)

## 5. Files affected (when approved)
| File | Change |
|---|---|
| `frontend/templates/submit_complaint.html` | Mic button + STT JS (~45 ln) + chips in preview box |
| `backend/app.py` | Add `/api/analyze` route (~8 ln) |
| `frontend/static/` (optional) | tiny `voice.js` if kept separate instead of inline |
| Option C only: `requirements.txt`, `.env.example` | whisper model config |

## 6. Risks & mitigations
- **Secure context**: if deployed over plain HTTP, SpeechRecognition will not start except on localhost → document quick demo = `python app.py` on localhost; for LAN deploy → HTTPS cert or use Whisper variant.
- **Accuracy of campus vocabulary**: add a tiny post-correct map ("wifi"→"WiFi", "charger"→"charger" etc.) and keep `interimResults` on for live correction.
- **Multiple languages**: STT is per-session; enforce one `lang` at a time (selector chip) to avoid mixed-language transcripts.
- **No change to existing pipeline/DB** — voice simply produces the same `text` the pipeline already consumes; zero data-model risk.

## 7. Decision ledger (from conversation)
- Approach: **study only** — no implementation now.
- STT engine: decided after study; Recommendation A (Web Speech, en-IN) for MVP.
- Subject autofill: "study only" — listed as optional refinement, not committed.

## 8. Suggested next step (when approved)
Implement Option A end-to-end on `submit_complaint.html` + `/api/analyze`, verify with the
existing test-client harness (POST text → same columns as typed complaints), then decide
whether B or C is needed based on demo feedback.