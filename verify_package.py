"""Check packaged file integrity against SHA256SUMS.json (not a publisher signature)."""
from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parent
manifest=json.loads((root/'SHA256SUMS.json').read_text())

def is_macos_metadata(path):
    # Finder writes .DS_Store after extraction; AppleDouble may accompany a
    # real file when copied between filesystems. Ignore only known sidecars.
    if path.name=='.DS_Store':return True
    return path.name.startswith('._') and len(path.name)>2 and (path.parent/path.name[2:]).exists()

expected={p.relative_to(root).as_posix() for p in root.rglob('*')
          if p.is_file() and p.name not in ('SHA256SUMS.json','.gitignore') and
          '.git' not in p.parts and '__pycache__' not in p.parts and p.suffix!='.pyc' and not is_macos_metadata(p)}
if set(manifest)!=expected:
    missing=sorted(expected-set(manifest));extra=sorted(set(manifest)-expected)
    raise SystemExit('套件檔案清單與 SHA256SUMS.json 不一致：缺少 '+repr(missing)+'；多餘 '+repr(extra))
for relative,digest in manifest.items():
    original=root/relative
    path=original.resolve()
    if original.is_symlink() or not path.is_relative_to(root) or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=digest:
        raise SystemExit('套件檔案缺失或已變更：'+relative+'。請重新解壓縮 ZIP。')
print('套件完整性檢查通過。')
