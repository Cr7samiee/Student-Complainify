import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from classifier import categorize, get_model, CAT_DECODER, AUTO_THRESHOLD, SUGGEST_THRESHOLD

print('=' * 55)
print(f'  Complaint Category Predictor')
print(f'  auto={AUTO_THRESHOLD*100:.0f}%+  suggest=60-89%  unknown<{SUGGEST_THRESHOLD*100:.0f}%')
print('=' * 55)

model = get_model()
print(f'Model ready!')

def top_n(nb, text, n=3):
    _, probs = nb.predict_with_proba(text)
    return sorted(probs.items(), key=lambda x: -x[1])[:n]

if len(sys.argv) > 1:
    inp = ' '.join(sys.argv[1:])
    r = categorize(inp)
    print(f'\nComplaint: {inp[:80]}...' if len(inp) > 80 else f'\nComplaint: {inp}')
    print(f'Predicted: {r["category"]} ({r["confidence"]*100:.1f}%) [{r["tier"]}]')
    if r['tier'] != 'unknown':
        print('Top-3:')
        for c, p in top_n(model, inp):
            print(f'  -> {CAT_DECODER[c]}: {p*100:.1f}%')
else:
    while True:
        inp = input('\nEnter complaint (or "quit"): ').strip()
        if inp.lower() == 'quit':
            break
        if not inp:
            continue
        r = categorize(inp)
        print(f'\n  Predicted: {r["category"]} ({r["confidence"]*100:.1f}%) [{r["tier"]}]')
        if r['tier'] != 'unknown':
            print('  Top-3:')
            for c, p in top_n(model, inp):
                print(f'    -> {CAT_DECODER[c]}: {p*100:.1f}%')
