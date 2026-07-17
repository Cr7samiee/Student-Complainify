import csv, json, os, re
from collections import OrderedDict

INPUT = os.path.join(os.path.dirname(__file__), 'training_dataset.csv')
OUTPUT = os.path.join(os.path.dirname(__file__), 'processed_dataset.csv')
ENCODER_DIR = os.path.join(os.path.dirname(__file__), 'encoders')

os.makedirs(ENCODER_DIR, exist_ok=True)

def clean_text(text):
    text = text.strip().lower()
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('\u2013', '-').replace('\u2014', '--')
    text = text.replace('\u2018', "'").replace('\u2019', "'")
    text = text.replace('\u201c', '"').replace('\u201d', '"')
    text = text.replace('\u2026', '...')
    return text

def build_encoder(values):
    seen = OrderedDict()
    for v in values:
        if v not in seen:
            seen[v] = len(seen)
    return seen

def apply_encoder(values, mapping):
    return [mapping[v] for v in values]

with open(INPUT, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f'Loaded {len(rows)} rows')

texts = [clean_text(r['complaint_text']) for r in rows]
categories = [r['category'] for r in rows]
priorities = [r['priority'] for r in rows]
sources = [r['source'] for r in rows]

# Deduplicate: keep first occurrence of each unique text (remove all duplicate texts)
from collections import Counter
text_groups = {}
for i, t in enumerate(texts):
    if t not in text_groups:
        text_groups[t] = []
    text_groups[t].append(i)

unique_indices = []
for t, indices in text_groups.items():
    # Majority vote for category and priority among duplicates
    cat_votes = Counter(categories[i] for i in indices)
    pri_votes = Counter(priorities[i] for i in indices)
    # Keep the index of the majority class (break ties by first occurrence)
    best_cat = cat_votes.most_common(1)[0][0]
    best_pri = pri_votes.most_common(1)[0][0]
    for i in indices:
        if categories[i] == best_cat and priorities[i] == best_pri:
            unique_indices.append(i)
            break
    else:
        unique_indices.append(indices[0])

removed = len(texts) - len(unique_indices)
texts = [texts[i] for i in unique_indices]
categories = [categories[i] for i in unique_indices]
priorities = [priorities[i] for i in unique_indices]
sources = [sources[i] for i in unique_indices]
print(f'Removed {removed} duplicate texts, kept {len(texts)} unique rows')

cat_encoder = build_encoder(categories)
pri_encoder = build_encoder(priorities)

cat_encoded = apply_encoder(categories, cat_encoder)
pri_encoded = apply_encoder(priorities, pri_encoder)

# Save processed CSV
with open(OUTPUT, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['text', 'category', 'priority', 'source', 'category_encoded', 'priority_encoded'])
    for txt, cat, pri, src, cat_e, pri_e in zip(texts, categories, priorities, sources, cat_encoded, pri_encoded):
        writer.writerow([txt, cat, pri, src, cat_e, pri_e])

print(f'Saved {OUTPUT}')

# Save encoders as JSON
cat_encoder_path = os.path.join(ENCODER_DIR, 'category_encoder.json')
pri_encoder_path = os.path.join(ENCODER_DIR, 'priority_encoder.json')

with open(cat_encoder_path, 'w') as f:
    json.dump(dict(cat_encoder), f, indent=2)

with open(pri_encoder_path, 'w') as f:
    json.dump(dict(pri_encoder), f, indent=2)

# Save reverse mapping for Flask
cat_rev = {v: k for k, v in cat_encoder.items()}
pri_rev = {v: k for k, v in pri_encoder.items()}

with open(os.path.join(ENCODER_DIR, 'category_decoder.json'), 'w') as f:
    json.dump(cat_rev, f, indent=2)

with open(os.path.join(ENCODER_DIR, 'priority_decoder.json'), 'w') as f:
    json.dump(pri_rev, f, indent=2)

print(f'Encoders saved to {ENCODER_DIR}')
print(f'\nCategory mapping: {dict(cat_encoder)}')
print(f'Priority mapping: {dict(pri_encoder)}')
print('\nDone!')
