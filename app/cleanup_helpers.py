"""Remove only obsolete MambaCraft versioned Python environments after a successful upgrade."""
from pathlib import Path
import re
import shutil
import sys

ENV_RE=re.compile(r'python-\d+\.\d+\.\d+-rc\d+\Z')

def cleanup(data_dir,current_env):
    root=Path(data_dir).resolve(strict=True)
    current_input=Path(current_env)
    if current_input.is_symlink():raise ValueError('Current MambaCraft environment must not be a symbolic link.')
    current=current_input.resolve(strict=True)
    if current.parent!=root or not current.is_dir():
        raise ValueError('Current MambaCraft environment is not a direct, safe child of the data folder.')
    removed=[];preserved=[]
    for candidate in sorted(root.iterdir()):
        if candidate==current or not ENV_RE.fullmatch(candidate.name):continue
        if candidate.is_symlink() or not candidate.is_dir():
            preserved.append(candidate.name);continue
        resolved=candidate.resolve(strict=True)
        if resolved.parent!=root:
            preserved.append(candidate.name);continue
        try:
            shutil.rmtree(resolved);removed.append(candidate.name)
        except OSError:
            preserved.append(candidate.name)
    return removed,preserved

if __name__=='__main__':
    if len(sys.argv)!=3:raise SystemExit('usage: cleanup_helpers.py DATA_DIR CURRENT_ENV')
    removed,preserved=cleanup(sys.argv[1],sys.argv[2])
    if removed:print('已移除舊 Helper 環境：'+', '.join(removed))
    if preserved:print('部分舊 Helper 因正在使用或權限不足而保留：'+', '.join(preserved))
