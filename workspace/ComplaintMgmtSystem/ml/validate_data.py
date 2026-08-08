import os, re, json, time
from collections import Counter

BASE = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(BASE, 'reports')
ENC_PATH = os.path.normpath(os.path.join(BASE, '..', 'data', 'encoders', 'category_encoder.json'))

MIN_TOKENS = 3
MAX_CHARS = 4000


def _load_known_categories():
    with open(ENC_PATH) as f:
        encoder = json.load(f)
    return set(encoder.keys())


def _tokens(text):
    return re.findall(r'[a-z0-9]+', (text or '').lower())


def validate_row(row, known_categories, seen_texts):
    """Returns (ok, reason, normalized_text)."""
    text = (row.get('text') or '').strip()
    category = (row.get('category') or '').strip()

    if not text:
        return False, 'empty_text', None
    if len(text) > MAX_CHARS:
        return False, 'text_too_long', None
    tokens = _tokens(text)
    if len(tokens) < MIN_TOKENS:
        return False, 'too_short', None
    if category not in known_categories:
        return False, 'unknown_category', None

    norm = re.sub(r'\s+', ' ', text.lower())
    if norm in seen_texts:
        return False, 'duplicate_text', None

    # junk/spam heuristics
    repeated = re.findall(r'(.)\1{4,}', norm)
    if repeated:
        return False, 'repetitive_chars', None
    char_counter = Counter(norm)
    letter_count = sum(1 for ch in norm if ch.isalpha())
    if letter_count > 0 and len(norm) > 0 and letter_count / len(norm) < 0.3:
        return False, 'gibberish', None

    return True, None, norm


def validate_rows(rows, existing_texts=None, report_name=None):
    """Gate rows before they may enter training.

    Returns dict: {valid: [...], rejected: [{row, reason}], summary}
    Writes a JSON validation report into train/reports/.
    """
    known_categories = _load_known_categories()
    seen_texts = set(t for t in (existing_texts or []))
    valid = []
    rejected = []

    for row in rows:
        ok, reason, norm = validate_row(row, known_categories, seen_texts)
        if ok:
            valid.append(row)
            seen_texts.add(norm)
        else:
            rejected.append({'row': row, 'reason': reason})

    report = {
        'validated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'total_checked': len(rows),
        'valid': len(valid),
        'rejected': len(rejected),
        'rejected_by_reason': dict(Counter(r['reason'] for r in rejected)),
        'rejected_samples': rejected[:50],
    }

    if report_name is None:
        report_name = f'validation_report_{time.strftime("%Y%m%d_%H%M%S")}.json'
    os.makedirs(REPORTS_DIR, exist_ok=True)
    report_path = os.path.join(REPORTS_DIR, report_name)
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)

    return {'valid': valid, 'rejected': rejected, 'summary': report, 'report_path': report_path}