import csv, os, random
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRAIN_PATH = os.path.join(BASE, 'TrainDataset', 'train_dataset.csv')

with open(TRAIN_PATH, encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

from collections import defaultdict
by_cat = defaultdict(list)
for r in rows:
    by_cat[r['category']].append(r)

target = 750
augmented = []
for cat in ['Canteen', 'Library']:
    existing = by_cat[cat]
    needed = target - len(existing)
    if needed <= 0: continue
    templates = [e['text'] for e in existing]
    substitutes = {
        'bad': ['terrible', 'awful', 'poor', 'horrible', 'disappointing', 'unacceptable', 'frustrating'],
        'good': ['great', 'excellent', 'wonderful', 'fantastic', 'satisfactory'],
        'slow': ['sluggish', 'delayed', 'lagging', 'unresponsive'],
        'clean': ['hygienic', 'sanitary', 'tidy', 'spotless'],
        'dirty': ['filthy', 'unhygienic', 'messy', 'unclean'],
        'help': ['assist', 'support', 'aid', 'resolve'],
        'problem': ['issue', 'concern', 'difficulty', 'trouble'],
    }
    for i in range(needed):
        t = random.choice(templates)
        for word, alts in substitutes.items():
            if word in t:
                t = t.replace(word, random.choice(alts), 1)
                break
        words = t.split()
        if len(words) > 5:
            idx = random.randint(1, len(words)-2)
            words.insert(idx, random.choice(['very', 'extremely', 'quite', 'really', 'so']))
        aug_text = ' '.join(words)
        new_row = dict(existing[0])
        new_row['text'] = aug_text
        augmented.append(new_row)

if augmented:
    with open(TRAIN_PATH, 'a', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        for r in augmented:
            w.writerow(r)
    print(f'Added {len(augmented)} augmented rows')
else:
    print('No augmentation needed')

with open(TRAIN_PATH, encoding='utf-8') as f:
    final = list(csv.DictReader(f))
from collections import Counter
cats = Counter(r['category'] for r in final)
print('Final distribution:')
for cat, count in cats.most_common():
    print(f'  {cat}: {count}')
print(f'Total: {len(final)}')
