import csv, json, os, math
from collections import Counter, defaultdict

DATA = os.path.join(os.path.dirname(__file__), 'processed_dataset.csv')

with open(DATA, encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

n = len(rows)
print('=' * 60)
print('   DATASET ANALYSIS REPORT')
print('=' * 60)
print(f'Total samples: {n}')
print()

# Category distribution
cat_counter = Counter(r['category'] for r in rows)
print(f'--- Category Distribution ---')
for cat, count in sorted(cat_counter.items(), key=lambda x: -x[1]):
    pct = (count / n) * 100
    bar = '#' * round(pct / 2)
    print(f'  {cat:25s} {count:4d} ({pct:5.1f}%) {bar}')

print()

# Priority distribution
pri_counter = Counter(r['priority'] for r in rows)
print(f'--- Priority Distribution ---')
for pri, count in sorted(pri_counter.items(), key=lambda x: -x[1]):
    pct = (count / n) * 100
    bar = '#' * round(pct / 2)
    print(f'  {pri:10s} {count:4d} ({pct:5.1f}%) {bar}')

print()

# Source distribution
src_counter = Counter(r['source'] for r in rows)
print(f'--- Source Distribution ---')
for src, count in sorted(src_counter.items(), key=lambda x: -x[1]):
    pct = (count / n) * 100
    print(f'  {src:15s} {count:4d} ({pct:5.1f}%)')

print()

# Category vs Priority cross-tab
print(f'--- Category x Priority Cross-tab ---')
header = f'{"Category":25s} {"High":>6s} {"Medium":>8s} {"Low":>6s} {"Total":>6s}'
print(header)
print('-' * len(header))
for cat in sorted(cat_counter.keys()):
    high = sum(1 for r in rows if r['category'] == cat and r['priority'] == 'High')
    med = sum(1 for r in rows if r['category'] == cat and r['priority'] == 'Medium')
    low = sum(1 for r in rows if r['category'] == cat and r['priority'] == 'Low')
    total = high + med + low
    print(f'  {cat:23s} {high:6d} {med:8d} {low:6d} {total:6d}')

print()

# Text length analysis
lengths = [len(r['text']) for r in rows]
lengths.sort()
avg_len = sum(lengths) / n
print(f'--- Text Length Stats (characters) ---')
print(f'  Average:   {avg_len:.1f}')
print(f'  Min:       {min(lengths)}')
print(f'  Max:       {max(lengths)}')
print(f'  Median:    {lengths[n // 2]}')
print(f'  P25:       {lengths[n // 4]}')
print(f'  P75:       {lengths[3 * n // 4]}')

print()

# Check for duplicates
texts = [r['text'] for r in rows]
unique = len(set(texts))
dup_count = n - unique
print(f'--- Data Quality ---')
print(f'  Unique texts:  {unique}')
print(f'  Duplicates:    {dup_count}')

# Check for very short texts
short = sum(1 for t in texts if len(t) < 20)
print(f'  Very short (<20 chars): {short}')

print()
print('=' * 60)
print('   ANALYSIS COMPLETE')
print('=' * 60)
