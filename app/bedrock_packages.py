"""Acquire user-supplied Android packages without an embedded store account.

No game mirrors, account credentials, or license patches are bundled.
Archive structure and hashes do not establish publisher authenticity.
"""
import hashlib
import ipaddress
from pathlib import Path, PurePosixPath
import re
import stat
import time
from urllib.parse import urljoin, urlsplit
import zipfile

import requests
from core import UserError, Cancelled

MAX_PACKAGE = 3 * 1024**3
MAX_EXPANDED_APKS = 6 * 1024**3
PACKAGE_SUFFIXES = {'.apk', '.xapk', '.apks', '.apkm', '.zip'}


def validate_url(value):
    if not isinstance(value, str) or len(value) > 4096 or any(c.isspace() or ord(c) < 32 for c in value):
        raise UserError('請輸入有效的 HTTPS 安裝包直連。')
    try:
        url = urlsplit(value)
        if (url.scheme != 'https' or not url.hostname or url.username or url.password
                or url.fragment or url.port not in (None, 443) or '\\' in value):
            raise ValueError()
        host = url.hostname.lower().rstrip('.')
        if host == 'localhost' or host.endswith(('.localhost', '.local')):
            raise ValueError()
        try:
            address = ipaddress.ip_address(host)
        except ValueError:
            address = None
        if address and not address.is_global:
            raise ValueError()
    except ValueError:
        raise UserError('只接受公開 HTTPS 直連，不接受帳號密碼、片段或本機位址。') from None
    return value


def download_package(url, target, expected, cancel, progress, limit=MAX_PACKAGE):
    url = validate_url(url)
    if not isinstance(expected, str) or (expected and not re.fullmatch('[a-fA-F0-9]{64}', expected)):
        raise UserError('SHA-256 必須是 64 位十六進制字串，或留空。')
    target = Path(target)
    digest = hashlib.sha256(); done = 0
    deadline = time.monotonic() + 1800
    try:
        for _ in range(6):
            if cancel.is_set(): raise Cancelled('已取消下載。')
            with requests.get(url, stream=True, timeout=(10, 30), allow_redirects=False,
                              headers={'Accept-Encoding': 'identity'}) as response:
                if response.status_code in (301, 302, 303, 307, 308):
                    location = response.headers.get('Location')
                    if not location: raise UserError('下載來源的轉址不完整。')
                    url = validate_url(urljoin(url, location))
                    continue
                if response.status_code != 200:
                    raise UserError('下載來源未提供安裝包（HTTP ' + str(response.status_code) + '）。')
                raw_size = response.headers.get('Content-Length', '')
                size = int(raw_size) if raw_size.isdigit() else 0
                if size > limit: raise UserError('安裝包超過 3 GB 限制。')
                progress('正在下載自訂來源安裝包…', 0, size)
                with target.open('xb') as output:
                    for chunk in response.iter_content(1024 * 1024):
                        if cancel.is_set(): raise Cancelled('已取消下載。')
                        if time.monotonic() > deadline: raise UserError('安裝包下載逾時，請重試。')
                        done += len(chunk)
                        if done > limit or size and done > size:
                            raise UserError('安裝包大小超過限制或與來源不符。')
                        digest.update(chunk); output.write(chunk); progress(done=done)
                if not done or size and done != size:
                    raise UserError('安裝包下載不完整。')
                actual = digest.hexdigest()
                if expected and actual != expected.lower():
                    raise UserError('安裝包 SHA-256 不符，未安裝。')
                return actual
        raise UserError('下載來源轉址過多。')
    except requests.RequestException:
        # Avoid leaking signed URLs into the job log, including chained tracebacks.
        raise UserError('安裝包下載失敗或逾時；請確認直連可以下載檔案後重試。') from None
    finally:
        if cancel.is_set(): target.unlink(missing_ok=True)


def package_apks(paths, temp, cancel):
    """Accept one APK/container, or an explicit base + split APK selection.

    Container members are copied to generated names, never archive paths.
    OBB containers and nested containers are rejected rather than half-installed.
    """
    if not isinstance(paths, list) or not 1 <= len(paths) <= 64:
        raise UserError('請選擇一個安裝包，或最多 64 個 base／split APK。')
    result = []; total = 0
    for value in paths:
        if cancel.is_set(): raise Cancelled('已取消匯入。')
        if not isinstance(value, (str, Path)) or len(str(value)) > 4096:
            raise UserError('安裝包路徑不合法。')
        path = Path(value).expanduser()
        if path.is_symlink() or not path.is_file() or not 0 < path.stat().st_size <= MAX_PACKAGE:
            raise UserError('找不到安裝包，或檔案超過 3 GB。')
        try:
            with zipfile.ZipFile(path) as archive:
                names = archive.namelist()
                if len(names) > 200000: raise UserError('安裝包檔案數量過多。')
                if 'AndroidManifest.xml' in names:
                    if len(paths) > 1 and path.suffix.lower() != '.apk':
                        raise UserError('多選時請只選 base／split APK。')
                    result.append(path)
                    total += path.stat().st_size
                else:
                    if len(paths) != 1: raise UserError('XAPK／APKS／APKM／ZIP 請一次選一個。')
                    seen = set()
                    for info in archive.infolist():
                        name = info.filename; parts = PurePosixPath(name).parts
                        if (not parts or name.startswith('/') or '\\' in name or '..' in parts
                                or stat.S_ISLNK(info.external_attr >> 16) or name in seen):
                            raise UserError('安裝包含不安全或重複的路徑。')
                        seen.add(name)
                        if name.lower().endswith('.obb'):
                            raise UserError('此安裝包依賴 OBB，這個版本暫不支援。請使用完整 APK 或 base／split APK。')
                        if info.is_dir() or not name.lower().endswith('.apk'): continue
                        if len(result) >= 64: raise UserError('安裝包包含過多 APK。')
                        total += info.file_size
                        if total > MAX_EXPANDED_APKS: raise UserError('安裝包解壓後超過 6 GB。')
                        output = Path(temp) / ('part-' + str(len(result)) + '.apk')
                        with archive.open(info) as source, output.open('xb') as destination:
                            while chunk := source.read(1024 * 1024):
                                if cancel.is_set(): raise Cancelled('已取消匯入。')
                                destination.write(chunk)
                        result.append(output)
                if total > MAX_EXPANDED_APKS: raise UserError('安裝包總大小超過 6 GB。')
        except (zipfile.BadZipFile, NotImplementedError, RuntimeError, KeyError):
            raise UserError('無法讀取安裝包；請提供完整、未加密的 APK／XAPK／APKS／APKM／ZIP。') from None
    if not result: raise UserError('檔案中沒有 Android APK。請使用安裝包直連，不能使用網頁連結。')
    return result
