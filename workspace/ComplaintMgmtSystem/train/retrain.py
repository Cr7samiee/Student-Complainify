import sys, os, json, csv, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from classifier import MultinomialNB

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRAIN_PATH = os.path.join(BASE, 'TrainDataset', 'train_dataset.csv')
NEW_PATH = os.path.join(BASE, 'TrainDataset', 'new_complaints.csv')
TEST_PATH = os.path.join(BASE, 'TrainDataset', 'test_dataset.csv')
ENC_PATH = os.path.join(BASE, 'TrainDataset', 'encoders', 'category_decoder.json')
LOG_PATH = os.path.join(BASE, 'train', 'training_log.json')
MODEL_PATH = os.path.join(BASE, 'TrainDataset', 'model_params.json')

with open(os.path.join(BASE, 'TrainDataset', 'encoders', 'category_encoder.json')) as f:
    cat_encoder = json.load(f)
with open(ENC_PATH) as f:
    cat_decoder = {int(k): v for k, v in json.load(f).items()}

all_rows = []
with open(TRAIN_PATH, encoding='utf-8') as f:
    all_rows += list(csv.DictReader(f))
if os.path.isfile(NEW_PATH):
    with open(NEW_PATH, encoding='utf-8') as f:
        for r in csv.DictReader(f):
            if r['category'] in cat_encoder:
                r['category_encoded'] = cat_encoder[r['category']]
                all_rows.append(r)

random.shuffle(all_rows)
split = int(len(all_rows) * 0.8)
train_rows, test_rows = all_rows[:split], all_rows[split:]

train_texts = [r['text'] for r in train_rows]
train_labels = [int(r['category_encoded']) for r in train_rows]
test_texts = [r['text'] for r in test_rows]
test_labels = [int(r['category_encoded']) for r in test_rows]

model = MultinomialNB()
model.fit(train_texts, train_labels)
model.save(MODEL_PATH)

correct = 0
per_class = {}
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

log_data = {}
if os.path.isfile(LOG_PATH):
    with open(LOG_PATH) as f:
        log_data = json.load(f)

history = log_data.get('history', [])

total_test = len(test_texts)
if total_test < 10:
    accuracy_val = None
    accuracy_display = None
    note = 'too few test samples for reliable accuracy'
else:
    accuracy_val = round(correct / total_test * 100, 2)
    accuracy_display = accuracy_val
    note = None

history.append({'date': __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M'),
                'accuracy': accuracy_val})

new_log = {
    'last_trained': __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'train_samples': len(train_texts),
    'test_samples': total_test,
    'accuracy': accuracy_val,
    'accuracy_display': accuracy_display,
    'note': note,
    'macro_f1': macro_f1,
    'per_class': class_metrics,
    'history': history[-20:]
}

with open(LOG_PATH, 'w') as f:
    json.dump(new_log, f, indent=2)

print(json.dumps(new_log))
