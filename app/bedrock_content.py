"""Version-scoped Bedrock content and resource installation."""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import tempfile
import threading
import time
import uuid
import zipfile
import re
from bedrock import BedrockManager, WORLD_ROOT, PACK_ROOTS, _safe_under
from bedrock_packages import download_package
from core import UserError, Cancelled, atomic_json, read_json

AUTO_IMPORT_SUFFIXES = {'.mcpack', '.mcaddon'}
AUTO_IMPORT_MAX_FILE = 512 * 1024**2


def safe_mkdir(root, target):
    root = Path(root).resolve(strict=True)
    target = Path(target)
    try: parts = target.relative_to(root).parts
    except ValueError: raise UserError('資料路徑超出管理範圍。')
    current = root
    for part in parts:
        current = current / part
        if current.is_symlink(): raise UserError('資料路徑含符號連結，請選擇實際資料夾。')
        current.mkdir(exist_ok=True)
    return target


class ContentMixin:
    def init_resource_watch(self):
        self._resource_watch_lock = threading.RLock()
        self._resource_watch_thread = threading.Thread(target=self._resource_watch_loop,
                                                       name='MambaCraftBedrockDownloads', daemon=True)
        self._resource_watch_thread.start()

    def _resource_watch_file(self):
        return self.launcher_data_root / 'bedrock-resource-watch.json'

    def _read_resource_watch(self):
        try:
            value = read_json(self._resource_watch_file())
            if not isinstance(value, dict): raise ValueError()
        except (OSError, ValueError, TypeError):
            value = {}
        seen = value.get('seen')
        pending = value.get('pending')
        return {
            'enabled': value.get('enabled') is True,
            'version': value.get('version') if isinstance(value.get('version'), str) else '',
            'seen': seen if isinstance(seen, dict) else {},
            'pending': pending if isinstance(pending, dict) else {},
            'lastFile': value.get('lastFile') if isinstance(value.get('lastFile'), str) else '',
            'lastMessage': value.get('lastMessage') if isinstance(value.get('lastMessage'), str) else '',
            'status': value.get('status') if isinstance(value.get('status'), str) else '',
        }

    def _write_resource_watch(self, value):
        atomic_json(self._resource_watch_file(), value)

    def _downloads_root(self):
        path = Path.home() / 'Downloads'
        try:
            root = path.resolve(strict=True)
            return root if root.is_dir() else None
        except (OSError, RuntimeError):
            return None

    def _download_candidates(self):
        root = self._downloads_root()
        if root is None: return {}
        result = {}
        try: paths = list(root.iterdir())[:5000]
        except OSError: return result
        for path in paths:
            if path.suffix.lower() not in AUTO_IMPORT_SUFFIXES or path.is_symlink(): continue
            try:
                info = path.stat(follow_symlinks=False)
                if not path.is_file() or not 0 < info.st_size <= AUTO_IMPORT_MAX_FILE: continue
                if path.resolve(strict=True).parent != root: continue
            except (OSError, RuntimeError):
                continue
            signature = hashlib.sha256((path.name + '\0' + str(info.st_size) + '\0' + str(info.st_mtime_ns)).encode()).hexdigest()
            result[signature] = {'name': path.name, 'size': info.st_size, 'mtime_ns': info.st_mtime_ns}
        return result

    def resource_auto_import_state(self):
        with self._resource_watch_lock:
            state = self._read_resource_watch()
        enabled = state['enabled']
        pending = [item for item in state['pending'].values() if isinstance(item, dict)
                   and item.get('status') in ('waiting', 'installing')]
        status = state['status'] or ('watching' if enabled else 'off')
        message = state['lastMessage'] or ('監看 Downloads 的新 .mcpack／.mcaddon 檔案。' if enabled else '自動匯入目前關閉。')
        return {'enabled': enabled, 'version': state['version'], 'status': status,
                'lastFile': state['lastFile'], 'message': message, 'pending': len(pending)}

    def configure_resource_auto_import(self, payload):
        enabled = payload.get('enabled')
        if type(enabled) is not bool: raise UserError('自動匯入設定不正確。')
        version = payload.get('id')
        if enabled:
            if version == 'external': raise UserError('自動匯入只能安裝到 MambaCraft 管理的遊戲版本。')
            self.content_root(version)
            with self._resource_watch_lock:
                state = self._read_resource_watch()
                if not state['enabled']:
                    state = {'enabled': True, 'version': version,
                             'seen': {key: {'name': item['name'], 'status': 'existing'}
                                      for key, item in self._download_candidates().items()},
                             'pending': {}, 'lastFile': '', 'lastMessage': '', 'status': 'watching'}
                else:
                    state['version'] = version
                self._write_resource_watch(state)
        else:
            with self._resource_watch_lock:
                state = self._read_resource_watch()
                state['enabled'] = False
                state['status'] = 'off'
                state['lastMessage'] = '自動匯入已關閉。'
                self._write_resource_watch(state)
        return self.resource_auto_import_state()

    def _resource_watch_loop(self):
        while not getattr(self.engine, 'closing', False):
            try: self._scan_resource_downloads()
            except Exception:
                try:
                    with (self.engine.logs / 'helper.log').open('a', encoding='utf-8') as log:
                        log.write('Bedrock Downloads 自動匯入掃描失敗。\n')
                except OSError: pass
            time.sleep(2)

    def _scan_resource_downloads(self):
        candidates = self._download_candidates()
        if not candidates: return
        action = None
        with self._resource_watch_lock:
            state = self._read_resource_watch()
            if not state['enabled'] or not state['version']: return
            pending = state['pending']
            seen = state['seen']
            for signature, item in candidates.items():
                if signature in seen: continue
                current = pending.get(signature)
                if not isinstance(current, dict):
                    current = {'name': item['name'], 'stable': 0, 'status': 'waiting'}
                elif current.get('status') == 'waiting':
                    current['stable'] = min(int(current.get('stable', 0)) + 1, 99)
                pending[signature] = current
                if len(pending) > 200:
                    pending = dict(list(pending.items())[-200:]); state['pending'] = pending
                if current.get('status') == 'waiting':
                    state['lastFile'] = item['name']
                    state['status'] = 'waiting'
                    state['lastMessage'] = '正在等候下載完成：' + item['name']
            for signature, item in pending.items():
                if not isinstance(item, dict) or item.get('status') != 'waiting' or int(item.get('stable', 0)) < 2:
                    continue
                current_file = candidates.get(signature)
                if not current_file: continue
                item['status'] = 'installing'
                state['status'] = 'installing'
                state['lastFile'] = item['name']
                state['lastMessage'] = '下載完成，正在驗證並匯入：' + item['name']
                action = {'id': state['version'], 'local_path': str(self._downloads_root() / item['name']),
                          'auto_import': True, 'watch_signature': signature, 'watch_name': item['name'],
                          'expected_size': current_file['size'], 'expected_mtime_ns': current_file['mtime_ns']}
                break
            self._write_resource_watch(state)
        if not action: return
        try:
            if self._bedrock_process_running():
                with self._resource_watch_lock:
                    state = self._read_resource_watch(); item = state['pending'].get(action['watch_signature'], {})
                    if isinstance(item, dict): item['status'] = 'waiting'
                    state['status'] = 'waiting-game'
                    state['lastMessage'] = '基岩版仍在執行；退出遊戲後會自動匯入。'
                    self._write_resource_watch(state)
                return
            self.engine.start('bedrock-resource-auto-install', action)
        except UserError as exc:
            with self._resource_watch_lock:
                state = self._read_resource_watch(); item = state['pending'].get(action['watch_signature'], {})
                if isinstance(item, dict): item['status'] = 'waiting'
                state['status'] = 'waiting'
                state['lastMessage'] = str(exc)
                self._write_resource_watch(state)

    def auto_import_resource(self, payload):
        signature = payload.get('watch_signature')
        try:
            result = self.install_resource(payload)
        except Exception as exc:
            self._finish_auto_import(signature, payload.get('watch_name', ''), False, str(exc))
            raise
        self._finish_auto_import(signature, payload.get('watch_name', ''), True, result)
        return result

    def _finish_auto_import(self, signature, name, success, message):
        if not isinstance(signature, str) or not re.fullmatch(r'[a-f0-9]{64}', signature): return
        with self._resource_watch_lock:
            state = self._read_resource_watch()
            item = state['pending'].get(signature)
            if not isinstance(item, dict): return
            item['status'] = 'imported' if success else 'error'
            state['seen'][signature] = {'name': str(name)[:200], 'status': item['status']}
            if len(state['seen']) > 1000: state['seen'] = dict(list(state['seen'].items())[-1000:])
            state['status'] = item['status']
            state['lastFile'] = str(name)[:200]
            state['lastMessage'] = ('已自動匯入 ' + str(name) + '；請在世界設定中啟用資源包／行為包。') if success else ('無法自動匯入 ' + str(name) + '：' + str(message)[:240])
            self._write_resource_watch(state)

    def content_versions(self):
        import re
        from bedrock import _plain_child_dirs
        versions = {v['id'] for v in BedrockManager.state(self)['versions']}
        versions.update(p.name for p in _plain_child_dirs(self.launcher_data_root / 'bedrock-instances', within_root=self.launcher_data_root) if re.fullmatch(r'[0-9]+(?:\.[0-9]+){2,3}', p.name))
        return sorted(versions)

    def open_folder(self, kind, world_id=None, pack_type=None):
        root, custom = self._configured_path()
        if not custom and kind in ('root', 'versions'):
            safe_mkdir(self.launcher_data_root, root if kind == 'root' else root / 'versions')
        return super().open_folder(kind, world_id, pack_type)

    def content_root(self, version):
        if version == 'external': return self._configured_path()[0]
        if not isinstance(version, str) or version not in self.content_versions():
            raise UserError('請先選擇已安裝的基岩版版本。')
        return self.launcher_data_root / 'bedrock-instances' / version

    def content_manager(self, version):
        path = self.content_root(version)
        manager = BedrockManager(self.launcher_data_root / 'bedrock-instance-backups' / version)
        manager._configured_path = lambda: (path, False)
        return manager

    def content_state(self, payload):
        version = payload.get('id')
        result = self.content_manager(version).state()
        result['id'] = version
        result['backupPath'] = str(self.launcher_data_root / 'bedrock-instance-backups' / version / 'bedrock-backups')
        result['autoImport'] = self.resource_auto_import_state()
        return result

    def content_open(self, payload):
        version = payload.get('id')
        manager = self.content_manager(version)
        if payload.get('kind') in ('root', 'worlds', 'resource-packs', 'behavior-packs') and version != 'external':
            root = self.content_root(version)
            relative = {'root': Path('.'), 'worlds': WORLD_ROOT, **PACK_ROOTS}[payload['kind']]
            safe_mkdir(self.launcher_data_root, root / relative)
        return manager.open_folder(payload.get('kind'), payload.get('world_id'), payload.get('pack_type'))

    def content_backup(self, payload):
        if self._bedrock_process_running(): raise UserError('請先儲存並退出基岩版，再備份世界。')
        version = payload.get('id')
        manager = self.content_manager(version)
        safe_mkdir(self.launcher_data_root, manager.launcher_data_root)
        return manager.backup_world(payload.get('world_id'))

    def remove_version(self, payload):
        if self._bedrock_process_running(): raise UserError('請先退出基岩版，再移除遊戲版本。')
        root, custom = self._configured_path()
        if custom: raise UserError('外部遊戲版本請使用原啟動器管理。')
        version = payload.get('id')
        self.content_root(version)  # Validate installed identity before joining any path.
        target = root / 'versions' / version
        if not _safe_under(root, target): raise UserError('遊戲版本路徑不安全。')
        shutil.rmtree(target)
        return '已移除遊戲版本；世界與資源保留於：' + str(self.launcher_data_root / 'bedrock-instances' / version)

    def support_open(self, payload):
        paths = {'logs': self.engine.logs, 'runtime': self.runtime_home,
                 'backups': self.launcher_data_root / 'bedrock-instance-backups',
                 'compatibility': self.compat_bridge.home}
        path = paths.get(payload.get('kind'))
        if path is None: raise UserError('未知的支援資料位置。')
        safe_mkdir(self.launcher_data_root, path)
        subprocess.Popen(['/usr/bin/open', str(path)], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return '已在 Finder 開啟：' + str(path)

    def install_resource(self, payload):
        self._mac_check()
        if self._bedrock_process_running(): raise UserError('請先退出基岩版，再安裝附加內容。')
        version = payload.get('id')
        root = self.content_root(version)
        if version == 'external': raise UserError('請選擇由 MambaCraft 啟動的遊戲版本。')
        safe_mkdir(self.launcher_data_root, root)
        with tempfile.TemporaryDirectory(prefix='.resource-', dir=root) as temporary:
            stage = Path(temporary)
            if payload.get('url'):
                source = stage / 'download.mcpack'
                download_package(payload['url'], source, payload.get('sha256', ''), self.engine.cancel, self.engine.progress)
            elif payload.get('local_path'):
                if payload.get('auto_import') is not True:
                    raise UserError('本機檔案自動匯入要求無效。')
                downloads = self._downloads_root()
                source = Path(payload['local_path']).expanduser()
                if downloads is None or source.is_symlink() or source.suffix.lower() not in AUTO_IMPORT_SUFFIXES:
                    raise UserError('自動匯入只接受 Downloads 內已完成的 .mcpack 或 .mcaddon。')
                try:
                    source = source.resolve(strict=True)
                    if source.parent != downloads: raise ValueError()
                    info = source.stat(follow_symlinks=False)
                    if (info.st_size != payload.get('expected_size') or info.st_mtime_ns != payload.get('expected_mtime_ns')
                            or hashlib.sha256((source.name + '\0' + str(info.st_size) + '\0' + str(info.st_mtime_ns)).encode()).hexdigest() != payload.get('watch_signature')):
                        raise ValueError()
                except (OSError, RuntimeError, ValueError):
                    raise UserError('自動匯入檔案已變更或不在 Downloads 根目錄。') from None
            elif payload.get('choose') is True:
                picked = subprocess.run(['/usr/bin/osascript', '-e', 'POSIX path of (choose file with prompt "選擇基岩版 .mcpack、.mcaddon 或 ZIP 附加內容")'], capture_output=True, text=True)
                if picked.returncode: raise Cancelled('已取消選擇資源檔案。')
                source = Path(picked.stdout.strip())
            else: raise UserError('請貼上 HTTPS 直連，或選擇資源檔案。')
            if source.is_symlink() or not source.is_file() or source.stat().st_size > 512 * 1024**2:
                raise UserError('資源檔案不存在或超過 512 MB。')
            budget = [0, 0]
            def unpack(archive, destination, nested=False):
                try:
                    with zipfile.ZipFile(archive) as z:
                        names = set()
                        for info in z.infolist():
                            name = PurePosixPath(info.filename)
                            key = str(name).casefold()
                            budget[0] += 1; budget[1] += info.file_size
                            if (budget[0] > 20000 or budget[1] > 1024**3 or name.is_absolute() or '..' in name.parts
                                    or '\\' in info.filename or ':' in info.filename or key in names
                                    or stat.S_ISLNK(info.external_attr >> 16)):
                                raise UserError('資源包含不安全路徑、重複檔案或超出解壓限制。')
                            names.add(key)
                            target = destination.joinpath(*name.parts)
                            if info.is_dir(): target.mkdir(parents=True, exist_ok=True); continue
                            target.parent.mkdir(parents=True, exist_ok=True)
                            with z.open(info) as src, target.open('xb') as dst:
                                while chunk := src.read(1024 * 1024):
                                    if self.engine.cancel.is_set(): raise Cancelled('已取消資源安裝。')
                                    dst.write(chunk)
                        if not nested:
                            for inner in list(destination.rglob('*.mcpack')):
                                unpack(inner, destination / ('nested-' + uuid.uuid4().hex), True)
                except (zipfile.BadZipFile, RuntimeError, OSError) as exc:
                    if isinstance(exc, (UserError, Cancelled)): raise
                    raise UserError('資源包損壞或無法解壓，未安裝。') from exc
            extracted = stage / 'unpacked'; extracted.mkdir()
            unpack(source, extracted)
            plans = []; seen = set()
            for manifest in extracted.rglob('manifest.json'):
                if manifest.stat().st_size > 128 * 1024: raise UserError('資源包 manifest 過大。')
                try:
                    data = json.loads(manifest.read_text(encoding='utf-8-sig'))
                    header = data['header']; identity = str(uuid.UUID(header['uuid']))
                    types = {m['type'] for m in data['modules']}
                    kind = 'resource-packs' if types == {'resources'} else 'behavior-packs' if types and types <= {'data', 'script'} else None
                    if kind is None: raise ValueError()
                except (ValueError, KeyError, TypeError, UnicodeError):
                    raise UserError('無法辨識資源包或行為包的 manifest。') from None
                parent = safe_mkdir(self.launcher_data_root, root / PACK_ROOTS[kind])
                target = parent / identity
                if identity in seen or target.exists() or target.is_symlink():
                    raise UserError('這個附加包已安裝或套件內有重複項目；原有內容保留。')
                seen.add(identity); plans.append((manifest.parent, target))
            if not plans: raise UserError('找不到附加包 manifest；請選擇 .mcpack 或 .mcaddon。')
            # Overlapping pack roots would duplicate files and cannot form independent packs.
            if any(a != b and (a in b.parents or b in a.parents) for a, _ in plans for b, _ in plans):
                raise UserError('資源包目錄重疊，未安裝。')
            committed = []
            try:
                for source, target in plans:
                    if self.engine.cancel.is_set(): raise Cancelled('已取消資源安裝。')
                    os.rename(source, target); committed.append(target)
            except BaseException:
                for target in committed: shutil.rmtree(target, ignore_errors=True)
                raise
        return '附加內容已安裝至：' + str(root) + '。請在遊戲內的世界設定啟用資源包／行為包。'
