import sys, os, json, pytest
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend'))
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    rv = client.get('/')
    assert rv.status_code == 200

def test_student_login_page(client):
    rv = client.get('/student/login')
    assert rv.status_code == 200

def test_admin_login_page(client):
    rv = client.get('/admin/login')
    assert rv.status_code == 200

def test_predict_api(client):
    rv = client.post('/api/predict', json={'text': 'The WiFi is slow'})
    assert rv.status_code == 200
    data = rv.get_json()
    assert 'category' in data
    assert 'confidence' in data

def test_predict_api_no_text(client):
    rv = client.post('/api/predict', json={})
    assert rv.status_code == 400

def test_predict_top3_api(client):
    rv = client.post('/api/predict-top3', json={'text': 'The WiFi in the library is slow'})
    assert rv.status_code == 200
    data = rv.get_json()
    assert 'predictions' in data
    assert len(data['predictions']) >= 1

def test_predict_resolution_api(client):
    rv = client.get('/api/predict-resolution?text=WiFi slow')
    assert rv.status_code == 200
    data = rv.get_json()
    assert 'hours' in data

def test_detect_anomaly_api(client):
    rv = client.post('/api/detect-anomaly', json={'text': 'bad'})
    assert rv.status_code == 200
    data = rv.get_json()
    assert 'is_anomaly' in data
    assert 'flags' in data

def test_similar_complaints_api(client):
    rv = client.post('/api/similar-complaints', json={'text': 'WiFi slow in library'})
    assert rv.status_code == 200
    data = rv.get_json()
    assert 'similar' in data

def test_track_page(client):
    rv = client.get('/track')
    assert rv.status_code == 200
