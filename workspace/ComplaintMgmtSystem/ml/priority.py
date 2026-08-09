import re

import env

_RISK_PATTERNS = re.compile(
    r'\b(harass\w*|stole|theft|robbery|threaten\w*|unsafe|abuse|assault|'
    r'unhygienic|filthy|spoiled|rotten|stale\s+food|overcharg\w*|leak\w*|'
    r'no\s+(?:response|reply|action|update)|never\s+(?:fixed|resolved|addressed))\b',
    re.IGNORECASE
)

_URGENT_PATTERNS = re.compile(
    r'\b(not\s+work(?:ing)?|doesn.?t\s+work|dont\s+work|wont\s+work|'
    r'broken|crack\w*|malfunction\w*|delay(?:s|ed)?|urgent|asap|'
    r'immediately|emergency|deadline|exam|fees?\s+confirm)\b',
    re.IGNORECASE
)

_APPRECIATION = re.compile(
    r'\b(thank|appreciate|grateful|excellent|wonderful|amazing|great|'
    r'fixed|resolved|solved|helpful|happy|satisfied|delighted|impressed)\b',
    re.IGNORECASE
)

# ML priority is used when its confidence is at least this high.
ML_CONFIDENCE = 0.55


def compute_priority_rules(text, sentiment_label, sentiment_score, anomaly=None):
    """Weighted, explainable priority score (pure rules, no ML).

    Returns (priority, score, reason).
    score is clamped to >= 0. High >= 3, Medium 1-2, Low <= 0.
    """
    score = 0
    reasons = []

    if sentiment_label == 'Negative' and sentiment_score <= -0.3:
        score += 2
        reasons.append('strong negative tone')
    elif sentiment_label == 'Negative':
        score += 1
        reasons.append('negative tone')

    if _RISK_PATTERNS.search(text):
        score += 2
        reasons.append('high-risk wording')

    if _URGENT_PATTERNS.search(text):
        score += 1
        reasons.append('urgent issue')

    if anomaly and anomaly.get('is_anomaly'):
        score += 2
        reasons.append('flagged as anomalous')

    if sentiment_label == 'Positive' and _APPRECIATION.search(text):
        score -= 1
        reasons.append('positive tone')

    score = max(score, 0)
    priority = 'High' if score >= 3 else ('Medium' if score >= 1 else 'Low')
    reason = ', '.join(reasons) if reasons else 'baseline'

    return priority, score, reason


# Representative weighted score for each ML priority class, so the app's
# score field keeps the same meaning as the rules (High >= 3, Medium 1-2, Low <= 0).
_ML_SCORE = {'High': 3, 'Medium': 2, 'Low': 0}


def compute_priority(text, sentiment_label, sentiment_score, anomaly=None):
    """Trained-model-first priority engine.

    Consults the Multinomial NB priority model (data/priority_model.json)
    when its confidence is >= ML_CONFIDENCE; falls back to the weighted
    rules otherwise. Anomaly-flagged complaints always go through the rules
    so the manual-review boost is never lost.

    Returns (priority, score, reason).
    """
    if not (anomaly and anomaly.get('is_anomaly')):
        ml = env.ml_priority(text)
        if ml and ml['confidence'] >= ML_CONFIDENCE:
            return (ml['priority'], _ML_SCORE[ml['priority']],
                    f'Multinomial NB model (confidence {ml["confidence"]*100:.0f}%)')

    return compute_priority_rules(text, sentiment_label, sentiment_score, anomaly)