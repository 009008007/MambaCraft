"""Record downloads created outside MambaCraft's application-data directory."""
import hashlib
import json
import os
from pathlib import Path
import uuid

APP_ID = 'org.mambacraft.launcher'
MARKER = '.mambacraft-owned.json'

def load_json(path, default=None):
    try:
        if path.is_symlink() or path.stat().st_size > 8 * 1024**2: return default
        return json.loads(path.read_text())
    except (OSError, ValueError): return default

def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    try:
        with temp.open('x') as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.flush(); os.fsync(stream.fileno())
        os.chmod(temp, 0o600); os.replace(temp, path)
    finally: temp.unlink(missing_ok=True)

def remember(data, entry):
    path = Path(data) / 'owned-files.json'; value = load_json(path, {})
    entries = value.get('entries', []) if isinstance(value, dict) else []
    entries = [item for item in entries if isinstance(item, dict) and item.get('path') != entry['path']]
    entries.append(entry)
    save_json(path, {'application': APP_ID, 'entries': entries})

def claim_new_tree(data, directory, kind='java'):
    directory = Path(directory).absolute()
    if directory.is_relative_to(Path(data).resolve()): return
    marker = load_json(directory / MARKER, {})
    if directory.exists() and (not isinstance(marker, dict) or marker.get('application') != APP_ID): return
    directory.mkdir(parents=True, exist_ok=True)
    save_json(directory / MARKER, {'application': APP_ID, 'kind': kind})
    remember(data, {'path': str(directory), 'kind': kind, 'type': 'tree'})

def remember_download(data, path):
    path = Path(path).resolve(strict=True)
    if path.is_relative_to(Path(data).resolve()): return
    digest = hashlib.sha256()
    with path.open('rb') as source:
        while chunk := source.read(1024**2): digest.update(chunk)
    remember(data, {'path': str(path), 'kind': 'download', 'type': 'file', 'sha256': digest.hexdigest()})
