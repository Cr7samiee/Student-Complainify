from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_analyzer = SentimentIntensityAnalyzer()


def analyze_sentiment(text):
    scores = _analyzer.polarity_scores(text)
    compound = scores['compound']

    if compound <= -0.5:
        label, sub_label = 'Negative', 'Angry / Frustrated'
    elif compound <= -0.05:
        label, sub_label = 'Negative', 'Dissatisfied'
    elif compound >= 0.5:
        label, sub_label = 'Positive', 'Appreciative'
    elif compound >= 0.05:
        label, sub_label = 'Positive', 'Satisfied'
    else:
        label, sub_label = 'Neutral', 'Informational'

    return {
        'label': label,
        'sub_label': sub_label,
        'score': round(compound, 3),
        'neg_words': 0,
        'pos_words': 0,
        'total_sentiment_words': 0,
        'negations': 0,
        'vader': scores,
    }


def sentiment_priority_boost(sentiment_label, current_priority):
    boosts = {
        'Negative': {'Low': 'Medium', 'Medium': 'High', 'High': 'High'},
        'Neutral': {'Low': 'Low', 'Medium': 'Medium', 'High': 'High'},
        'Positive': {'Low': 'Low', 'Medium': 'Medium', 'High': 'High'},
    }
    return boosts.get(sentiment_label, {}).get(current_priority, current_priority)
