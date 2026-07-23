import sys, os, json, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'train'))
from classifier import categorize, predict_top3, detect_anomaly, clean_and_tokenize, stem, MultinomialNB

def test_stem():
    assert stem('running') == 'runn'
    assert stem('slowly') == 'slow'
    assert stem('happiness') == 'happi'
    assert len(stem('cat')) == 3

def test_clean_and_tokenize():
    tokens = clean_and_tokenize('The internet is very slow in the library!')
    assert 'internet' in tokens
    assert 'slow' in tokens
    assert 'library' in tokens
    assert 'the' not in tokens

def test_categorize_returns_dict():
    result = categorize('The WiFi in the library keeps disconnecting every 5 minutes')
    assert 'category' in result
    assert 'confidence' in result
    assert 'tier' in result
    assert 0 <= result['confidence'] <= 1

def test_categorize_it_support():
    result = categorize('The internet connection in the library is extremely slow and keeps dropping')
    assert result['category'] in ('IT Support',)

def test_categorize_hostels():
    result = categorize('The hostel room has no hot water and the bathroom is leaking')
    assert result['category'] in ('Hostels',)

def test_categorize_canteen():
    result = categorize('The food in the canteen is not hygienic and expensive')
    assert result['category'] in ('Canteen',)

def test_categorize_unknown():
    result = categorize('a b c d e f')
    assert result['category'] in ('Other', 'Administrative')

def test_predict_top3_returns_list():
    result = predict_top3('The WiFi is slow')
    assert len(result) <= 3
    assert len(result) >= 1
    for item in result:
        assert 'category' in item
        assert 'confidence' in item

def test_predict_top3_sorted():
    result = predict_top3('The WiFi in the library is very slow and keeps disconnecting')
    assert result[0]['confidence'] >= result[-1]['confidence']

def test_detect_anomaly_returns_dict():
    result = detect_anomaly('The internet is slow')
    assert 'is_anomaly' in result
    assert 'flags' in result
    assert 'known_token_ratio' in result

def test_detect_anomaly_short_text():
    result = detect_anomaly('bad')
    assert 'too_short' in result['flags']

def test_detect_anomaly_true():
    result = detect_anomaly('xyzzy qux flob grunt')
    assert result['is_anomaly'] == True

def test_model_save_load(tmp_path):
    model = MultinomialNB()
    model.fit(['this is a test document', 'another document here'], [0, 1])
    path = os.path.join(tmp_path, 'model.json')
    model.save(path)
    loaded = MultinomialNB.load(path)
    assert loaded._trained == True
    assert loaded.classes == [0, 1]
    assert loaded.vocab_size == model.vocab_size
