import csv, json, os
from collections import Counter

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'TrainDataset')
cat_dec = json.load(open(os.path.join(BASE, 'encoders', 'category_decoder.json')))
rows = list(csv.DictReader(open(os.path.join(BASE, 'processed_dataset.csv'))))

for cat_enc in sorted(set(r['category_encoded'] for r in rows)):
    cat_rows = [r for r in rows if r['category_encoded'] == cat_enc]
    words = []
    for r in cat_rows:
        words.extend(r['text'].split())
    top5 = Counter(words).most_common(5)
    print(f'{cat_dec[cat_enc]} ({len(cat_rows)} docs): {[w for w,_ in top5]}')

print('\n--- Sample Academics texts ---')
for r in rows:
    if r['category_encoded'] == '2':
        print(f'  - {r["text"][:100]}')
