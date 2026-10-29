"""Managed runtime and user-supplied Android package lifecycle.

No embedded store authentication, game mirror list, or DRM modifications.
Runtime downloads retain the original pinned upstream release checksums.
"""
import base64
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import shutil
import stat
import struct
import subprocess
import tempfile
import time
import zipfile

import requests
from bedrock import BedrockManager, _safe_under, WORLD_ROOT, PACK_ROOTS
from core import UserError, Cancelled, atomic_json, read_json, host_arch, APP_VERSION
from bedrock_packages import package_apks, download_package, MAX_PACKAGE

ASSETS = Path(__file__).parent / 'bedrock_assets'
CATALOG_BASE = 'https://raw.githubusercontent.com/minecraft-linux/mcpelauncher-versiondb/master/'
VERSION = re.compile(r'^[0-9]+(?:\.[0-9]+){2,3}$')


def version_tuple(value):
    return tuple(int(x) for x in value.split('.')) if VERSION.fullmatch(value) else ()


def check_digest(path, expected):
    digest = hashlib.sha256()
    with Path(path).open('rb') as f:
        while chunk := f.read(1024 * 1024): digest.update(chunk)
    if not expected:
        return
    if re.fullmatch('[a-fA-F0-9]{64}', expected):
        matches = digest.hexdigest() == expected.lower()
    else:
        matches = base64.urlsafe_b64encode(digest.digest()).decode().rstrip('=') == expected.replace('+', '-').replace('/', '_').rstrip('=')
    if not matches: raise UserError('安裝包檔案校驗失敗。')


def parse_catalog(data, abi):
    if not isinstance(data, list) or len(data) > 20000:
        raise UserError('版本索引格式不正確。')
    result = {}
    for row in data:
        if (not isinstance(row, list) or len(row) < 3 or type(row[0]) is not int
                or not 0 < row[0] < 2**31 or not isinstance(row[1], str)
                or not VERSION.fullmatch(row[1]) or type(row[2]) is not int or row[2] not in (0, 1)):
            raise UserError('版本索引包含不正確的項目。')
        result[row[0]] = {'id': row[1], 'code': row[0], 'abi': abi, 'beta': bool(row[2]),
                         'availability': 'reference-only'}
    return sorted(result.values(), key=lambda x: (version_tuple(x['id']), x['code']), reverse=True)


def manifest_attributes(data):
    """Read only root manifest attributes from Android binary XML (no execution)."""
    if len(data) < 8 or len(data) > 4 * 1024 * 1024:
        raise UserError('Android manifest 大小不正確。')
    strings = []
    u16 = lambda p: struct.unpack_from('<H', data, p)[0]
    u32 = lambda p: struct.unpack_from('<I', data, p)[0]
    def length(p, utf8):
        n = data[p] if utf8 else u16(p); p += 1 if utf8 else 2
        flag = 128 if utf8 else 32768
        if n & flag:
            n = ((n & (flag - 1)) << (8 if utf8 else 16)) | (data[p] if utf8 else u16(p))
            p += 1 if utf8 else 2
        return n, p
    try:
        if u16(0) != 3 or u32(4) != len(data):
            raise ValueError()
        offset = u16(2)
        while offset + 8 <= len(data):
            kind, header, size = struct.unpack_from('<HHI', data, offset)
            if size < header or header < 8 or offset + size > len(data):
                raise ValueError()
            if kind == 1:
                count, _, flags, start = struct.unpack_from('<4I', data, offset + 8)
                if count > 100000 or header + count * 4 > size:
                    raise ValueError()
                for i in range(count):
                    pos = offset + start + u32(offset + header + i * 4)
                    utf8 = bool(flags & 256)
                    n, pos = length(pos, utf8)
                    if utf8: n, pos = length(pos, True)
                    end = pos + n * (1 if utf8 else 2)
                    if end > offset + size: raise ValueError()
                    strings.append(data[pos:end].decode('utf-8' if utf8 else 'utf-16le'))
            elif kind == 0x102:
                ext = offset + header
                name = strings[u32(ext + 4)]
                if name != 'manifest': raise ValueError()
                start, width, count = struct.unpack_from('<HHH', data, ext + 8)
                if width < 20 or ext + start + count * width > offset + size: raise ValueError()
                attrs = {}
                for i in range(count):
                    p = ext + start + width * i
                    key = strings[u32(p + 4)]; raw = u32(p + 8); typ = data[p + 15]; value = u32(p + 16)
                    attrs[key] = strings[raw] if raw != 0xffffffff else strings[value] if typ == 3 else value
                return attrs
            offset += size
    except (ValueError, IndexError, UnicodeError, struct.error):
        pass
    raise UserError('無法驗證安裝包的 Android manifest。')


def extract_game(files, target, version, abi, cancel):
    """Merge user-supplied base/split APKs into a fresh directory, bounded and checked."""
    target = Path(target)
    if target.exists(): raise UserError('這個版本已存在，已保留原本的遊戲檔案。')
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.bedrock-install-', dir=target.parent) as temp:
        stage = Path(temp) / 'payload'; stage.mkdir()
        total = 0; entries = 0; has_base = False
        for path in files:
            with zipfile.ZipFile(path) as archive:
                info = archive.getinfo('AndroidManifest.xml')
                if info.file_size > 4 * 1024 * 1024: raise UserError('APK manifest 過大。')
                attrs = manifest_attributes(archive.read(info))
                if attrs.get('package') != 'com.mojang.minecraftpe' or attrs.get('versionCode') != version['code']:
                    raise UserError('安裝包的遊戲或版本不一致，未安裝。')
                is_base = not attrs.get('split')
                if is_base:
                    if has_base or attrs.get('versionName') != version['id']:
                        raise UserError('安裝包版本名稱不一致，未安裝。')
                    has_base = True
                archive_names = set()
                for member in archive.infolist():
                    if cancel.is_set(): raise Cancelled('已取消安裝。')
                    name = member.filename; parts = PurePosixPath(name).parts
                    if not parts or name.startswith('/') or '\\' in name or '..' in parts or stat.S_ISLNK(member.external_attr >> 16):
                        raise UserError('APK 含不安全的路徑。')
                    if name in archive_names: raise UserError('APK 含重複路徑。')
                    archive_names.add(name)
                    total += member.file_size; entries += 1
                    if total > 6 * 1024**3 or entries > 200000: raise UserError('APK 超過安裝大小限制。')
                    if member.is_dir(): continue
                    if name == 'AndroidManifest.xml':
                        if not is_base: continue
                        mapped = name
                    elif name.startswith(('assets/', 'lib/')): mapped = name
                    elif name.startswith('res/raw/'): mapped = 'assets/' + name[len('res/raw/'):]
                    else: continue
                    destination = stage / mapped
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    if destination.exists():
                        raise UserError('APK 含重複遊戲檔案，無法安全合併。')
                    with archive.open(member) as src, destination.open('xb') as dst:
                        while chunk := src.read(1024 * 1024):
                            if cancel.is_set(): raise Cancelled('已取消安裝。')
                            dst.write(chunk)
        if not has_base or not (stage / 'lib' / abi / 'libminecraftpe.so').is_file() or not (stage / 'assets').is_dir():
            raise UserError('安裝包缺少對應此 Mac 的遊戲程式或資源。請檢查是否選齊 base 與 split APK。')
        with (stage / 'lib' / abi / 'libminecraftpe.so').open('rb') as f: elf = f.read(20)
        expected_machine = 183 if abi == 'arm64-v8a' else 62
        if len(elf) < 20 or elf[:6] != b'\x7fELF\x02\x01' or struct.unpack_from('<H', elf, 18)[0] != expected_machine:
            raise UserError('安裝包的遊戲程式架構不正確。')
        atomic_json(stage / 'mambacraft-version.json', {**version, 'installedAt': time.time()})
        if cancel.is_set(): raise Cancelled('已取消安裝。')
        stage.rename(target)


from bedrock_content import ContentMixin, safe_mkdir
from bedrock_compatibility import CompatibilityBridge, failure_detail, bridge_loaded


class IntegratedBedrockManager(ContentMixin, BedrockManager):
    def __init__(self, engine):
        super().__init__(engine.root)
        self.engine = engine
        self.runtime_home = self.launcher_data_root / 'bedrock-runtime'
        self.arch = {'aarch64': 'arm64'}.get(host_arch(), host_arch())
        self.abi = 'arm64-v8a' if self.arch == 'arm64' else 'x86_64'
        self.runtime_manifest = read_json(ASSETS / 'runtimes.json')
        self.catalog = self._load_catalog()
        self.game = None
        self.game_exit = None
        self.game_log = self.engine.logs / 'bedrock-game.log'
        self.init_resource_watch()
        self.active_version = None
        self.compat_bridge = CompatibilityBridge(self)

    def _configured_path(self):
        path, custom = super()._configured_path()
        return (path, True) if custom else (self.launcher_data_root / 'bedrock-data', False)

    def _load_catalog(self):
        cache = self.launcher_data_root / ('bedrock-catalog-' + self.abi + '.json')
        try: return parse_catalog(read_json(cache), self.abi)
        except (OSError, ValueError, UserError):
            return parse_catalog(read_json(ASSETS / ('versions.' + self.abi + '.json')), self.abi)

    def _mac_check(self):
        if platform.system() != 'Darwin' or self.arch not in ('arm64', 'x86_64'):
            raise UserError('此基岩版整合目前只支援 Apple Silicon 與 Intel Mac。')
        minimum = self.runtime_manifest[self.arch]['minMacOS']
        current = tuple(int(x) for x in (platform.mac_ver()[0] or '0').split('.')[:2])
        if current < tuple(int(x) for x in minimum.split('.')[:2]):
            raise UserError('此基岩版執行核心需要 macOS ' + minimum + ' 或更新版本。')

    def _runtime_app(self):
        spec = self.runtime_manifest[self.arch]
        return self.runtime_home / (self.arch + '-' + spec['tag']) / 'Minecraft Bedrock Launcher.app'

    def _runtime_client(self):
        folder = self._runtime_app() / 'Contents' / 'MacOS'
        names = ['mcpelauncher-client-arm64-v8a', 'mcpelauncher-client'] if self.arch == 'arm64' else ['mcpelauncher-client']
        return next((folder / name for name in names if (folder / name).is_file()), folder / names[0])

    def runtime_ready(self):
        app = self._runtime_app()
        try:
            receipt = read_json(app.parent / 'receipt.json')
            return receipt.get('sha256') == self.runtime_manifest[self.arch]['sha256'] and self._runtime_client().is_file()
        except (OSError, ValueError, AttributeError): return False

    def compatibility(self, version):
        value = version_tuple(version)
        lower = (1, 19, 70) if self.arch == 'arm64' else (1, 13, 0)
        if self.arch == 'x86_64' and (1, 16, 210) <= value < (1, 17, 50):
            return 'known-issues'  # Upstream reports crafting bugs and world corruption.
        # Conservative baseline from upstream's published requirements; never assert tested playability.
        if value and lower <= value <= (1, 21, 73, 99):
            return 'candidate'
        return 'unverified'

    def launch_block_reason(self, version):
        if not isinstance(version, str) or not VERSION.fullmatch(version):
            return '版本名稱無法辨識，請重新匯入遊戲安裝包。'
        if self.compatibility(version) == 'known-issues':
            return '此 Intel 版本已知可能損壞世界，請改用其他遊戲版本。'
        root, _ = self._configured_path()
        if self.arch == 'arm64' and version_tuple(version) > (1, 21, 73, 99):
            fallback = root / 'versions' / '1.21.71.01' / 'lib' / self.abi / 'libminecraftpe.so'
            message = '此版本超出 Apple Silicon 核心目前公布的支援範圍（最高至 Minecraft 1.21.73）。'
            if version in ('1.21.132.1', '1.26.52.3'):
                message += f' 你提供的 {version} 日誌已顯示它在 PlayFab 初始化時崩潰。'
            else:
                message += ' 此版本尚未驗證，已停止啟動以避免相同類型的崩潰。'
            if _safe_under(root, fallback) and fallback.is_file():
                message += ' 你已安裝的 1.21.71.01 位於支援範圍內，請改選該版本。'
            else:
                message += ' 請匯入 1.21.73 或較舊、屬於支援範圍的遊戲版本。'
            return message
        library = root / 'versions' / version / 'lib' / self.abi / 'libminecraftpe.so'
        if not _safe_under(root, library) or not library.is_file():
            return '此版本缺少 ' + self.abi + ' 遊戲程式，請匯入適合這台 Mac 的完整安裝包。'
        return ''

    def state(self):
        result = super().state()
        for item in result['versions']:
            item['compatibility'] = self.compatibility(item['id'])
            item['launchBlockReason'] = self.launch_block_reason(item['id'])
            item['canLaunch'] = not item['launchBlockReason']
        result.update(runtime={'ready': self.runtime_ready(), 'tag': self.runtime_manifest[self.arch]['tag'],
                               'architecture': self.arch, 'size': self.runtime_manifest[self.arch]['size']},
                      catalog=[dict(v, compatibility=self.compatibility(v['id'])) for v in self.catalog],
                      running=bool(self.game and self.game.poll() is None), lastExit=self.game_exit,
                      activeVersion=self.active_version, job=dict(self.engine.job),
                      managedRoot=str(self.launcher_data_root / 'bedrock-data'),
                      acquisition={'local': True, 'https': True, 'builtInGameSources': []},
                      macOSMinimum=self.runtime_manifest[self.arch]['minMacOS'],
                      catalogSource=CATALOG_BASE + 'versions.' + self.abi + '.json.min')
        result['compatibilityBridge'] = {'id': self.compat_bridge.spec['id'], 'ready': self.compat_bridge.ready(), 'path': str(self.compat_bridge.home), 'games': list(self.compat_bridge.spec['games'])}
        result['contentVersions'] = self.content_versions()
        result['locations'] = {'runtime': str(self.runtime_home), 'logs': str(self.engine.logs), 'gameLog': str(self.game_log), 'backups': str(self.launcher_data_root / 'bedrock-instance-backups'), 'instances': str(self.launcher_data_root / 'bedrock-instances'), 'compatibility': str(self.compat_bridge.home)}
        for item in result['versions']:
            item['dataPath'] = str(self.launcher_data_root / 'bedrock-instances' / item['id'])
            item['storage'] = self.storage_state(Path(item['dataPath']))
        return result

    def storage_state(self, data):
        """Read the volume that actually contains this version's world data."""
        try:
            current = Path(data)
            while True:
                if current.is_symlink(): raise OSError('資料路徑含符號連結。')
                if current == self.launcher_data_root: break
                if current == current.parent: raise OSError('資料路徑超出管理範圍。')
                current = current.parent
            probe = Path(data)
            while not probe.exists(): probe = probe.parent
            usage = shutil.disk_usage(probe)
            return {'freeBytes': usage.free, 'totalBytes': usage.total, 'volumePath': str(probe), 'error': ''}
        except OSError as exc:
            return {'freeBytes': None, 'totalBytes': None, 'volumePath': str(data), 'error': str(exc)}

    def check_world_storage(self, data):
        info = self.storage_state(data)
        if info['error']: raise UserError('無法讀取世界存檔空間：' + str(data) + '。' + info['error'])
        if info['freeBytes'] < 256 * 1024**2:
            raise UserError('世界存檔所在磁碟可用空間不足 256 MiB，請先釋放空間。存檔位置：' + str(data))
        try:
            with tempfile.NamedTemporaryFile(prefix='.mamba-write-check-', dir=data) as probe:
                probe.write(b'MambaCraft world storage check\n'); probe.flush(); os.fsync(probe.fileno())
                probe.seek(0)
                if probe.read() != b'MambaCraft world storage check\n': raise OSError('寫入後讀取不一致。')
        except OSError as exc:
            raise UserError('無法寫入世界存檔資料夾：' + str(data) + '。' + str(exc)) from exc
        return info

    def preserve_previous_game_log(self):
        if not self.game_log.is_file() or self.game_log.is_symlink(): return
        with self.game_log.open('rb') as stream: header = stream.read(1024).decode('utf-8', errors='replace')
        match = re.search(r'^Version: ([0-9]+(?:\.[0-9]+){2,3})$', header, re.M)
        if match:
            target = self.engine.logs / ('bedrock-game-' + match.group(1) + '.log')
            if target.is_symlink(): raise UserError('版本日誌路徑含符號連結。')
            shutil.copyfile(self.game_log, target)

    def set_root(self, path):
        with self.engine.lock:
            if self.engine.job.get('status') == 'running' or self.game and self.game.poll() is None:
                raise UserError('請先完成工作及退出遊戲，再更改資料位置。')
            if path is None or path == '':
                self.config_path.unlink(missing_ok=True)
                return '已使用 MambaCraft 管理的 Bedrock 資料位置。'
            return super().set_root(path)

    def launch_upstream(self):
        raise UserError('此版本已改為直接啟動遊戲。請選擇已安裝的基岩版版本。')

    def refresh_catalog(self, payload):
        self.engine.progress('正在更新基岩版版本清單…')
        url = CATALOG_BASE + 'versions.' + self.abi + '.json.min'
        with requests.get(url, timeout=(10, 30), stream=True) as response:
            response.raise_for_status(); content = bytearray()
            for chunk in response.iter_content(65536):
                if self.engine.cancel.is_set(): raise Cancelled('已取消更新。')
                content.extend(chunk)
                if len(content) > 4 * 1024**2: raise UserError('版本清單過大。')
        data = json.loads(content)
        catalog = parse_catalog(data, self.abi)
        if not catalog: raise UserError('版本來源回傳空清單，已保留快取。')
        atomic_json(self.launcher_data_root / ('bedrock-catalog-' + self.abi + '.json'), data)
        self.catalog = catalog
        return f'已更新 {len(catalog)} 筆基岩版版本資料。此清單僅供版本與相容性參考，不代表有下載來源。'

    def prepare_runtime(self, payload):
        self._mac_check()
        if self.runtime_ready(): return '基岩版執行核心已就緒。'
        spec = self.runtime_manifest[self.arch]
        self.runtime_home.mkdir(parents=True, exist_ok=True)
        if not _safe_under(self.launcher_data_root, self.runtime_home): raise UserError('核心資料夾不安全，請檢查符號連結。')
        if shutil.disk_usage(self.runtime_home).free < 3 * 1024**3: raise UserError('準備基岩版核心至少需要 3 GB 可用空間。')
        with tempfile.TemporaryDirectory(prefix='.install-', dir=self.runtime_home) as temp:
            temp = Path(temp); archive = temp / 'runtime.dmg'; digest = hashlib.sha256(); done = 0
            self.engine.progress('正在下載基岩版執行核心…', 0, spec['size'])
            with requests.get(spec['url'], stream=True, timeout=(10, 30)) as response:
                response.raise_for_status()
                with archive.open('xb') as f:
                    for chunk in response.iter_content(1024 * 1024):
                        if self.engine.cancel.is_set(): raise Cancelled('已取消核心下載。')
                        done += len(chunk)
                        if done > spec['size']: raise UserError('核心檔案大小不符。')
                        digest.update(chunk); f.write(chunk); self.engine.progress(done=done)
            if done != spec['size'] or digest.hexdigest() != spec['sha256']:
                raise UserError('核心校驗失敗，未安裝；請重新下載。')
            return self._install_runtime_archive(archive, temp, spec)

    def _install_runtime_archive(self, archive, temp, spec):
        self.engine.progress('正在驗證及安裝基岩版核心…', 0, 0)
        mount = temp / 'mount'; mount.mkdir(); stage = temp / 'ready'; stage.mkdir()
        mounted = False
        try:
            subprocess.run(['/usr/bin/hdiutil', 'attach', str(archive), '-nobrowse', '-readonly', '-mountpoint', str(mount)],
                           check=True, capture_output=True, timeout=120)
            mounted = True
            apps = list(mount.glob('*.app'))
            if len(apps) != 1: raise UserError('核心套件結構不正確。')
            app = stage / 'Minecraft Bedrock Launcher.app'
            subprocess.run(['/usr/bin/ditto', str(apps[0]), str(app)], check=True, capture_output=True, timeout=120)
            client = app / 'Contents/MacOS/mcpelauncher-client'
            if not client.is_file(): raise UserError('核心套件缺少遊戲執行檔。')
            archs = subprocess.run(['/usr/bin/lipo', '-archs', str(client)], capture_output=True, text=True, check=True, timeout=10).stdout.split()
            if self.arch not in archs: raise UserError('核心套件與這台 Mac 的架構不符。')
            if self.engine.cancel.is_set(): raise Cancelled('已取消安裝核心。')
            atomic_json(stage / 'receipt.json', spec)
            destination = self._runtime_app().parent
            if destination.exists():
                raise UserError('已有不完整的核心目錄；請先保留診斷資料並移走該目錄，再重試。')
            stage.rename(destination)
        finally:
            if mounted:
                subprocess.run(['/usr/bin/hdiutil', 'detach', str(mount)], capture_output=True, timeout=30, check=True)
        return '基岩版執行核心已安裝；不需要另一套啟動器。'

    def install_game(self, payload):
        self._mac_check()
        if self._bedrock_process_running():
            raise UserError('請先儲存並退出基岩版，再匯入安裝包。')
        root, custom = self._configured_path()
        if custom: raise UserError('安裝新版本請先按「使用 MambaCraft 資料位置」，外部資料只供讀取及啟動。')
        url = payload.get('url')
        paths = payload.get('paths')
        if bool(url) == bool(paths): raise UserError('請選擇本機安裝包或填寫 HTTPS 直連。')
        root.mkdir(parents=True, exist_ok=True)
        if not _safe_under(self.launcher_data_root, root): raise UserError('遊戲資料夾不安全，請檢查符號連結。')
        (root / 'versions').mkdir(exist_ok=True)
        if not _safe_under(root, root / 'versions'): raise UserError('版本資料夾不安全，請檢查符號連結。')
        if shutil.disk_usage(root).free < 12 * 1024**3: raise UserError('匯入基岩版至少需要 12 GB 暫存及安裝空間。')
        with tempfile.TemporaryDirectory(prefix='.package-', dir=root) as temp:
            temp = Path(temp)
            hashes = []
            if url:
                path = temp / 'download.package'
                digest = download_package(url, path, payload.get('sha256', ''), self.engine.cancel, self.engine.progress)
                originals = [path]; hashes.append(digest)
                source = 'custom-https'
            else:
                if not isinstance(paths, list) or not 1 <= len(paths) <= 64:
                    raise UserError('請選擇一個安裝包，或最多 64 個 base／split APK。')
                originals = []; input_total = 0
                for i, value in enumerate(paths):
                    if not isinstance(value, str) or len(value) > 4096: raise UserError('安裝包路徑不合法。')
                    original = Path(value).expanduser()
                    if original.is_symlink() or not original.is_file() or not 0 < original.stat().st_size <= MAX_PACKAGE:
                        raise UserError('找不到安裝包，或檔案超過 3 GB。')
                    # Snapshot before parsing so the original is never modified or used during launch.
                    path = temp / ('input-' + str(i) + original.suffix.lower())
                    digest = hashlib.sha256(); size = 0
                    self.engine.progress('正在讀取本機安裝包…', 0, original.stat().st_size)
                    with original.open('rb') as incoming, path.open('xb') as outgoing:
                        while chunk := incoming.read(1024 * 1024):
                            if self.engine.cancel.is_set(): raise Cancelled('已取消匯入。')
                            size += len(chunk); input_total += len(chunk)
                            if input_total > 6 * 1024**3: raise UserError('安裝包總大小超過 6 GB。')
                            if size > MAX_PACKAGE: raise UserError('安裝包超過 3 GB 限制。')
                            digest.update(chunk); outgoing.write(chunk); self.engine.progress(done=size)
                    originals.append(path); hashes.append(digest.hexdigest())
                source = 'local-package'
            self.engine.progress('正在檢查安裝包版本及 CPU 架構…', 0, 0)
            try:
                files = package_apks(originals, temp, self.engine.cancel)
                base = []
                for path in files:
                    with zipfile.ZipFile(path) as archive:
                        info = archive.getinfo('AndroidManifest.xml')
                        if info.file_size > 4 * 1024**2: raise UserError('APK manifest 過大。')
                        attrs = manifest_attributes(archive.read(info))
                        if not attrs.get('split'): base.append(attrs)
                if len(base) != 1: raise UserError('請選齊安裝包；必須包含唯一的 base APK。')
                attrs = base[0]
                name, code = attrs.get('versionName'), attrs.get('versionCode')
                if (attrs.get('package') != 'com.mojang.minecraftpe' or not isinstance(name, str)
                        or not VERSION.fullmatch(name) or type(code) is not int or not 0 < code < 2**31):
                    raise UserError('這不是可辨識的 Minecraft Android 正式版安裝包。')
                item = {'id': name, 'code': code, 'abi': self.abi, 'source': source, 'packageSha256': hashes}
                target = root / 'versions' / name
                self.engine.progress('正在驗證及安裝遊戲…', 0, 0)
                extract_game(files, target, item, self.abi, self.engine.cancel)
            except (zipfile.BadZipFile, KeyError, NotImplementedError, RuntimeError):
                raise UserError('安裝包不完整或無法讀取，未安裝。') from None
        return '已匯入 Minecraft Bedrock ' + name + '。' + (self.launch_block_reason(name) or ('可以按「開始遊戲」啟動；此版本相容性尚未實測。' if self.compatibility(name) == 'unverified' else '可以按「開始遊戲」啟動。'))

    def launch_game(self, payload):
        self._mac_check()
        version = payload.get('id')
        if not isinstance(version, str) or not VERSION.fullmatch(version): raise UserError('請選擇有效的基岩版版本。')
        reason = self.launch_block_reason(version)
        if reason: raise UserError(reason)
        if self._bedrock_process_running():
            raise UserError('另一個基岩版遊戲仍在執行。請先儲存並退出，再啟動版本。')
        root, _ = self._configured_path(); game = root / 'versions' / version
        if not _safe_under(root, game / 'lib' / self.abi / 'libminecraftpe.so'):
            raise UserError('此版本缺少適合這台 Mac 的遊戲程式。')
        # Every managed version has independent worlds; switching old versions cannot upgrade/damage another world's files.
        data = self.launcher_data_root / 'bedrock-instances' / version
        safe_mkdir(self.launcher_data_root, data)
        for relative in (WORLD_ROOT, *PACK_ROOTS.values(), Path('files'), Path('cache')): safe_mkdir(self.launcher_data_root, data / relative)
        storage = self.check_world_storage(data)
        self.prepare_runtime({})
        compatibility = self.compat_bridge.prepare(version)
        client = self._runtime_client()
        env = os.environ.copy(); env['PATH'] = str(client.parent) + os.pathsep + env.get('PATH', '')
        env['ANGLE_DEFAULT_PLATFORM'] = 'metal'
        resources = self._runtime_app() / 'Contents' / 'Resources'
        env['XDG_DATA_DIRS'] = str(resources) + (os.pathsep + env['XDG_DATA_DIRS'] if env.get('XDG_DATA_DIRS') else '')
        cache = data / 'cache'; cache.mkdir(exist_ok=True)
        arguments = [str(client), '-dg', str(game), '-dd', str(data), '-dc', str(cache)]
        if self.arch == 'arm64': arguments.append('-fes')
        if compatibility:
            arguments.extend(['-m', str(compatibility)])
            env['MAMBACRAFT_COMPAT_DIR'] = str(compatibility)
            env['MAMBACRAFT_INSTANCE_DIR'] = str(data)
        if self.engine.cancel.is_set(): raise Cancelled('已取消啟動。')
        self.preserve_previous_game_log()
        with self.game_log.open('wb') as log:
            log.write(('MambaCraft Bedrock launch\nLauncher: ' + APP_VERSION + '\nVersion: ' + version + '\nRuntime: ' + self.runtime_manifest[self.arch]['tag'] + '\nArchitecture: ' + self.abi + '\nGame directory: ' + str(game) + '\nWorld data directory: ' + str(data) + '\nWorld volume available bytes: ' + str(storage['freeBytes']) + '\nWorld directory write/read check: passed\nCompatibility bridge: ' + (str(compatibility) if compatibility else 'not required for this version') + '\n\n').encode('utf-8'))
            log.flush()
            proc = subprocess.Popen(arguments, cwd=client.parent,
                                    env=env, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                                    start_new_session=True)
        self.game = proc; self.game_exit = None; self.active_version = version
        self.engine.progress('基岩版程式已啟動，等待遊戲視窗；可玩性需以實際進入世界確認。')
        code = proc.wait()
        self.game_exit = code
        if code or compatibility is not None and not bridge_loaded(self.game_log):
            raise UserError(failure_detail(self.game_log, code, compatibility is not None) + f' 退出代碼：{code}。日誌位置：{self.game_log}')
        return '基岩版程式已正常結束。'

    def prepare_compatibility(self, payload):
        self._mac_check()
        if self._bedrock_process_running():raise UserError('請先退出基岩版，再準備相容補丁。')
        path=self.compat_bridge.prepare(payload.get('id'))
        return ('相容補丁已準備：'+str(path)) if path else '此版本不需要這組相容補丁。'

    def instance_root(self, version):
        if not isinstance(version, str) or not VERSION.fullmatch(version): raise UserError('版本識別資料不合法。')
        path = self.launcher_data_root / 'bedrock-instances' / version
        if not _safe_under(self.launcher_data_root, path): raise UserError('此版本尚未建立獨立存檔。')
        return path

    def instance_action(self, payload):
        path = self.instance_root(payload.get('id'))
        if payload.get('backup'):
            self.engine.progress('正在備份這個版本的所有世界…')
            manager = BedrockManager(self.launcher_data_root / 'bedrock-instance-backups' / payload['id'])
            manager.set_root(str(path))
            worlds = manager.state()['worlds']
            if not worlds: return '這個版本目前沒有可備份的世界。'
            for world in worlds: manager.backup_world(world['id'])
            return f'已備份 {len(worlds)} 個世界。'
        subprocess.Popen(['/usr/bin/open', str(path)], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return '已開啟此版本的獨立存檔及資源包資料夾。'
