import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from classifier import categorize, get_model, CAT_DECODER, AUTO_THRESHOLD, SUGGEST_THRESHOLD
from sentiment import analyze_sentiment
from priority import compute_priority

print('=' * 55)
print(f'  Complaint Category Predictor')
print(f'  auto={AUTO_THRESHOLD*100:.0f}%+  suggest=60-89%  unknown<{SUGGEST_THRESHOLD*100:.0f}%')
print('=' * 55)

model = get_model()
print(f'Model ready!')

def top_n(nb, text, n=3):
    _, probs = nb.predict_with_proba(text)
    return sorted(probs.items(), key=lambda x: -x[1])[:n]

def run(inp):
    r = categorize(inp)
    print(f'\nComplaint: {inp[:80]}...' if len(inp) > 80 else f'\nComplaint: {inp}')
    print(f'Category : {r["category"]} ({r["confidence"]*100:.1f}%) [{r["tier"]}]')
    if r['tier'] != 'unknown':
        print('  Top-3:')
        for c, p in top_n(model, inp):
            print(f'    -> {CAT_DECODER[c]}: {p*100:.1f}%')
    s = analyze_sentiment(inp)
    priority, score, reason = compute_priority(inp, s['label'], s['score'])
    print(f'  Sentiment: {s["label"]} (score {s["score"]}) '
          f'[model={s.get("model", "rule_based")}]')
    if s.get('ml_confidence') is not None:
        print(f'  ML confidence: {s["ml_confidence"]*100:.1f}%')
    print(f'  Priority : {priority} (weighted score {score} — {reason})')

if len(sys.argv) > 1:
    run(' '.join(sys.argv[1:]))
else:
    while True:
        inp = input('\nEnter complaint (or "quit"): ').strip()
        if inp.lower() == 'quit':
            break
        if not inp:
            continue
        run(inp)
