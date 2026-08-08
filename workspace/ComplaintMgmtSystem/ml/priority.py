import re

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


def compute_priority(text, sentiment_label, sentiment_score, anomaly=None):
    """Weighted, explainable priority score.

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