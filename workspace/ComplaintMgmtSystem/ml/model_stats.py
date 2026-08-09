"""Model statistics shared by the admin dashboard and the study notebooks.

Single source of truth for the accuracy cards AND the correlation matrix, so
the website and the notebooks always agree:
    model_cards()      -> accuracy / macro-F1 / per-class for category,
                          sentiment and priority (reads ml/training_log.json +
                          ml/sentiment_training_log.json)
    correlation_matrix() -> Pearson correlations between numeric complaint
                          signals from data/sentiment_dataset.csv
"""

import csv
import json
import math
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAT_LOG = os.path.join(BASE, 'ml', 'training_log.json')
SP_LOG = os.path.join(BASE, 'ml', 'sentiment_training_log.json')
DATASET = os.path.join(BASE, 'data', 'sentiment_dataset.csv')

SENT_ENC = {'positive': 1, 'neutral': 0, 'negative': -1}
PRI_ENC = {'Low': 1, 'Medium': 2, 'High': 3}


def _load(path):
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def _norm_per_class(rows):
    out = []
    for r in rows or []:
        out.append({
            'label': r.get('label') or r.get('category') or r.get('class', '?'),
            'precision': r.get('precision', 0),
            'recall': r.get('recall', 0),
            'f1': r.get('f1', 0),
            'support': r.get('support', r.get('samples', 0)),
        })
    return out


def model_cards():
    """Return the same metrics the notebooks show, for the admin dashboard."""
    cat = _load(CAT_LOG)
    sp = _load(SP_LOG)
    cards = [
        {
            'name': 'Category',
            'accuracy': cat.get('accuracy'),
            'macro_f1': cat.get('macro_f1'),
            'last_trained': cat.get('last_trained'),
            'train_samples': cat.get('train_samples'),
            'test_samples': cat.get('test_samples'),
            'per_class': _norm_per_class(cat.get('per_class')),
            'history': cat.get('history', []),
        },
        {
            'name': 'Sentiment',
            'accuracy': (sp.get('sentiment') or {}).get('accuracy'),
            'macro_f1': (sp.get('sentiment') or {}).get('macro_f1'),
            'last_trained': sp.get('last_trained'),
            'train_samples': sp.get('train_samples'),
            'test_samples': sp.get('test_samples'),
            'per_class': _norm_per_class((sp.get('sentiment') or {}).get('per_class')),
            'history': sp.get('history', []),
        },
        {
            'name': 'Priority',
            'accuracy': (sp.get('priority') or {}).get('accuracy'),
            'macro_f1': (sp.get('priority') or {}).get('macro_f1'),
            'last_trained': sp.get('last_trained'),
            'train_samples': sp.get('train_samples'),
            'test_samples': sp.get('test_samples'),
            'per_class': _norm_per_class((sp.get('priority') or {}).get('per_class')),
            'history': [],
        },
    ]
    return [c for c in cards if c['accuracy'] is not None]


def _pearson(xs, ys):
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if sx == 0 or sy == 0:
        return 0.0
    return cov / (sx * sy)


def correlation_matrix():
    """Pearson matrix of the numeric complaint signals in the dataset.

    Rows/cols: sentiment (positive=+1, neutral=0, negative=-1),
    priority (low=1, medium=2, high=3), text length, polarity score.
    """
    features = {
        'sentiment': [], 'priority': [], 'text_length': [], 'polarity': [],
    }
    with open(DATASET, encoding='utf-8') as f:
        for r in csv.DictReader(f):
            sent = r.get('sentiment_label', '').strip().lower()
            pri = r.get('priority', '').strip()
            if sent not in SENT_ENC or pri not in PRI_ENC:
                continue
            try:
                pol = float(r.get('polarity_score', 0))
            except ValueError:
                pol = 0.0
            features['sentiment'].append(SENT_ENC[sent])
            features['priority'].append(PRI_ENC[pri])
            features['text_length'].append(len(r.get('complaint_text', '')))
            features['polarity'].append(pol)

    names = list(features.keys())
    matrix = []
    for a in names:
        row = []
        for b in names:
            row.append(round(_pearson(features[a], features[b]), 3))
        matrix.append(row)
    return {'labels': names, 'matrix': matrix, 'rows': len(features['sentiment'])}
