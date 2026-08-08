import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_analyzer = SentimentIntensityAnalyzer()

_APPRECIATION = re.compile(
    r'\b(thank|appreciate|grateful|excellent|wonderful|amazing|great|'
    r'fixed|resolved|solved|helpful|happy|satisfied|delighted|impressed)\b',
    re.IGNORECASE
)

# Genuine complaint markers only — NOT bare topic nouns (wifi/water/power...)
# so positive feedback that mentions a topic ("wifi fixed, very helpful") stays positive.
_COMPLAINT_WORDS = re.compile(
    r'\b(complaint|complain|problem|issue|fix|repair|broken|damage|leak|'
    r'not\s+work(?:ing)?|not\s+function|stole|theft|delay|not\s+good)\b',
    re.IGNORECASE
)

_NEG_PATTERNS = re.compile(
    r'\b(not\s+work(?:ing)?|doesn.?t\s+work|dont\s+work|wont\s+work|'
    r'not\s+function(?:ing)?|stole|theft|robbery|harass\w*|'
    r'no\s+(?:response|reply|action|update)|'
    r'no\s+one\s+(?:listens|cares|responds)|'
    r'nobody\s+(?:listens|cares|responds)|'
    r'never\s+(?:fixed|resolved|addressed|solved)|'
    r'nothing\s+(?:done|works?|happens)|'
    r'stale|spoiled|rotten|foul|smelly|infest\w*|'
    r'leak(?:ing|s|ed)?|broken|crack(?:ed)?|dirty|filthy|malfunction\w*|'
    r'overcharg\w*|rude|unsafe|cheat\w*|unhygienic|abuse|threaten\w*|'
    r'refus\w*|ignor\w*|delay(?:s|ed)?)\b',
    re.IGNORECASE
)

# Polite informational requests ("please share the syllabus", "how can I…") —
# these are not appreciation, force to Neutral instead of Positive.
_REQUEST = re.compile(
    r'\b(?:please|kindly|pls)\s+(?:share|send|provide|give|inform|update|forward|'
    r'attach|tell|arrange|schedule|check|confirm|review|consider)\b|'
    r'\bhow\s+(?:do|can|should)\s+[a-z]|'
    r'\b(?:can|could)\s+(?:you|u)\s+please|'
    r'\bi\s+(?:want|need|would\s+like)\b',
    re.IGNORECASE
)


def analyze_sentiment(text):
    scores = _analyzer.polarity_scores(text)
    compound = scores['compound']

    if compound > -0.05 and _NEG_PATTERNS.search(text):
        compound = min(compound, -0.1)

    if compound > 0 and _REQUEST.search(text) and not _APPRECIATION.search(text):
        compound = 0.0

    if compound >= 0.05 and _COMPLAINT_WORDS.search(text) and not _APPRECIATION.search(text):
        compound = 0.0

    if compound <= -0.5:
        label, sub_label = 'Negative', 'Angry / Frustrated'
    elif compound <= -0.05:
        label, sub_label = 'Negative', 'Dissatisfied'
    elif compound >= 0.5:
        label, sub_label = 'Positive', 'Appreciative'
    elif compound >= 0.05:
        label, sub_label = 'Positive', 'Satisfied'
    else:
        label, sub_label = 'Neutral', 'Informational'

    return {
        'label': label,
        'sub_label': sub_label,
        'score': round(compound, 3),
        'neg_words': 0,
        'pos_words': 0,
        'total_sentiment_words': 0,
        'negations': 0,
        'vader': scores,
    }


def sentiment_priority_boost(sentiment_label, current_priority):
    boosts = {
        'Negative': {'Low': 'Medium', 'Medium': 'High', 'High': 'High'},
        'Neutral': {'Low': 'Low', 'Medium': 'Medium', 'High': 'High'},
        'Positive': {'Low': 'Low', 'Medium': 'Medium', 'High': 'High'},
    }
    return boosts.get(sentiment_label, {}).get(current_priority, current_priority)
