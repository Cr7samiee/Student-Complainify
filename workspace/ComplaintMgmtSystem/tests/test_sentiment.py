import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'train'))
from sentiment import analyze_sentiment, sentiment_priority_boost

def test_analyze_sentiment_returns_dict():
    result = analyze_sentiment('This is good')
    assert 'label' in result
    assert 'score' in result
    assert 'sub_label' in result

def test_sentiment_positive():
    result = analyze_sentiment('The service was excellent and very helpful')
    assert result['label'] == 'Positive'

def test_sentiment_negative():
    result = analyze_sentiment('This is terrible and extremely frustrating')
    assert result['label'] == 'Negative'

def test_sentiment_boost_negative_high():
    result = sentiment_priority_boost('Negative', 'Medium')
    assert result == 'High'

def test_sentiment_boost_negative_low():
    result = sentiment_priority_boost('Negative', 'Low')
    assert result == 'Medium'

def test_sentiment_boost_positive():
    result = sentiment_priority_boost('Positive', 'High')
    assert result == 'High'

def test_sentiment_boost_neutral():
    result = sentiment_priority_boost('Neutral', 'Medium')
    assert result == 'Medium'
