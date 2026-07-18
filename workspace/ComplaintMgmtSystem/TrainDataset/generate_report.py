import csv, json, os
from collections import Counter

DATA = os.path.join(os.path.dirname(__file__), 'processed_dataset.csv')

with open(DATA, encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

n = len(rows)

cat_counter = Counter(r['category'] for r in rows)
pri_counter = Counter(r['priority'] for r in rows)
src_counter = Counter(r['source'] for r in rows)

cat_labels = json.dumps([c for c, _ in sorted(cat_counter.items(), key=lambda x: -x[1])])
cat_values = json.dumps([v for _, v in sorted(cat_counter.items(), key=lambda x: -x[1])])
cat_colors = json.dumps(['#022448', '#0058be', '#1a73e8', '#4a90d9', '#7ab3f0', '#a8d1f7', '#c4c6cf', '#e8eaf6', '#f8f9ff'])

pri_labels = json.dumps([p for p in ['High', 'Medium', 'Low']])
pri_values = json.dumps([pri_counter.get('High',0), pri_counter.get('Medium',0), pri_counter.get('Low',0)])

src_labels = json.dumps([s for s, _ in sorted(src_counter.items(), key=lambda x: -x[1])])
src_values = json.dumps([v for _, v in sorted(src_counter.items(), key=lambda x: -x[1])])

lengths = [len(r['text']) for r in rows]
texts = [r['text'] for r in rows]
unique = len(set(texts))
dupes = n - unique

# Bucket text lengths
buckets = {'0-50':0,'51-100':0,'101-150':0,'151-200':0,'201-300':0,'301-500':0,'500+':0}
for l in lengths:
    if l <= 50: buckets['0-50'] += 1
    elif l <= 100: buckets['51-100'] += 1
    elif l <= 150: buckets['101-150'] += 1
    elif l <= 200: buckets['151-200'] += 1
    elif l <= 300: buckets['201-300'] += 1
    elif l <= 500: buckets['301-500'] += 1
    else: buckets['500+'] += 1
len_labels = json.dumps(list(buckets.keys()))
len_values = json.dumps(list(buckets.values()))

cross = {}
for cat in sorted(cat_counter.keys()):
    cross[cat] = {
        'High': sum(1 for r in rows if r['category'] == cat and r['priority'] == 'High'),
        'Medium': sum(1 for r in rows if r['category'] == cat and r['priority'] == 'Medium'),
        'Low': sum(1 for r in rows if r['category'] == cat and r['priority'] == 'Low'),
    }
cross_json = json.dumps(cross)

html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dataset Analysis Report</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:'Inter',sans-serif; background:#f8f9ff; color:#022448; padding:40px; }}
.container {{ max-width:1200px; margin:0 auto; }}
h1 {{ font-size:28px; margin-bottom:30px; color:#022448; border-bottom:3px solid #0058be; padding-bottom:10px; }}
.stats {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:16px; margin-bottom:40px; }}
.stat-card {{ background:white; border-radius:12px; padding:20px; text-align:center; box-shadow:0 2px 8px rgba(0,0,0,0.08); }}
.stat-card .num {{ font-size:32px; font-weight:700; color:#0058be; }}
.stat-card .label {{ font-size:14px; color:#666; margin-top:4px; }}
.grid {{ display:grid; grid-template-columns:1fr 1fr; gap:24px; margin-bottom:40px; }}
.chart-card {{ background:white; border-radius:12px; padding:20px; box-shadow:0 2px 8px rgba(0,0,0,0.08); }}
.chart-card h3 {{ font-size:16px; margin-bottom:16px; color:#022448; }}
.full {{ grid-column:1/-1; }}
table {{ width:100%; border-collapse:collapse; font-size:14px; }}
th {{ background:#022448; color:white; padding:10px 12px; text-align:left; }}
td {{ padding:8px 12px; border-bottom:1px solid #e8eaf6; }}
tr:hover td {{ background:#f0f4ff; }}
.num-col {{ text-align:right; font-weight:600; }}
</style>
</head>
<body>
<div class="container">
<h1>Dataset Analysis Report</h1>

<div class="stats">
<div class="stat-card"><div class="num">{n}</div><div class="label">Total Samples</div></div>
<div class="stat-card"><div class="num">{len(cat_counter)}</div><div class="label">Categories</div></div>
<div class="stat-card"><div class="num">{len(pri_counter)}</div><div class="label">Priority Levels</div></div>
<div class="stat-card"><div class="num">{len(src_counter)}</div><div class="label">Sources</div></div>
<div class="stat-card"><div class="num">{unique}</div><div class="label">Unique Texts</div></div>
<div class="stat-card"><div class="num">{dupes}</div><div class="label">Duplicates</div></div>
</div>

<div class="grid">
<div class="chart-card">
<h3>Category Distribution</h3>
<canvas id="catChart" height="200"></canvas>
</div>
<div class="chart-card">
<h3>Priority Distribution</h3>
<canvas id="priChart" height="200"></canvas>
</div>
<div class="chart-card">
<h3>Source Distribution</h3>
<canvas id="srcChart" height="200"></canvas>
</div>
<div class="chart-card">
<h3>Text Length Distribution</h3>
<canvas id="lenChart" height="200"></canvas>
</div>
</div>

<div class="chart-card full">
<h3>Category x Priority Cross-tab</h3>
<div style="overflow-x:auto;">
<table>
<tr><th>Category</th><th>High</th><th>Medium</th><th>Low</th><th>Total</th></tr>
'''

for cat in sorted(cat_counter.keys()):
    c = cross[cat]
    total = c['High'] + c['Medium'] + c['Low']
    html += f'<tr><td>{cat}</td><td class="num-col">{c["High"]}</td><td class="num-col">{c["Medium"]}</td><td class="num-col">{c["Low"]}</td><td class="num-col">{total}</td></tr>\n'

html += f'''</table>
</div>
</div>
</div>

<script>
new Chart(document.getElementById('catChart'), {{
    type: 'bar',
    data: {{
        labels: {cat_labels},
        datasets: [{{ label:'Count', data:{cat_values}, backgroundColor:{cat_colors}, borderRadius:6 }}]
    }},
    options: {{ responsive:true, plugins:{{ legend:{{ display:false }} }} }}
}});
new Chart(document.getElementById('priChart'), {{
    type: 'doughnut',
    data: {{
        labels: {pri_labels},
        datasets: [{{ data:{pri_values}, backgroundColor:['#EF4444','#F59E0B','#10B981'] }}]
    }},
    options: {{ responsive:true }}
}});
new Chart(document.getElementById('srcChart'), {{
    type: 'pie',
    data: {{
        labels: {src_labels},
        datasets: [{{ data:{src_values}, backgroundColor:['#022448','#0058be','#4a90d9'] }}]
    }},
    options: {{ responsive:true }}
}});
new Chart(document.getElementById('lenChart'), {{
    type: 'bar',
    data: {{
        labels: {len_labels},
        datasets: [{{ label:'Count', data:{len_values}, backgroundColor:'#0058be', borderRadius:6 }}]
    }},
    options: {{ responsive:true, plugins:{{ legend:{{ display:false }} }} }}
}});
</script>
</body>
</html>'''

out = os.path.join(os.path.dirname(__file__), 'report.html')
with open(out, 'w', encoding='utf-8') as f:
    f.write(html)
print(f'Report saved: {out}')
