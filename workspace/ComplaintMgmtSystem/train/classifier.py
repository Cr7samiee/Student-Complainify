import csv, re, json, os, math
from collections import Counter, defaultdict

CONFIDENCE_THRESHOLD = 0.35
AUTO_THRESHOLD = 0.90
SUGGEST_THRESHOLD = 0.60
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE, 'TrainDataset', 'train_dataset.csv')
TEST_PATH = os.path.join(BASE, 'TrainDataset', 'test_dataset.csv')
ENC_PATH = os.path.join(BASE, 'TrainDataset', 'encoders', 'category_decoder.json')

with open(ENC_PATH) as f:
    CAT_DECODER = {int(k): v for k, v in json.load(f).items()}

STOPWORDS = set('a an the is are was were be been being have has had do does did will would shall should may might must can could of in on at by for with about against between into through during before after above below to from up down out off over under again further then once here there when where why how all each every both few more most other some such no nor not only own same so than too very just because as until while'.split())

def stem(w):
    if len(w) < 5: return w
    if w.endswith('ingly'): return w[:-5]
    if w.endswith('edly'): return w[:-4]
    if w.endswith('ying'): return w[:-4] + 'y'
    if w.endswith('ation'): return w[:-5]
    if w.endswith('ment'): return w[:-4]
    if w.endswith('able'): return w[:-4]
    if w.endswith('ible'): return w[:-4]
    if w.endswith('ness'): return w[:-4]
    if w.endswith('less'): return w[:-4]
    if w.endswith('ally'): return w[:-4]
    if w.endswith('sion'): return w[:-3] + 's'
    if w.endswith('tion'): return w[:-3] + 't'
    if w.endswith('ical'): return w[:-4]
    if w.endswith('ied'): return w[:-3] + 'y'
    if w.endswith('ies'): return w[:-3] + 'y'
    if w.endswith('ing'): return w[:-3]
    if w.endswith('ive'): return w[:-3]
    if w.endswith('ful'): return w[:-3]
    if w.endswith('ous'): return w[:-3]
    if w.endswith('ise'): return w[:-3]
    if w.endswith('ize'): return w[:-3]
    if w.endswith('ate'): return w[:-3]
    if w.endswith('ify'): return w[:-3]
    if w.endswith('ed'): return w[:-2]
    if w.endswith('er'): return w[:-2]
    if w.endswith('or'): return w[:-2]
    if w.endswith('ly'): return w[:-2]
    if w.endswith('al'): return w[:-2]
    if w.endswith('en'): return w[:-2]
    if w.endswith('s') and not w.endswith('ss'): return w[:-1]
    return w

def clean_and_tokenize(text, add_bigrams=True):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    tokens = [stem(t) for t in text.split() if t not in STOPWORDS and len(t) > 2]
    if add_bigrams and len(tokens) > 1:
        tokens += ['_'.join(tokens[i:i+2]) for i in range(len(tokens)-1)]
    return tokens

class MultinomialNB:
    def __init__(self, alpha=1.0, min_df=3):
        self.alpha = alpha; self.min_df = min_df
        self._trained = False

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
        self._trained = True

    def predict_with_proba(self, text):
        if not self._trained:
            raise RuntimeError("Model not trained")
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

_model = None

CATEGORY_NORMALIZE = {
    'Fees / Finance': 'Financial Services',
    'Security / Discipline': 'Security',
    'Administration': 'Administrative',
}

RULE_BASED_CATEGORIES = [
    {
        'category': 'Administrative',
        'confidence': 0.95,
        'topic_terms': {
            'hackathon', 'hackthon', 'hackaton', 'event', 'competition',
            'seminar', 'workshop', 'fest', 'festival', 'orientation',
            'program', 'ceremony', 'club', 'conference'
        },
        'issue_terms': {
            'manage', 'management', 'mismanag', 'organize', 'organization',
            'arrange', 'arrangement', 'coordination', 'coordinat', 'schedule',
            'registration', 'venue', 'bad', 'poor', 'worst'
        },
    },
]

def rule_based_categorize(text):
    tokens = set(clean_and_tokenize(text, add_bigrams=False))
    raw_words = set(re.findall(r'[a-z0-9]+', text.lower()))
    words = tokens | raw_words
    for rule in RULE_BASED_CATEGORIES:
        if words & rule['topic_terms'] and words & rule['issue_terms']:
            return rule['category'], rule['confidence']
    return None

def get_model():
    global _model
    if _model is None:
        with open(DATA_PATH, encoding='utf-8') as f:
            rows = list(csv.DictReader(f))
        texts = [r['text'] for r in rows]
        labels = [int(r['category_encoded']) for r in rows]
        _model = MultinomialNB()
        _model.fit(texts, labels)
    return _model

def categorize(text):
    rule_match = rule_based_categorize(text)
    if rule_match:
        cat, conf = rule_match
        return {
            'category': cat,
            'confidence': conf,
            'tier': 'auto' if conf >= AUTO_THRESHOLD else 'suggest'
        }

    model = get_model()
    pred, probs = model.predict_with_proba(text)
    conf = probs[pred]

    if conf < CONFIDENCE_THRESHOLD:
        return {'category': 'Other', 'confidence': conf, 'tier': 'unknown'}

    cat = CAT_DECODER[pred]
    cat = CATEGORY_NORMALIZE.get(cat, cat)

    if conf >= AUTO_THRESHOLD:
        tier = 'auto'
    elif conf >= SUGGEST_THRESHOLD:
        tier = 'suggest'
    else:
        tier = 'unknown'

    return {'category': cat, 'confidence': conf, 'tier': tier}

def auto_categorize(text):
    result = categorize(text)
    return result['category'], result['confidence']
