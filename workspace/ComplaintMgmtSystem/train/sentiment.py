"""
Lexicon-based Sentiment Analyzer for Complaints
- No sklearn, no training data needed
- Uses word lists + negation handling + intensifier amplification
"""

import re, math

NEGATION_WORDS = {'not', 'no', 'never', 'neither', 'nor', 'none', 'nothing',
                  'nobody', 'nowhere', 'cannot', "can't", "don't", "won't",
                  "wouldn't", "shouldn't", "couldn't", "isn't", "aren't",
                  "wasn't", "weren't", "haven't", "hasn't", "hadn't", "didn't",
                  "doesn't", "donot", "dont"}

INTENSIFIERS = {'very': 1.5, 'extremely': 2.0, 'really': 1.5, 'absolutely': 2.0,
                'completely': 1.5, 'totally': 1.5, 'highly': 1.5, 'strongly': 1.5,
                'utterly': 2.0, 'terribly': 1.5, 'so': 1.3, 'too': 1.3,
                'incredibly': 2.0, 'particularly': 1.3, 'exceptionally': 2.0}

NEGATIVE_WORDS = {
    'angry': -2, 'furious': -3, 'frustrated': -2, 'frustrating': -2,
    'terrible': -3, 'horrible': -3, 'worst': -3, 'awful': -3,
    'useless': -3, 'pathetic': -3, 'ridiculous': -3, 'unacceptable': -3,
    'disgusting': -3, 'fedup': -2, 'fed_up': -2, 'sick_of': -2,
    'tired_of': -1, 'enough': -1, 'waste': -2, 'hate': -3, 'hated': -3,
    'stupid': -2, 'careless': -2, 'rude': -2, 'arrogant': -2,
    'irresponsible': -2, 'delay': -1, 'delayed': -1, 'late': -1,
    'ignored': -2, 'ignoring': -2, 'ignore': -2, 'helpless': -2,
    'disappointed': -2, 'disappointing': -2, 'disappoint': -2,
    'shame': -2, 'shameful': -2, 'inexcusable': -3, 'outrageous': -3,
    'nonsense': -2, 'annoyed': -2, 'annoying': -2, 'irritating': -2,
    'irritated': -2, 'hopeless': -3, 'tension': -2, 'stress': -2,
    'stressful': -2, 'stressed': -2, 'scared': -2, 'afraid': -2,
    'worried': -2, 'depressing': -2, 'depressed': -2, 'worst': -3,
    'broken': -2, 'damaged': -2, 'damage': -1, 'not_working': -2,
    'notworking': -2, 'failure': -2, 'fail': -1, 'failed': -2,
    'poor': -2, 'bad': -2, 'worse': -2, 'pain': -1, 'painful': -2,
    'suffer': -2, 'suffering': -2, 'complaint': -1, 'problem': -1,
    'issue': -1, 'trouble': -1, 'difficult': -1, 'hard': -1,
    'impossible': -2, 'unable': -2, 'cannot': -2, 'cant': -2,
    'stuck': -1, 'blocked': -1, 'missing': -1, 'lost': -1,
    'urgent': -1, 'emergency': -2, 'critical': -1, 'crisis': -2,
    'harassment': -3, 'harassing': -3, 'harass': -3, 'abuse': -3,
    'abused': -3, 'threat': -3, 'threatened': -3, 'steal': -2,
    'stolen': -3, 'stole': -2, 'theft': -3, 'robbery': -3, 'cheat': -2,
    'cheated': -3, 'scam': -3, 'fraud': -3, 'fake': -2,
    'dirty': -1, 'unhygienic': -2, 'dirty': -1, 'rotten': -2,
    'spoiled': -2, 'expired': -1, 'stale': -2, 'smelly': -2,
    'stink': -2, 'leakage': -1, 'leaking': -1, 'flood': -2,
    'overflow': -1, 'clogged': -1, 'cracked': -1, 'broken': -2,
    'malfunction': -2, 'malfunctioning': -2, 'slow': -1, 'slower': -1,
    'slowest': -2, 'worst': -3, 'pathetic': -3, 'dreadful': -3,
    'lousy': -2, 'mediocre': -1, 'unsatisfactory': -2, 'unsatisfied': -2,
    'frustrate': -2, 'aggravate': -2, 'aggravated': -2,
    'miserable': -3, 'unhappy': -2, 'unsafe': -2, 'dangerous': -2,
}

POSITIVE_WORDS = {
    'thank': 2, 'thanks': 2, 'thankful': 2, 'gratitude': 2,
    'appreciate': 2, 'appreciated': 2, 'appreciation': 2,
    'grateful': 2, 'kindly': 1, 'good': 1, 'great': 2,
    'excellent': 3, 'wonderful': 3, 'helpful': 2, 'helpfully': 1,
    'quick': 1, 'fast': 1, 'efficient': 2, 'efficiently': 2,
    'satisfied': 2, 'satisfying': 2, 'happy': 2, 'happier': 2,
    'pleased': 2, 'nice': 1, 'superb': 3, 'fantastic': 3,
    'amazing': 3, 'love': 2, 'best': 2, 'perfect': 3,
    'smooth': 1, 'easy': 1, 'easygoing': 1, 'cooperative': 2,
    'supportive': 2, 'support': 1, 'help': 1, 'assist': 1,
    'assistance': 1, 'resolved': 1, 'resolve': 1, 'solution': 1,
    'solved': 1, 'fixed': 1, 'improved': 1, 'improvement': 1,
    'clean': 1, 'well': 1, 'better': 1, 'friendly': 2,
    'polite': 2, 'courteous': 2, 'professional': 2, 'prompt': 2,
    'timely': 1, 'responsive': 2, 'understanding': 2, 'patient': 1,
    'welcoming': 2, 'comfortable': 1, 'convenient': 1,
}


def analyze_sentiment(text):
    text_lower = text.lower()
    tokens = re.findall(r"[a-z]+'?[a-z]*", text_lower)

    score = 0.0
    word_count = 0
    negate_next = False
    intensify_next = 1.0
    negations_used = 0
    pos_words_found = []
    neg_words_found = []

    for i, token in enumerate(tokens):
        multiplier = -1.0 if negate_next else 1.0
        multiplier *= intensify_next

        if token in NEGATION_WORDS:
            negate_next = True
            negations_used += 1
            intensify_next = 1.0
            continue

        if token in INTENSIFIERS:
            intensify_next = INTENSIFIERS[token]
            continue

        if token in POSITIVE_WORDS:
            word_score = POSITIVE_WORDS[token] * multiplier
            score += word_score
            word_count += 1
            pos_words_found.append((token, word_score))
            negate_next = False
            intensify_next = 1.0
        elif token in NEGATIVE_WORDS:
            word_score = NEGATIVE_WORDS[token] * multiplier
            score += word_score
            word_count += 1
            neg_words_found.append((token, word_score))
            negate_next = False
            intensify_next = 1.0
        else:
            negate_next = False
            intensify_next = 1.0

    if word_count == 0:
        return {'label': 'Neutral', 'sub_label': 'Informational', 'score': 0.0,
                'neg_words': 0, 'pos_words': 0, 'total_sentiment_words': 0,
                'details': 'no_sentiment_words'}

    avg_score = score / word_count

    if avg_score < -0.5:
        sub_label = 'Angry / Frustrated'
    elif avg_score < -0.1:
        sub_label = 'Dissatisfied'
    elif avg_score > 0.5:
        sub_label = 'Appreciative'
    elif avg_score > 0.1:
        sub_label = 'Satisfied'
    else:
        sub_label = 'Informational'

    if avg_score < -0.1:
        label = 'Negative'
    elif avg_score > 0.1:
        label = 'Positive'
    else:
        label = 'Neutral'

    return {
        'label': label,
        'sub_label': sub_label,
        'score': round(avg_score, 3),
        'neg_words': len(neg_words_found),
        'pos_words': len(pos_words_found),
        'total_sentiment_words': word_count,
        'negations': negations_used,
    }


def sentiment_priority_boost(sentiment_label, current_priority):
    boosts = {
        'Negative': {'Low': 'Medium', 'Medium': 'High', 'High': 'High'},
        'Neutral': {'Low': 'Low', 'Medium': 'Medium', 'High': 'High'},
        'Positive': {'Low': 'Low', 'Medium': 'Medium', 'High': 'High'},
    }
    return boosts.get(sentiment_label, {}).get(current_priority, current_priority)


if __name__ == '__main__':
    test_cases = [
        "Thank you for your help, really appreciate it",
        "The problem is still not fixed, very disappointed with the service",
        "WiFi is not working in the library",
        "This is absolutely ridiculous and unacceptable behavior from the staff. I am extremely frustrated and angry about how this was handled. Complete waste of time.",
        "Please look into the water leakage issue in my room when you get a chance",
        "I hate this college, worst experience ever, useless administration",
        "Great work by the maintenance team, very helpful and quick response",
        "exam schedule not released yet",
        "someone stole my laptop from library",
        "my ex is posting my public pics online revenge please take action",
    ]

    print(f"{'Text':<55s} {'Label':<12s} {'Score':>8s} {'Neg':>4s} {'Pos':>4s}")
    print('-' * 85)
    for t in test_cases:
        r = analyze_sentiment(t)
        sub = r['sub_label']
        print(f"{t[:52]:<55s} {sub:<12s} {r['score']:>7.2f}  {r['neg_words']:>3d}  {r['pos_words']:>3d}")
