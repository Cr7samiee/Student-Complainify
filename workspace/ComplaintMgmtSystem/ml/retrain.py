import sys, os, json, csv, math, random, re
import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from classifier import MultinomialNB
import validate_data
import model_registry

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRAIN_PATH = os.path.join(BASE, 'data', 'train_dataset.csv')
ENC_PATH = os.path.join(BASE, 'data', 'encoders', 'category_decoder.json')
LOG_PATH = os.path.join(BASE, 'ml', 'training_log.json')
CAT_ENC_PATH = os.path.join(BASE, 'data', 'encoders', 'category_encoder.json')
PRI_ENC_PATH = os.path.join(BASE, 'data', 'encoders', 'priority_encoder.json')


def load_json(p):
    with open(p) as f:
        return json.load(f)


with open(CAT_ENC_PATH) as f:
    cat_encoder = json.load(f)


def collect_dataset_rows():
    """Rows == collected CSV (trusted base) + admin-confirmed DB complaints."""
    all_rows = []
    with open(TRAIN_PATH, encoding='utf-8') as f:
        all_rows += list(csv.DictReader(f))

    # Pull only admin-confirmed complaints straight from the DB.
    # Student-submitted rows keep their auto-predicted category but are
    # NOT eligible until an admin sets category_confirmed=1 (human label).
    new_rows = []
    try:
        if os.path.isfile(os.path.join(BASE, '.env')):
            try:
                from dotenv import load_dotenv
                load_dotenv(os.path.join(BASE, '.env'))
            except ImportError:
                pass
        import pymysql
        dbcfg = dict(
            host=os.environ.get('DB_HOST', '127.0.0.1'),
            port=int(os.environ.get('DB_PORT', 3306)),
            user=os.environ.get('DB_USER', 'root'),
            password=os.environ.get('DB_PASSWORD', ''),
            database=os.environ.get('DB_NAME', 'complainify'),
            charset='utf8mb4'
        )
        conn = pymysql.connect(**dbcfg, cursorclass=pymysql.cursors.DictCursor)
        cur = conn.cursor()
        cur.execute(
            "SELECT ticket_id, subject, description, category, priority "
            "FROM complaints WHERE category_confirmed = 1")
        for r in cur.fetchall():
            if r['category'] in cat_encoder:
                new_rows.append({
                    'text': (r['subject'] or '') + ' ' + (r['description'] or ''),
                    'category': r['category'],
                    'priority': r.get('priority') or 'Medium',
                    'source': 'db_verified',
                })
        cur.close(); conn.close()
    except Exception as db_err:
        print(f"[RETRAIN DB WARNING] could not load confirmed complaints from DB: {db_err}", file=sys.stderr)

    return all_rows, new_rows


def append_new_rows(new_rows, existing_rows):
    """Validate and append previously unseen confirmed rows to the CSV."""
    existing_texts = [r['text'] for r in existing_rows]
    validated = validate_data.validate_rows(new_rows, existing_texts=existing_texts)
    valid = validated['valid']
    if not valid:
        return validated, 0

    with open(TRAIN_PATH, encoding='utf-8') as f:
        present = {r['text'].strip().lower() for r in csv.DictReader(f)}
    pri_enc = load_json(PRI_ENC_PATH)

    added = 0
    fieldnames = ['text', 'category', 'priority', 'source', 'category_encoded', 'priority_encoded']
    with open(TRAIN_PATH, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if os.path.getsize(TRAIN_PATH) == 0:
            writer.writeheader()
        for r in valid:
            norm = r['text'].strip().lower()
            if norm in present:
                continue
            pri = r.get('priority') if r.get('priority') in pri_enc else 'Medium'
            txt = re.sub(r'\s+', ' ', r['text']).strip()
            writer.writerow({
                'text': txt,
                'category': r['category'],
                'priority': pri,
                'source': 'db_verified',
                'category_encoded': cat_encoder[r['category']],
                'priority_encoded': pri_enc[pri],
            })
            present.add(norm)
            added += 1
    return validated, added


def main():
    all_rows, new_rows = collect_dataset_rows()

    validated, added_count = append_new_rows(new_rows, all_rows)
    summary = validated['summary']

    # Reload the CSV: it now also contains the newly appended rows.
    with open(TRAIN_PATH, encoding='utf-8') as f:
        all_rows = list(csv.DictReader(f))

    # Dedupe by exact text - prevents train/test leakage that inflates accuracy
    seen_texts = set()
    all_rows = [r for r in all_rows if not (r['text'] in seen_texts or seen_texts.add(r['text']))]

    random.shuffle(all_rows)
    split = int(len(all_rows) * 0.8)
    train_rows, test_rows = all_rows[:split], all_rows[split:]

    train_texts = [r['text'] for r in train_rows]
    train_labels = [int(r['category_encoded']) for r in train_rows]
    test_texts = [r['text'] for r in test_rows]
    test_labels = [int(r['category_encoded']) for r in test_rows]

    model = MultinomialNB()
    model.fit(train_texts, train_labels)

    correct = 0
    per_class = {}
    with open(ENC_PATH) as f:
        cat_decoder = {int(k): v for k, v in json.load(f).items()}
    for cid, cname in cat_decoder.items():
        per_class[cname] = {'tp': 0, 'fp': 0, 'fn': 0, 'total': 0}

    for i, text in enumerate(test_texts):
        pred, probs = model.predict_with_proba(text)
        true_label = test_labels[i]
        if pred == true_label:
            correct += 1
        cat_name = cat_decoder.get(pred, 'Other')
        true_cat_name = cat_decoder.get(true_label, 'Other')
        per_class[true_cat_name]['total'] += 1
        if pred == true_label:
            per_class[cat_name]['tp'] += 1
        else:
            per_class[cat_name]['fp'] += 1
            if true_cat_name not in per_class:
                per_class[true_cat_name] = {'tp': 0, 'fp': 0, 'fn': 0, 'total': 0}
            per_class[true_cat_name]['fn'] += 1

    MIN_SAMPLES = 3
    class_metrics = []
    for cat, counts in per_class.items():
        if counts['total'] < MIN_SAMPLES:
            class_metrics.append({'category': cat, 'precision': None, 'recall': None, 'f1': None, 'samples': counts['total'], 'note': 'insufficient data'})
        else:
            p = counts['tp'] / max(counts['tp'] + counts['fp'], 1)
            r = counts['tp'] / max(counts['tp'] + counts['fn'], 1)
            f1 = 2 * p * r / max(p + r, 1)
            class_metrics.append({'category': cat, 'precision': round(p, 4), 'recall': round(r, 4), 'f1': round(f1, 4), 'samples': counts['total']})

    valid_metrics = [m for m in class_metrics if m['f1'] is not None]
    macro_f1 = round(sum(m['f1'] for m in valid_metrics) / max(len(valid_metrics), 1), 4) if valid_metrics else None

    total_test = len(test_texts)
    if total_test < 10:
        accuracy_val = None
        note = 'too few test samples for reliable accuracy'
    else:
        accuracy_val = round(correct / total_test * 100, 2)
        note = None

    metrics = {
        'accuracy': accuracy_val,
        'macro_f1': macro_f1,
        'train_samples': len(train_texts),
        'test_samples': total_test,
        'per_class': class_metrics,
        'new_rows_appended': added_count,
        'validated_total': summary['total_checked'],
        'validated_rejected': summary['rejected'],
    }

    # Versioned save + registry + legacy active copy
    record = model_registry.save_version(model, metrics=metrics)
    version_id = record['id']

    log_data = {}
    if os.path.isfile(LOG_PATH):
        with open(LOG_PATH) as f:
            log_data = json.load(f)
    history = log_data.get('history', [])
    history.append({'date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'accuracy': accuracy_val})

    new_log = {
        'last_version': version_id,
        'last_trained': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'train_samples': len(train_texts),
        'test_samples': total_test,
        'accuracy': accuracy_val,
        'note': note,
        'macro_f1': macro_f1,
        'per_class': class_metrics,
        'new_verified_used': added_count,
        'history': history[-20:],
    }
    with open(LOG_PATH, 'w') as f:
        json.dump(new_log, f, indent=2)

    print(json.dumps(new_log))


if __name__ == '__main__':
    main()