import csv, re, json, os, math
from collections import Counter, defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE, 'TrainDataset', 'processed_dataset.csv')
ENC_PATH = os.path.join(BASE, 'TrainDataset', 'encoders', 'category_decoder.json')

with open(ENC_PATH) as f:
    CAT_DECODER = {int(k): v for k, v in json.load(f).items()}

STOPWORDS = set('a an the is are was were be been being have has had do does did will would shall should may might must can could of in on at by for with about against between into through during before after above below to from up down out off over under again further then once here there when where why how all each every both few more most other some such no nor not only own same so than too very just because as until while'.split())

def clean_and_tokenize(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    tokens = text.split()
    return [t for t in tokens if t not in STOPWORDS and len(t) > 2]

def load_data(path):
    with open(path, encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    texts = [r['text'] for r in rows]
    labels = [int(r['category_encoded']) for r in rows]
    return texts, labels

class MultinomialNB:
    def __init__(self, alpha=1.0, min_df=2):
        self.alpha = alpha
        self.min_df = min_df
        self.classes = None
        self.priors = {}
        self.word_counts = {}
        self.class_total_words = {}
        self.vocab = set()

    def fit(self, texts, labels):
        self.classes = sorted(set(labels))
        n = len(texts)
        class_docs = Counter(labels)
        self.priors = {c: math.log(class_docs[c] / n) for c in self.classes}

        # Count word frequencies across ALL documents first
        all_tokenized = [clean_and_tokenize(t) for t in texts]
        doc_freq = Counter()
        for tokens in all_tokenized:
            for token in set(tokens):
                doc_freq[token] += 1

        # Filter: keep words that appear in at least min_df documents
        self.vocab = {word for word, freq in doc_freq.items() if freq >= self.min_df}
        print(f'Total unique words: {len(doc_freq)}, kept (min_df={self.min_df}): {len(self.vocab)}')

        self.word_counts = {c: defaultdict(int) for c in self.classes}
        self.class_total_words = {c: 0 for c in self.classes}

        for tokens, label in zip(all_tokenized, labels):
            for token in set(tokens):
                if token in self.vocab:
                    self.word_counts[label][token] += 1
                    self.class_total_words[label] += 1

        self.vocab_size = len(self.vocab)
        for c in self.classes:
            print(f'  Class {c} ({CAT_DECODER[c]}): {class_docs[c]} docs, {self.class_total_words[c]} words')

    def predict_proba(self, text):
        tokens = clean_and_tokenize(text)
        scores = {}
        for c in self.classes:
            log_prob = self.priors[c]
            total_wc = self.class_total_words[c]
            for token in tokens:
                count = self.word_counts[c].get(token, 0)
                log_prob += math.log((count + self.alpha) / (total_wc + self.alpha * self.vocab_size))
            scores[c] = log_prob
        return scores

    def predict(self, text):
        scores = self.predict_proba(text)
        return max(scores, key=scores.get)

    def predict_with_proba(self, text):
        scores = self.predict_proba(text)
        best = max(scores, key=scores.get)
        # Convert log probs to normal probabilities for display
        log_vals = list(scores.values())
        max_log = max(log_vals)
        exp_vals = [math.exp(v - max_log) for v in log_vals]
        total = sum(exp_vals)
        probs = {c: exp_vals[i] / total for i, c in enumerate(scores.keys())}
        return best, probs

    def accuracy(self, texts, labels):
        correct = 0
        for text, label in zip(texts, labels):
            pred = self.predict(text)
            if pred == label:
                correct += 1
        return correct / len(texts)

if __name__ == '__main__':
    print('=' * 60)
    print('   MULTINOMIAL NAIVE BAYES CLASSIFIER')
    print('   Implemented from scratch')
    print('=' * 60)

    texts, labels = load_data(DATA_PATH)
    print(f'\nLoaded {len(texts)} training samples')

    # Shuffle then stratified split (80/20)
    import random
    combined = list(zip(texts, labels))
    random.shuffle(combined)
    texts, labels = zip(*combined) if combined else ([], [])
    texts, labels = list(texts), list(labels)

    # Stratified split: keep class proportions
    from collections import Counter
    label_indices = defaultdict(list)
    for i, lbl in enumerate(labels):
        label_indices[lbl].append(i)

    train_idx, test_idx = [], []
    for lbl, indices in label_indices.items():
        random.shuffle(indices)
        split = max(1, int(len(indices) * 0.8))
        train_idx.extend(indices[:split])
        test_idx.extend(indices[split:])

    train_texts = [texts[i] for i in train_idx]
    train_labels = [labels[i] for i in train_idx]
    test_texts = [texts[i] for i in test_idx]
    test_labels = [labels[i] for i in test_idx]
    print(f'Training: {len(train_texts)} samples')
    print(f'Testing:  {len(test_texts)} samples')

    # 5-fold cross-validation
    print('\n--- 5-Fold Cross-Validation ---')
    label_indices = defaultdict(list)
    for i, lbl in enumerate(labels):
        label_indices[lbl].append(i)

    k = 5
    fold_accs = []
    for fold in range(k):
        train_idx, test_idx = [], []
        for lbl, indices in label_indices.items():
            shuffled = indices[:]
            random.shuffle(shuffled)
            split = max(1, len(shuffled) // k)
            test_idx.extend(shuffled[fold * split:(fold + 1) * split])
            train_idx.extend(shuffled[:fold * split] + shuffled[(fold + 1) * split:])

        fold_train_t = [texts[i] for i in train_idx]
        fold_train_l = [labels[i] for i in train_idx]
        fold_test_t = [texts[i] for i in test_idx]
        fold_test_l = [labels[i] for i in test_idx]

        fold_nb = MultinomialNB(alpha=1.0, min_df=3)
        fold_nb.fit(fold_train_t, fold_train_l)
        acc = fold_nb.accuracy(fold_test_t, fold_test_l)
        fold_accs.append(acc)
        print(f'  Fold {fold+1}: {acc*100:.2f}%')

    cv_acc = sum(fold_accs) / len(fold_accs)
    print(f'  Average: {cv_acc*100:.2f}%')

    nb = MultinomialNB(alpha=1.0, min_df=3)
    print('\n--- Training (full 80% split) ---')
    nb.fit(train_texts, train_labels)

    print('\n--- Evaluation ---')
    train_acc = nb.accuracy(train_texts, train_labels)
    test_acc = nb.accuracy(test_texts, test_labels)
    print(f'Training accuracy:   {train_acc*100:.2f}%')
    print(f'Testing accuracy:    {test_acc*100:.2f}%')
    print(f'Cross-val accuracy:  {cv_acc*100:.2f}%')

    print('\n--- Sample Predictions ---')
    samples = [
        "The wifi in the library is not working since morning I cannot access online journals",
        "My hostel room has a broken fan and the water is leaking from the ceiling",
        "Exam results are delayed and I need my grade card for placement applications",
        "I have not received my scholarship amount for this semester",
        "The bus timing has changed and I missed my evening classes",
        "Someone has stolen my laptop from the library reading hall"
    ]
    for s in samples:
        pred, probs = nb.predict_with_proba(s)
        conf = probs[pred] * 100
        print(f'\n  Text: "{s[:60]}..."')
        print(f'  Predicted: {CAT_DECODER[pred]} (confidence: {conf:.1f}%)')
        top3 = sorted(probs.items(), key=lambda x: -x[1])[:3]
        for c, p in top3:
            print(f'    → {CAT_DECODER[c]}: {p*100:.1f}%')

    print('\n' + '=' * 60)
    print(f'   FINAL TEST ACCURACY: {test_acc*100:.2f}%')
    print(f'   CROSS-VAL ACCURACY:  {cv_acc*100:.2f}%')
    print('=' * 60)
