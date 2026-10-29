"""Previewable permanent removal of MambaCraft-owned files. Stdlib only."""
import argparse
import fcntl
import hashlib
import os
from pathlib import Path, PurePosixPath
import platform
import plistlib
import re
import shutil
import subprocess
import sys
import zipfile
from ownership import APP_ID, MARKER, load_json

CONFIRM = 'DELETE ALL MAMBACRAFT'
DATA_NAME = re.compile(r'MambaCraft[0-9]*\Z')
PACKAGE_NAME = re.compile(r'MambaCraft_macOS_[A-Za-z0-9_. -]+(?: \([0-9]+\))?\Z')

def present(path): return path.exists() or path.is_symlink()

def bundle_is_ours(path):
    try:
        with (path/'Contents/Info.plist').open('rb') as stream:
            return plistlib.load(stream).get('CFBundleIdentifier') == APP_ID
    except (OSError, ValueError, plistlib.InvalidFileException): return False

def protected(path, home):
    path = Path(os.path.abspath(path))
    exact = {home, *home.parents, home/'Library', home/'Library/Application Support',
             home/'Downloads', home/'Desktop', home/'Documents', home/'Applications',
             Path('/Applications'), Path('/Volumes'), Path('/Library')}
    return path in exact or any(path==p or p in path.parents for p in
        map(Path, ('/System', '/usr', '/bin', '/sbin', '/etc', '/private', '/dev', '/proc', '/opt')))

def safe_parent(path):
    # A final symlink is only unlinked. Never follow an ancestor alias.
    return not any(parent.is_symlink() for parent in path.parents)

def checksum(path, algorithm):
    digest = hashlib.new(algorithm)
    with path.open('rb') as stream:
        while chunk := stream.read(1024**2): digest.update(chunk)
    return digest.hexdigest()

def legacy_java(root, add, notes):
    config = load_json(root/'settings.json', {})
    value = config.get('java_root') if isinstance(config, dict) else None
    roots = {Path(value).expanduser()} if isinstance(value, str) and Path(value).expanduser().is_absolute() else set()
    for record in (root/'instances').glob('*/instance.json'):
        data = load_json(record, {}); java = data.get('java') if isinstance(data, dict) else None
        if isinstance(java, str) and Path(java).is_absolute():
            for parent in Path(java).parents:
                if parent.name in ('mac-os', 'mac-os-arm64', 'linux'): roots.add(parent.parent); break
    for base in roots:
        if not safe_parent(base): notes.append('外部 Java 位置含符號連結：'+str(base)); continue
        for manifest in (root/'runtime-manifests').glob('*.json'):
            spec = load_json(manifest, {})
            if not isinstance(spec, dict) or not isinstance(spec.get('files'), dict): continue
            match = re.fullmatch(r'(mac-os-arm64|mac-os|linux)-([A-Za-z0-9._-]+)', manifest.stem)
            if not match: continue
            component = base/match[1]/match[2]
            for relative, item in spec['files'].items():
                if not isinstance(relative, str) or not isinstance(item, dict): continue
                name = PurePosixPath(relative)
                if name.is_absolute() or '..' in name.parts or '\\' in relative: continue
                path = component.joinpath(*name.parts)
                if not safe_parent(path): continue
                if item.get('type')=='file' and path.is_file() and not path.is_symlink():
                    raw = item.get('downloads', {}).get('raw', {}); expected = raw.get('sha1')
                    if isinstance(expected, str) and re.fullmatch('[0-9a-fA-F]{40}', expected):
                        if checksum(path, 'sha1')==expected.lower(): add(path, 'file', '舊版下載的 Java', component)
                        else: notes.append('Java 檔案與下載紀錄不同：'+str(path))
                elif item.get('type')=='link' and path.is_symlink() and os.readlink(path)==item.get('target'):
                    add(path, 'file', 'Java 連結', component)
        java8 = base/'mac-os-arm64/java8-arm64'
        if java8.is_dir() and not java8.is_symlink():
            # This component directory name was created by MambaCraft.
            candidates = list(java8.glob('*/Contents/Home/bin/java'))+list(java8.glob('bin/java'))+list(java8.glob('Contents/Home/bin/java'))
            if candidates: add(java8, 'tree', 'MambaCraft Apple Silicon Java 8')
        archive = base/'.downloads/apple-silicon-java8.archive'
        if present(archive): add(archive, 'file', 'Java 8 下載暫存')

def package_owned(path):
    if not path.is_dir() or path.is_symlink(): return False
    manifest = load_json(path/'SHA256SUMS.json', {})
    if not isinstance(manifest, dict) or not {'app/core.py', 'Start.command', 'Install.command'} <= set(manifest): return False
    try: return 'MambaCraft' in (path/'app/core.py').read_text()[:300]
    except OSError: return False

def plan_removal(home, package):
    home=Path(home).resolve(); package=Path(package).absolute()
    entries={}; notes=[]; data_roots=[]
    def add(path, kind, reason, prune=None):
        path=Path(os.path.abspath(path))
        if not present(path): return
        if protected(path, home) or not safe_parent(path):
            notes.append('拒絕不安全或過於廣泛的路徑：'+str(path)); return
        if path.is_symlink(): kind='file'
        identity=path.lstat()
        entries[str(path)]={'path':str(path), 'type':kind, 'reason':reason, 'prune':str(prune) if prune else None,
                            'identity':[identity.st_dev,identity.st_ino]}
    support=home/'Library/Application Support'
    for root in sorted(support.glob('MambaCraft*')):
        if not DATA_NAME.fullmatch(root.name): continue
        if root.is_symlink(): notes.append('資料目錄是連結，只會移除連結；請另外確認其實際位置：'+str(root.resolve()))
        if not root.is_symlink() and root.is_dir():
            data_roots.append(root)
            ledger=load_json(root/'owned-files.json', {})
            if isinstance(ledger, dict) and ledger.get('application')==APP_ID:
                for item in ledger.get('entries', []):
                    if not isinstance(item, dict) or not isinstance(item.get('path'), str): continue
                    target=Path(item['path'])
                    if not target.is_absolute() or not safe_parent(target): continue
                    if item.get('type')=='tree' and item.get('kind')=='java':
                        marker=load_json(target/MARKER, {})
                        if isinstance(marker, dict) and marker.get('application')==APP_ID: add(target, 'tree', 'MambaCraft 自訂位置 Java')
                        elif present(target): notes.append('Java 所有權標記缺失：'+str(target))
                    elif item.get('type')=='file' and item.get('kind')=='download' and target.is_file() and not target.is_symlink():
                        if checksum(target, 'sha256')==item.get('sha256'): add(target, 'file', 'MambaCraft 下載的檔案')
                        else: notes.append('下載檔案已被替換或修改：'+str(target))
            legacy_java(root, add, notes)
        add(root, 'tree', '全部遊戲、存檔、設定、Java、核心、備份與 Helper')
    for apps in (home/'Applications', Path('/Applications')):
        for app in apps.glob('MambaCraft*.app'):
            if bundle_is_ours(app): add(app, 'app', 'MambaCraft 應用程式')
    for folder in ('Caches','Logs','HTTPStorages','WebKit','Application Scripts','Containers'):
        for name in (APP_ID,'MambaCraft','MambaCraft1'): add(home/'Library'/folder/name, 'tree', 'MambaCraft macOS 資料')
    for name in (APP_ID+'.plist',APP_ID+'.plist.lockfile'):
        add(home/'Library/Preferences'/name, 'file', '偏好設定')
    add(home/'Library/Saved Application State'/(APP_ID+'.savedState'), 'tree', '視窗狀態')
    for file in (home/'Library/Preferences/ByHost').glob(APP_ID+'.*.plist'): add(file, 'file', 'Mac 專屬偏好設定')
    for app in (home/'.Trash').glob('MambaCraft*.app'):
        if bundle_is_ours(app): add(app, 'app', '舊版留在垃圾桶的 App')
    for log in (home/'Downloads').glob('MambaCraft-Bedrock*.txt'):
        if log.is_symlink() or not log.is_file(): continue
        with log.open('rb') as stream: header=stream.read(512)
        if header.startswith(b'MambaCraft Bedrock launch'): add(log,'file','匯出的基岩版日誌')
    for report in (home/'Library/Logs/DiagnosticReports').glob('*'):
        if report.suffix not in ('.ips','.crash','.hang') or not report.is_file() or report.is_symlink(): continue
        with report.open('rb') as stream: header=stream.read(65536)
        if APP_ID.encode() in header or any(str(root).encode() in header for root in data_roots):
            add(report,'file','MambaCraft macOS 崩潰報告')
    # Known package names in Downloads/Desktop and next to the current package.
    for parent in {home/'Downloads',home/'Desktop',package.parent}:
        if parent==home or not parent.is_dir() or not safe_parent(parent): continue
        for candidate in parent.iterdir():
            stem=candidate.stem if candidate.suffix.lower()=='.zip' else candidate.name
            if not PACKAGE_NAME.fullmatch(stem): continue
            if candidate.is_dir() and package_owned(candidate): add(candidate,'package','MambaCraft 解壓縮套件')
            elif candidate.suffix.lower()=='.zip' and not candidate.is_symlink():
                try:
                    with zipfile.ZipFile(candidate) as archive:
                        cores=[n for n in archive.namelist() if n.endswith('/app/core.py') or n=='app/core.py']
                        if cores and archive.getinfo(cores[0]).file_size<1024**2 and b'MambaCraft' in archive.read(cores[0])[:300]:
                            add(candidate,'file','MambaCraft 安裝壓縮檔')
                except (OSError,ValueError,zipfile.BadZipFile): pass
    if package_owned(package) and str(package) not in entries:
        manifest=load_json(package/'SHA256SUMS.json', {})
        for relative in (*manifest,'SHA256SUMS.json'):
            name=PurePosixPath(relative)
            if not name.is_absolute() and '..' not in name.parts: add(package.joinpath(*name.parts),'file','目前卸載套件',package)
        for cache in package.glob('app/**/__pycache__/*.pyc'): add(cache,'file','Python 快取',package)
    result=[]
    for entry in sorted(entries.values(),key=lambda e:len(Path(e['path']).parts)):
        if not any(other['type']!='file' and Path(entry['path']).is_relative_to(other['path']) for other in result): result.append(entry)
    return result,notes,data_roots

def execute_plan(entries, home):
    failures=[]
    for entry in sorted(entries,key=lambda e:{'app':0,'tree':1,'file':2,'package':3}.get(e['type'],2)):
        path=Path(entry['path'])
        try:
            if protected(path,home) or not safe_parent(path): raise OSError('路徑已變更或不安全。')
            if not present(path): continue
            identity=path.lstat()
            if entry.get('identity') and entry['identity'] != [identity.st_dev,identity.st_ino]:
                raise OSError('預覽後檔案身份已變更，未刪除。')
            if path.is_symlink() or path.is_file(): path.unlink()
            elif entry['type']=='file': raise OSError('原檔案已變成資料夾，未刪除。')
            else:
                if entry['type']=='app' and not bundle_is_ours(path): raise OSError('App 身份已變更。')
                shutil.rmtree(path)
            print('已永久刪除：'+str(path))
            boundary=Path(entry['prune']) if entry.get('prune') else None
            parent=path.parent
            while boundary and parent.is_relative_to(boundary) and not protected(parent,home):
                try: parent.rmdir()
                except OSError: break
                parent=parent.parent
        except OSError as exc: failures.append(str(path)+'：'+str(exc))
    return failures

def main():
    parser=argparse.ArgumentParser(description='完整永久移除 MambaCraft 與管理的所有遊戲資料。')
    parser.add_argument('--preview',action='store_true',help='只列出路徑，不停止程序或刪除檔案。')
    args=parser.parse_args()
    if platform.system()!='Darwin': raise SystemExit('此卸載程式只適用於 macOS。')
    home=Path.home().resolve(); package=Path(__file__).resolve().parents[1]
    entries,notes,roots=plan_removal(home,package)
    print('完整移除 MambaCraft：以下檔案會永久刪除，不會移到垃圾桶。')
    print('包含 Java／基岩版遊戲、世界存檔、設定、Mods、資源、備份及 Python Helper。')
    for entry in entries: print('  '+entry['path']+'  ['+entry['reason']+']')
    for note in notes: print('需手動確認：'+note)
    if args.preview or not entries: return 0
    print('\n請先備份你要保留的世界，並正常儲存、退出遊戲。')
    try: answer=input('輸入 '+CONFIRM+' 確認永久刪除：')
    except EOFError: return 0
    if answer!=CONFIRM: print('已取消，沒有刪除任何檔案。'); return 0
    from desktop import read_session,stop_helper
    locks=[]
    try:
        for root in roots:
            session=read_session(root)
            if session: stop_helper(root,session)
            for name in ('install.lock','server.lock'):
                lock=(root/name).open('a'); locks.append(lock); fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        result=subprocess.run(['/bin/ps','-axo','uid=,pid=,command='],capture_output=True,text=True,check=True)
        for line in result.stdout.splitlines():
            fields=line.strip().split(None,2)
            if len(fields)!=3 or fields[0]!=str(os.getuid()) or fields[1]==str(os.getpid()): continue
            if any(str(root) in fields[2] for root in roots) and re.search(r'(?:^|[/\s])(?:java|mcpelauncher-client[^\s]*|server\.py)(?:\s|$)',fields[2]):
                raise RuntimeError('仍有 MambaCraft 遊戲或 Helper 在執行，請先正常退出：PID '+fields[1])
        lsregister='/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister'
        if Path(lsregister).is_file():
            for entry in entries:
                if entry['type']=='app': subprocess.run([lsregister,'-u',entry['path']],capture_output=True)
        failures=execute_plan(entries,home)
    except (OSError,RuntimeError) as exc:
        print('卸載停止：'+str(exc),file=sys.stderr); return 1
    finally:
        for lock in locks: lock.close()
    leftovers=[entry['path'] for entry in entries if present(Path(entry['path']))]
    if failures or leftovers or notes:
        print('\n尚有項目需要處理：')
        for item in (*failures,*leftovers,*notes): print('  '+item)
        return 1
    print('\n已完整移除所列 MambaCraft 檔案與全部管理資料。'); return 0

if __name__=='__main__': raise SystemExit(main())
