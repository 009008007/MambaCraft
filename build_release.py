"""Build and validate a MambaCraft release archive, including its manifest."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

root=Path(__file__).resolve().parent
if len(sys.argv)!=2:raise SystemExit('Usage: python3 build_release.py /absolute/path/to/release.zip')
out=Path(sys.argv[1]).expanduser().resolve()
if out.is_relative_to(root):raise SystemExit('Place the release archive outside the package directory.')

def metadata(p):
    return p.name=='.DS_Store' or (p.name.startswith('._') and len(p.name)>2 and (p.parent/p.name[2:]).exists())
files=[]
for p in root.rglob('*'):
    if p.is_symlink():raise SystemExit('Package contains a symbolic link: '+str(p))
    if not p.is_file() or p.name in ('SHA256SUMS.json','.gitignore') or '.git' in p.parts or '__pycache__' in p.parts or p.suffix=='.pyc' or metadata(p):continue
    files.append(p)
files.sort(key=lambda p:p.relative_to(root).as_posix())
manifest={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
(root/'SHA256SUMS.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
out.parent.mkdir(parents=True,exist_ok=True)
with tempfile.NamedTemporaryFile(prefix='.mambacraft-release-',suffix='.zip',dir=out.parent,delete=False) as tmp:
    temporary=Path(tmp.name)
try:
    with zipfile.ZipFile(temporary,'w',zipfile.ZIP_DEFLATED,compresslevel=8) as z:
        z.writestr('MambaCraft/','')
        for p in [*files,root/'SHA256SUMS.json']:
            z.write(p,'MambaCraft/'+p.relative_to(root).as_posix())
    with tempfile.TemporaryDirectory(prefix='mambacraft-archive-check-') as td:
        with zipfile.ZipFile(temporary) as z:
            if 'MambaCraft/SHA256SUMS.json' not in z.namelist():raise SystemExit('Archive is missing SHA256SUMS.json.')
            z.extractall(td)
        check=subprocess.run([sys.executable,str(Path(td)/'MambaCraft'/'verify_package.py')],capture_output=True,text=True)
        if check.returncode:raise SystemExit('Extracted archive failed integrity check: '+check.stdout+check.stderr)
    temporary.replace(out)
finally:temporary.unlink(missing_ok=True)
print('Release created and extracted contents verified:',out)
print('SHA-256:',hashlib.sha256(out.read_bytes()).hexdigest())
