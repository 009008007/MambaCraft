"""Read-only discovery and safe world backup for an existing mcpelauncher install.

This module deliberately does not acquire, redistribute, or install Minecraft
Bedrock game files.  It manages files that the user already has locally.
"""
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import time
import uuid
import zipfile

from core import UserError, atomic_json, read_json


DEFAULT_DATA_ROOT = Path.home() / 'Library' / 'Application Support' / 'mcpelauncher'
APP_BUNDLES = (
    Path('/Applications/Minecraft Bedrock Launcher.app'),
    Path.home() / 'Applications' / 'Minecraft Bedrock Launcher.app',
)
WORLD_ROOT = Path('games') / 'com.mojang' / 'minecraftWorlds'
PACK_ROOTS = {
    'resource-packs': Path('games') / 'com.mojang' / 'resource_packs',
    'behavior-packs': Path('games') / 'com.mojang' / 'behavior_packs',
}
OPEN_TARGETS = {
    'root': Path('.'),
    'versions': Path('versions'),
    'worlds': WORLD_ROOT,
    'resource-packs': PACK_ROOTS['resource-packs'],
    'behavior-packs': PACK_ROOTS['behavior-packs'],
}


def normalize_data_root(path):
    """Accept a data root or one of its recognizable subfolders."""
    try:
        candidate = Path(path).expanduser().resolve(strict=True)
    except (OSError, RuntimeError, TypeError) as exc:
        raise UserError('找不到所選資料夾。') from exc
    if not candidate.is_dir():
        raise UserError('所選位置不是資料夾。')
    if candidate.name == 'versions':
        return candidate.parent
    if candidate.parent.name == 'versions':
        return candidate.parent.parent
    # Accept the common world / pack folders and normalize them to the root.
    for ancestor in (candidate, *candidate.parents):
        if ancestor.name == 'com.mojang' and ancestor.parent.name == 'games':
            return ancestor.parent.parent
    if candidate.name == 'games':
        return candidate.parent
    return candidate


def _safe_under(root, path):
    try:
        root = Path(root).resolve(strict=True)
        path = Path(path)
        relative = path.relative_to(root)
        current = root
        for part in relative.parts:
            current = current / part
            if current.is_symlink():
                return False
        return path.resolve(strict=True).is_relative_to(root)
    except (OSError, RuntimeError, ValueError):
        return False


def _plain_child_dirs(path, limit=500, within_root=None):
    if (within_root is not None and not _safe_under(within_root, path)) or path.is_symlink() or not path.is_dir():
        return []
    try:
        items = sorted(path.iterdir(), key=lambda p: p.name.casefold())
    except OSError:
        return []
    return [p for p in items[:limit] if not p.is_symlink() and p.is_dir() and (within_root is None or _safe_under(within_root, p))]


def _raise_walk_error(error):
    raise error


def _pack_info(folder):
    result = {'id': folder.name, 'name': folder.name, 'version': '', 'path': str(folder)}
    manifest = folder / 'manifest.json'
    if manifest.is_symlink() or not manifest.is_file():
        return result
    try:
        if manifest.stat().st_size > 128 * 1024:
            return result
        data = json.loads(manifest.read_text(encoding='utf-8'))
        header = data.get('header') if isinstance(data, dict) else None
        if not isinstance(header, dict):
            return result
        name = header.get('name')
        version = header.get('version')
        if isinstance(name, str) and name.strip():
            result['name'] = name.strip()[:200]
        if isinstance(version, list) and version and all(isinstance(part, (str, int)) for part in version):
            result['version'] = '.'.join(str(part) for part in version)[:80]
        elif isinstance(version, (str, int, float)):
            result['version'] = str(version)[:80]
    except (OSError, UnicodeError, ValueError, TypeError):
        pass
    return result


class BedrockManager:
    def __init__(self, launcher_data_root):
        self.launcher_data_root = Path(launcher_data_root).resolve()
        self.config_path = self.launcher_data_root / 'bedrock.json'
        self.launcher_data_root.mkdir(parents=True, exist_ok=True)

    def _configured_path(self):
        try:
            value = read_json(self.config_path).get('data_root')
        except (OSError, ValueError, AttributeError):
            value = None
        if isinstance(value, str) and value.strip():
            try:
                return Path(value).expanduser().resolve(strict=False), True
            except (OSError, RuntimeError):
                return Path(value).expanduser(), True
        return DEFAULT_DATA_ROOT.resolve(strict=False), False

    def set_root(self, path):
        if path is None or path == '':
            self.config_path.unlink(missing_ok=True)
            return '已恢復 mcpelauncher 預設資料位置。'
        if not isinstance(path, str) or len(path) > 2048:
            raise UserError('Bedrock 資料夾路徑不合法。')
        normalized = normalize_data_root(path)
        atomic_json(self.config_path, {'data_root': str(normalized)})
        return '已設定 Bedrock 資料位置：' + str(normalized)

    @staticmethod
    def _launcher_app():
        for path in APP_BUNDLES:
            try:
                if path.is_dir():
                    return str(path.resolve(strict=True))
            except OSError:
                continue
        return None

    @staticmethod
    def _world_name(folder):
        name_file = folder / 'levelname.txt'
        if not name_file.is_symlink() and name_file.is_file():
            try:
                value = name_file.read_text(encoding='utf-8', errors='replace').strip()
                if value:
                    return value[:200]
            except OSError:
                pass
        return folder.name

    def state(self):
        root, configured = self._configured_path()
        root_exists = root.is_dir() and not root.is_symlink()
        versions = []
        version_root = root / 'versions'
        for folder in _plain_child_dirs(version_root, within_root=root):
            lib = folder / 'lib'
            architectures = [p.name for p in _plain_child_dirs(lib, limit=20, within_root=root)]
            versions.append({'id': folder.name, 'path': str(folder), 'architectures': architectures})

        worlds = []
        worlds_root = root / WORLD_ROOT
        for folder in _plain_child_dirs(worlds_root, within_root=root):
            level_dat = folder / 'level.dat'
            database = folder / 'db'
            if not ((not level_dat.is_symlink() and level_dat.is_file()) or
                    (not database.is_symlink() and database.is_dir())):
                continue
            worlds.append({'id': folder.name, 'name': self._world_name(folder), 'path': str(folder)})

        packs = {}
        for kind, relative in PACK_ROOTS.items():
            packs[kind] = [_pack_info(folder) for folder in _plain_child_dirs(root / relative, within_root=root)]

        return {
            'dataRoot': str(root), 'dataRootExists': root_exists,
            'customRoot': configured, 'customRootMissing': configured and not root_exists,
            'launcherApp': self._launcher_app(),
            'versions': versions, 'worlds': worlds, 'packs': packs,
            'paths': {key: str(root / relative) for key, relative in OPEN_TARGETS.items()},
        }

    def open_folder(self, kind, world_id=None, pack_type=None):
        if kind not in OPEN_TARGETS and kind not in ('world', 'version', 'pack'):
            raise UserError('未知的 Bedrock 資料夾。')
        root, _ = self._configured_path()
        if kind in ('world', 'version', 'pack'):
            if not isinstance(world_id, str) or not world_id or world_id in ('.', '..') or '/' in world_id or '\\' in world_id:
                raise UserError('資料夾識別資料不合法。')
            if kind == 'world':
                parent = root / WORLD_ROOT
            elif kind == 'version':
                parent = root / 'versions'
            else:
                if pack_type not in PACK_ROOTS:
                    raise UserError('未知的 Bedrock 資源包類型。')
                parent = root / PACK_ROOTS[pack_type]
            path = parent / world_id
            if not _safe_under(root, parent) or not _safe_under(root, path) or path.parent.resolve() != parent.resolve():
                raise UserError('找不到這個資料夾，請重新掃描。')
        else:
            path = root / OPEN_TARGETS[kind]
            if not _safe_under(root, path):
                raise UserError('找不到這個資料夾，請確認 mcpelauncher 已安裝並重新掃描。')
        if platform.system() != 'Darwin':
            raise UserError('開啟 Finder 資料夾只適用於 macOS。')
        subprocess.Popen(['/usr/bin/open', str(path)], stdin=subprocess.DEVNULL,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return '已在 Finder 開啟：' + str(path)

    def launch_upstream(self):
        if platform.system() != 'Darwin':
            raise UserError('開啟 macOS Bedrock Launcher 只適用於 macOS。')
        app = self._launcher_app()
        if not app:
            raise UserError('找不到 Minecraft Bedrock Launcher.app。請先安裝上游啟動器，或確認它位於 /Applications 或 ~/Applications。')
        subprocess.Popen(['/usr/bin/open', app], stdin=subprocess.DEVNULL,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return '已交由 Minecraft Bedrock Launcher 開啟。遊戲版本仍由上游啟動器管理。'

    @staticmethod
    def _bedrock_process_running():
        try:
            result = subprocess.run(['/bin/ps', '-axo', 'pid=,command='], capture_output=True,
                                    text=True, timeout=4, check=False)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise UserError('無法確認 Bedrock 是否正在執行，因此取消備份以保護存檔。') from exc
        if result.returncode != 0:
            raise UserError('無法確認 Bedrock 是否正在執行，因此取消備份以保護存檔。')
        for line in result.stdout.splitlines():
            command = line.split(None, 1)[1] if len(line.split(None, 1)) == 2 else ''
            if 'mcpelauncher-client' in command:
                return True
        return False

    def backup_world(self, world_id):
        if self._bedrock_process_running():
            raise UserError('請先完全退出 Minecraft Bedrock，再備份世界。')
        state = self.state()
        matches = {item['id']: item for item in state['worlds']}
        if not isinstance(world_id, str) or world_id not in matches:
            raise UserError('找不到這個世界，請重新掃描。')
        world = Path(matches[world_id]['path'])
        root, _ = self._configured_path()
        if not _safe_under(root, world):
            raise UserError('世界資料夾已移動或無法安全讀取。')
        backup_dir = self.launcher_data_root / 'bedrock-backups'
        if backup_dir.is_symlink():
            raise UserError('備份位置是符號連結，已停止以保護資料。')
        backup_dir.mkdir(parents=True, exist_ok=True)
        if backup_dir.is_symlink():
            raise UserError('備份位置是符號連結，已停止以保護資料。')
        safe_name = re.sub(r'[^A-Za-z0-9._-]+', '-', world_id).strip('.-')[:80] or 'world'
        stamp = time.strftime('%Y%m%d-%H%M%S')
        dest = backup_dir / f'{safe_name}-{stamp}-{uuid.uuid4().hex[:6]}.mcworld'
        temp = dest.with_suffix('.mcworld.part')
        written = 0
        try:
            with zipfile.ZipFile(temp, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
                for current, dirs, files in os.walk(world, followlinks=False, onerror=_raise_walk_error):
                    current_path = Path(current)
                    dirs[:] = sorted(d for d in dirs if not (current_path / d).is_symlink())
                    for name in sorted(files):
                        source = current_path / name
                        if source.is_symlink() or not source.is_file():
                            continue
                        if not source.resolve(strict=True).is_relative_to(world.resolve(strict=True)):
                            raise UserError('世界內含無法安全讀取的路徑，已取消備份。')
                        written += source.stat().st_size
                        archive.write(source, source.relative_to(world).as_posix())
            if written == 0:
                raise UserError('這個世界沒有可備份的檔案。')
            with zipfile.ZipFile(temp, 'r') as archive:
                bad = archive.testzip()
                if bad is not None:
                    raise UserError('備份檔完整性檢查失敗，未保留不完整檔案。')
                if not any(Path(item).name == 'level.dat' for item in archive.namelist()):
                    raise UserError('世界缺少 level.dat，未建立不完整備份。')
            os.replace(temp, dest)
        except Exception:
            temp.unlink(missing_ok=True)
            raise
        return '世界備份已建立：' + str(dest)
