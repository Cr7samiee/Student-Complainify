import os, json, time

BASE = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE, 'models')
MANIFEST_PATH = os.path.join(MODELS_DIR, 'manifest.json')
REPORTS_DIR = os.path.join(BASE, 'reports')
ACTIVE_COPY_PATH = os.path.normpath(os.path.join(BASE, '..', 'data', 'model_params.json'))
MAX_KEEP = 10

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)


def _load_manifest():
    if os.path.isfile(MANIFEST_PATH):
        try:
            with open(MANIFEST_PATH) as f:
                return json.load(f)
        except Exception:
            pass
    return {'versions': [], 'active': None}


def _save_manifest(manifest):
    with open(MANIFEST_PATH, 'w') as f:
        json.dump(manifest, f, indent=2)


def latest_version_id():
    manifest = _load_manifest()
    return manifest.get('active')


def list_versions():
    manifest = _load_manifest()
    return sorted(manifest.get('versions', []), key=lambda v: v.get('id', ''), reverse=True)


def get_version_info(version_id):
    for v in list_versions():
        if v['id'] == version_id:
            return v
    return None


def _version_path(version_id):
    return os.path.join(MODELS_DIR, f'model_{version_id}.json')


def save_version(model, metrics=None, keep=MAX_KEEP):
    """Persist a trained model under a new version id and register it."""
    version_id = time.strftime('v%Y%m%d_%H%M%S')
    path = _version_path(version_id)
    model.save(path)

    import classifier
    record = {
        'id': version_id,
        'saved_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'path': path.replace('\\', '/'),
        'metrics': metrics or {},
    }
    manifest = _load_manifest()
    manifest['versions'] = [v for v in manifest.get('versions', []) if v['id'] != version_id]
    manifest['versions'].append(record)
    manifest['active'] = version_id
    versions = sorted(manifest['versions'], key=lambda v: v.get('id', ''), reverse=True)
    for stale in versions[keep:]:
        try:
            os.remove(_version_path(stale['id']))
        except OSError:
            pass
    manifest['versions'] = versions[:keep]
    _save_manifest(manifest)

    # keep legacy active copy so classifier.get_model() (existing app code) keeps working
    try:
        import shutil
        shutil.copyfile(path, ACTIVE_COPY_PATH)
    except OSError:
        pass
    return record


def load_version(version_id):
    path = _version_path(version_id)
    if not os.path.isfile(path):
        raise FileNotFoundError(f'Model version {version_id} not found at {path}')
    from classifier import MultinomialNB
    return MultinomialNB.load(path)


def load_latest():
    """Load the most recent registered model; falls back to the active copy."""
    manifest = _load_manifest()
    active = manifest.get('active')
    if active and os.path.isfile(_version_path(active)):
        return load_version(active)
    if os.path.isfile(ACTIVE_COPY_PATH):
        from classifier import MultinomialNB
        return MultinomialNB.load(ACTIVE_COPY_PATH)
    raise FileNotFoundError('No model registered yet. Run retrain.py first.')


def active_metrics():
    manifest = _load_manifest()
    active = manifest.get('active')
    for v in manifest.get('versions', []):
        if v['id'] == active:
            return v['metrics']
    return {}