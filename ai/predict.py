import csv, re, json, os, math, sys
from collections import Counter, defaultdict

CONFIDENCE_THRESHOLD = 0.60

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE, 'TrainDataset', 'processed_dataset_815.csv')
ENC_PATH = os.path.join(BASE, 'TrainDataset', 'encoders', 'category_decoder.json')

with open(ENC_PATH) as f:
    CAT_DECODER = {int(k): v for k, v in json.load(f).items()}

STOPWORDS = set('a an the is are was were be been being have has had do does did will would shall should may might must can could of in on at by for with about against between into through during before after above below to from up down out off over under again further then once here there when where why how all each every both few more most other some such no nor not only own same so than too very just because as until while'.split())

def clean_and_tokenize(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    tokens = text.split()
    return [t for t in tokens if t not in STOPWORDS and len(t) > 2]

class MultinomialNB:
    def __init__(self, alpha=1.0, min_df=3):
        self.alpha = alpha
        self.min_df = min_df

    def fit(self, texts, labels):
        self.classes = sorted(set(labels))
        n = len(texts)
        class_docs = Counter(labels)
        self.priors = {c: math.log(class_docs[c] / n) for c in self.classes}

        all_tokenized = [clean_and_tokenize(t) for t in texts]
        doc_freq = Counter()
        for tokens in all_tokenized:
            for token in set(tokens):
                doc_freq[token] += 1

        self.vocab = {word for word, freq in doc_freq.items() if freq >= self.min_df}
        self.word_counts = {c: defaultdict(int) for c in self.classes}
        self.class_total_words = {c: 0 for c in self.classes}

        for tokens, label in zip(all_tokenized, labels):
            for token in set(tokens):
                if token in self.vocab:
                    self.word_counts[label][token] += 1
                    self.class_total_words[label] += 1

        self.vocab_size = len(self.vocab)

    def predict_with_proba(self, text):
        tokens = clean_and_tokenize(text)
        scores = {}
        for c in self.classes:
            log_prob = self.priors[c]
            total_wc = self.class_total_words[c]
            for token in tokens:
                count = self.word_counts[c].get(token, 0)
                log_prob += math.log((count + self.alpha) / (total_wc + self.alpha * self.vocab_size))
            scores[c] = log_prob

        best = max(scores, key=scores.get)
        log_vals = list(scores.values())
        max_log = max(log_vals)
        exp_vals = [math.exp(v - max_log) for v in log_vals]
        total = sum(exp_vals)
        probs = {c: exp_vals[i] / total for i, c in enumerate(scores.keys())}
        return best, probs

print('=' * 55)
print(f'  Complaint Category Predictor')
print(f'  (threshold: {CONFIDENCE_THRESHOLD*100:.0f}% → Other)')
print('=' * 55)

with open(DATA_PATH, encoding='utf-8') as f:
    rows = list(csv.DictReader(f))
texts = [r['text'] for r in rows]
labels = [int(r['category_encoded']) for r in rows]

print(f'Training on {len(texts)} samples...')
nb = MultinomialNB()
nb.fit(texts, labels)
print('Model ready!')

def predict_safe(inp, nb):
    pred, probs = nb.predict_with_proba(inp)
    conf = probs[pred]
    if conf < CONFIDENCE_THRESHOLD:
        return 'Other', conf, probs
    return CAT_DECODER[pred], conf, probs

if len(sys.argv) > 1:
    inp = ' '.join(sys.argv[1:])
    label, conf, probs = predict_safe(inp, nb)
    print(f'\nComplaint: {inp[:80]}...' if len(inp) > 80 else f'\nComplaint: {inp}')
    print(f'Predicted: {label} ({conf*100:.1f}% confidence)')
    if label != 'Other':
        print('Top-3:')
        for c, p in sorted(probs.items(), key=lambda x: -x[1])[:3]:
            print(f'  → {CAT_DECODER[c]}: {p*100:.1f}%')
else:
    while True:
        inp = input('\nEnter complaint (or "quit"): ').strip()
        if inp.lower() == 'quit':
            break
        if not inp:
            continue

        label, conf, probs = predict_safe(inp, nb)
        print(f'\n  Predicted: {label} ({conf*100:.1f}% confidence)')
        if label != 'Other':
            print('  Top-3:')
            for c, p in sorted(probs.items(), key=lambda x: -x[1])[:3]:
                print(f'    → {CAT_DECODER[c]}: {p*100:.1f}%')
