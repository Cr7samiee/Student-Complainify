"""Lazy-loading env for the trained SENTIMENT and PRIORITY models.

Keeps the rule-based modules (sentiment.py / priority.py) as the public
interface: they consult this module first and fall back to heuristics when
the trained models are absent or unconfident.
"""

import os

from classifier import MultinomialNB

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SENT_MODEL_PATH = os.path.join(BASE, 'data', 'sentiment_model.json')
PRI_MODEL_PATH = os.path.join(BASE, 'data', 'priority_model.json')

SENT_DECODER = {0: 'positive', 1: 'neutral', 2: 'negative'}
SENT_LABEL = {'positive': 'Positive', 'neutral': 'Neutral', 'negative': 'Negative'}
PRI_DECODER = {0: 'Low', 1: 'Medium', 2: 'High'}

_sent_model = None
_pri_model = None
_sent_attempted = False
_pri_attempted = False


def _load(path):
    if not os.path.isfile(path):
        return None
    try:
        return MultinomialNB.load(path)
    except Exception as e:
        print(f"[ENV MODEL LOAD] {path}: {e}")
        return None


def get_sentiment_model():
    global _sent_model, _sent_attempted
    if not _sent_attempted:
        _sent_model = _load(SENT_MODEL_PATH)
        _sent_attempted = True
    return _sent_model


def get_priority_model():
    global _pri_model, _pri_attempted
    if not _pri_attempted:
        _pri_model = _load(PRI_MODEL_PATH)
        _pri_attempted = True
    return _pri_model


def ml_sentiment(text):
    """Return {'label': 'Positive'|..., 'label_lower': ..., 'confidence': float}
    or None when the model is unavailable."""
    model = get_sentiment_model()
    if model is None:
        return None
    pred, probs = model.predict_with_proba(text)
    label = SENT_LABEL[SENT_DECODER[pred]]
    return {'label': label, 'label_lower': SENT_DECODER[pred],
            'confidence': round(probs[pred], 4)}


def ml_priority(text):
    """Return {'priority': 'High'|'Medium'|'Low', 'confidence': float}
    or None when the model is unavailable."""
    model = get_priority_model()
    if model is None:
        return None
    pred, probs = model.predict_with_proba(text)
    return {'priority': PRI_DECODER[pred], 'confidence': round(probs[pred], 4)}
