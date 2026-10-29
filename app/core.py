"""MambaCraft local launcher. Modern Vanilla + Fabric. No shell commands from UI.
SPDX-License-Identifier: MIT
"""
from __future__ import annotations
import concurrent.futures as futures
import hashlib
import json
import os
import posixpath
from pathlib import Path, PurePosixPath
import platform
import re
import shutil
import stat
import struct
import subprocess
import threading
import time
import tempfile
import tarfile
import traceback
import uuid
import zipfile
import requests
from ownership import claim_new_tree, remember_download

APP_VERSION = '1.3-rc22'
MANIFEST_URL = 'https://piston-meta.mojang.com/mc/game/version_manifest_v2.json'
RUNTIME_URL = 'https://launchermeta.mojang.com/v1/products/java-runtime/2ec0cc96c44e5a76b9c8b7c39df7210883d12871/all.json'
FMM_HOSTS = {'launchermeta.fastmcmirror.org','launcher.fastmcmirror.org','resources.fastmcmirror.org',
             'libraries.fastmcmirror.org','fabric.fastmcmirror.org','fabricmeta.fastmcmirror.org'}
OFFICIAL_HOSTS = {'piston-meta.mojang.com','piston-data.mojang.com','launchermeta.mojang.com',
                  'launcher.mojang.com','libraries.minecraft.net','resources.download.minecraft.net',
                  'meta.fabricmc.net','maven.fabricmc.net'}
MIRROR_HOSTS = {'bmclapi2.bangbang93.com','bmclapi.bangbang93.com'}|FMM_HOSTS
COMPAT_HOSTS = {'cdn.azul.com','corretto.aws','github.com','release-assets.githubusercontent.com','objects.githubusercontent.com','authlib-injector.yushi.moe','bmclapi2.bangbang93.com',
                'gh-proxy.com','ghproxy.net','ghfast.top'}
MOD_API_HOSTS = {'api.modrinth.com','mod.mcimirror.top'}
MOD_FILE_HOSTS = {'cdn.modrinth.com','mod.mcimirror.top'}
MODRINTH_API = 'https://api.modrinth.com/v2'
MCIM_API = 'https://mod.mcimirror.top/modrinth/v2'
MCIM_FILES = 'https://mod.mcimirror.top'
ARM64_LEGACY_JAVA_URL = 'https://cdn.azul.com/zulu/bin/zulu8.96.0.205-ca-jre8.0.504-macosx_aarch64.zip'
ARM64_LEGACY_JAVA_SHA256 = '1769ea082fa13ba29403363425716451b04b10f5ae6dba07f7f0a69666197f15'
ARM64_LEGACY_JAVA_SIZE = 40334100
ARM64_LEGACY_CORRETTO_URL = 'https://github.com/corretto/corretto-8/releases/download/8.504.04.1/amazon-corretto-8.504.04.1-macosx-aarch64.tar.gz'
ARM64_LEGACY_CORRETTO_SHA256 = 'b779a70a47b910ca4c10c5d98d6ae11e2f82d9720423704eaf5eacf87f1ca436'
ARM64_LEGACY_CORRETTO_URLS = (
    'https://corretto.aws/downloads/resources/8.504.04.1/amazon-corretto-8.504.04.1-macosx-aarch64.tar.gz',
    ARM64_LEGACY_CORRETTO_URL,
)
ARM64_LWJGL_VERSION = '2.9.4-nightly-20150209'
ARM64_LWJGL_JAR = {
    'path':'org/lwjgl/lwjgl/lwjgl/2.9.4-nightly-20150209/lwjgl-2.9.4-nightly-20150209.jar',
    'url':'https://libraries.minecraft.net/org/lwjgl/lwjgl/lwjgl/2.9.4-nightly-20150209/lwjgl-2.9.4-nightly-20150209.jar',
    'sha1':'697517568c68e78ae0b4544145af031c81082dfe','size':1047168}
ARM64_LWJGL_UTIL_JAR = {
    'path':'org/lwjgl/lwjgl/lwjgl_util/2.9.4-nightly-20150209/lwjgl_util-2.9.4-nightly-20150209.jar',
    'url':'https://libraries.minecraft.net/org/lwjgl/lwjgl/lwjgl_util/2.9.4-nightly-20150209/lwjgl_util-2.9.4-nightly-20150209.jar',
    'sha1':'d51a7c040a721d13efdfbd34f8b257b2df882ad0','size':173887}
ARM64_LWJGL_NATIVE = {
    'path':'org/lwjgl/lwjgl/lwjgl-platform/2.9.4-nightly-20150209-mmachina.2/lwjgl-platform-2.9.4-nightly-20150209-mmachina.2-natives-osx.jar',
    'url':'https://github.com/MinecraftMachina/lwjgl/releases/download/2.9.4-20150209-mmachina.2/lwjgl-platform-2.9.4-nightly-20150209-natives-osx.jar',
    'sha1':'eff546c0b319d6ffc7a835652124c18089c67f36','sha256':'a14379458c749872a1e183e88edceaab87c762328fb031481d98d0aaed5e6311','size':488316}
ARM64_LWJGL_NATIVE_MIRRORS = (
    'https://gh-proxy.com/https://github.com/MinecraftMachina/lwjgl/releases/download/2.9.4-20150209-mmachina.2/lwjgl-platform-2.9.4-nightly-20150209-natives-osx.jar',
    'https://ghproxy.net/https://github.com/MinecraftMachina/lwjgl/releases/download/2.9.4-20150209-mmachina.2/lwjgl-platform-2.9.4-nightly-20150209-natives-osx.jar',
    'https://ghfast.top/https://github.com/MinecraftMachina/lwjgl/releases/download/2.9.4-20150209-mmachina.2/lwjgl-platform-2.9.4-nightly-20150209-natives-osx.jar',
)
ARM64_JNA_JAR = {
    'path':'assets/jna-5.7.0.jar',
    'sha256':'c34e3e002cca6e197379c105b554255cc0638101ed7a09ef00334dade0013621',
    'size':1686295,
    'native_path':'com/sun/jna/darwin/libjnidispatch.jnilib',
}
ARM64_OBJC_BRIDGE_JAR = {
    'path':'assets/java-objc-bridge-1.1.0-mmachina.1.jar',
    'sha1':'369a83621e3c65496348491e533cb97fe5f2f37d',
    'sha256':'06ea2091fee1b8a6ca947376aa0b60c486feb9f1558441938edb245b20e58ede',
    'size':91947,
    'native_path':'libjcocoa.dylib',
    'required_class':'ca/weblite/objc/RuntimeUtils.class',
}
ID_RE = re.compile(r'[A-Za-z0-9][A-Za-z0-9._+ _-]{0,119}\Z')
NAME_RE = re.compile(r'[A-Za-z0-9_]{3,16}\Z')
VERSION_TYPES = ('release','snapshot','old_beta','old_alpha')
MIN_VERSION_COUNTS = {'release':50,'snapshot':100,'old_beta':20,'old_alpha':20}

class UserError(Exception): pass
class Cancelled(UserError): pass

def ident(value):
    if not isinstance(value, str) or not ID_RE.fullmatch(value) or '..' in value or value.endswith((' ', '.')):
        raise UserError('無效的版本／實例名稱。')
    return value

def username(value):
    if not isinstance(value, str) or not NAME_RE.fullmatch(value):
        raise UserError('玩家名稱需為 3–16 個英文字母、數字或底線。')
    return value

def offline_uuid(name):
    return str(uuid.UUID(bytes=hashlib.md5(('OfflinePlayer:' + username(name)).encode()).digest(), version=3))

def inside(root, relative):
    root = Path(root).resolve()
    if not isinstance(relative, str) or '\\' in relative or '\x00' in relative:
        raise UserError('檔案路徑不合法。')
    p = PurePosixPath(relative)
    if p.is_absolute() or '..' in p.parts:
        raise UserError('拒絕越界的檔案路徑。')
    target = (root / relative).resolve()
    if not target.is_relative_to(root):
        raise UserError('拒絕越界的檔案路徑。')
    return target

def atomic_json(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    try:
        with temp.open('w', encoding='utf-8') as out:
            json.dump(value, out, ensure_ascii=False, indent=2)
            out.flush(); os.fsync(out.fileno())
        os.chmod(temp, 0o600); os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)

def read_json(path):
    with Path(path).open(encoding='utf-8') as f: return json.load(f)

def sha1(path):
    h = hashlib.sha1()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1024 * 1024), b''): h.update(chunk)
    return h.hexdigest()

def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1024 * 1024), b''): h.update(chunk)
    return h.hexdigest()

def sha512(path):
    h = hashlib.sha512()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1024 * 1024), b''): h.update(chunk)
    return h.hexdigest()

def modrinth_file_mirror(url):
    """Return the documented MCIM CDN equivalent for an official Modrinth file."""
    from urllib.parse import urlparse, urlunparse
    parsed=urlparse(url)
    if parsed.scheme!='https' or parsed.hostname!='cdn.modrinth.com' or parsed.username or parsed.password:
        return None
    return urlunparse(('https','mod.mcimirror.top',parsed.path,parsed.params,parsed.query,''))

def safe_archive_path(value):
    if not isinstance(value,str) or not value or '\\' in value or '\x00' in value:
        raise UserError('整合包內含不安全的檔案路徑。')
    path=PurePosixPath(value)
    if path.is_absolute() or any(part in ('','.','..') for part in path.parts):
        raise UserError('整合包內含不安全的檔案路徑。')
    return path.as_posix()

def safe_download_name(value, fallback='download.bin'):
    if not isinstance(value,str): value=fallback
    name=Path(value.replace('\\','/')).name
    name=re.sub(r'[^A-Za-z0-9._ ()+\[\]-]+','_',name).strip(' .')
    if not name or name in ('.','..'):name=fallback
    return name[:180]

def supported(v):
    # Official version IDs include classic releases, weekly snapshots and April-Fools IDs.
    return isinstance(v, str) and bool(ID_RE.fullmatch(v)) and '..' not in v and not v.endswith((' ', '.'))

def java_major_for(data, version):
    info=data.get('javaVersion')
    if isinstance(info,dict) and isinstance(info.get('majorVersion'),int): return info['majorVersion']
    m=re.match(r'^1\.(\d+)',version)
    if not m: return 8
    minor=int(m.group(1))
    if minor>=18:return 17
    if minor==17:return 16
    return 8

def java_compatible(required,actual):
    # Mojang metadata pins a tested Java major. A newer JVM can break old game/mod loaders.
    return type(required) is int and type(actual) is int and actual==required

def host_os(): return {'Darwin':'osx', 'Linux':'linux', 'Windows':'windows'}.get(platform.system(), 'unknown')
def host_arch(): return {'arm64':'aarch64', 'AMD64':'x86_64', 'amd64':'x86_64'}.get(platform.machine(), platform.machine())

def has_lwjgl2(data):
    return isinstance(data,dict) and any(
        isinstance(lib,dict) and isinstance(lib.get('name'),str) and
        lib['name'].split(':',2)[:2]==['org.lwjgl.lwjgl','lwjgl']
        for lib in data.get('libraries',[]))

def active_lwjgl2_versions(data):
    versions=set()
    if not isinstance(data,dict):return versions
    for lib in data.get('libraries',[]):
        if not isinstance(lib,dict) or not isinstance(lib.get('name'),str) or not allowed(lib.get('rules')):continue
        parts=lib['name'].split(':')
        if len(parts)>=3 and parts[:2]==['org.lwjgl.lwjgl','lwjgl']:versions.add(parts[2])
    return versions

def use_arm64_legacy_lwjgl2(data):
    # Apple Silicon cannot load Mojang's x86 LWJGL 2 natives. Swap the runtime
    # and both LWJGL Java jars together, without rewriting version metadata.
    if not isinstance(data,dict):return False
    version=data.get('id') or data.get('inheritsFrom') or '1.12.1'
    versions=active_lwjgl2_versions(data)
    supported=bool(versions) and all(v.startswith(('2.9.2','2.9.4')) for v in versions)
    return (host_os()=='osx' and host_arch()=='aarch64' and supported
            and java_major_for(data,version)==8)

def needs_intel_java8(required,data=None):
    # Historical macOS LWJGL binaries are Intel-only. On Apple Silicon they must run
    # inside an Intel JVM translated by Rosetta, rather than an ARM Java 8 runtime.
    return required==8 and host_os()=='osx' and host_arch()=='aarch64' and not use_arm64_legacy_lwjgl2(data)

def rosetta_installed():
    # Do not probe by executing an Intel binary: macOS can pop up a Rosetta install
    # prompt. This filesystem check is passive and leaves installation to the user.
    return Path('/Library/Apple/usr/libexec/oah').is_dir()

def java_arch_compatible(required,actual,data=None):
    if use_arm64_legacy_lwjgl2(data):
        return actual=='aarch64'
    if needs_intel_java8(required,data):
        return actual=='x86_64' and rosetta_installed()
    return actual==host_arch()

def rosetta_message():
    return ('Apple Silicon 上的舊版 Minecraft 需要 Intel Java 8 與 Rosetta 2。'
            '請先在 Terminal 執行 `softwareupdate --install-rosetta`，完成後再重試。')

RUNTIME_COMPONENT_BY_MAJOR = {8:'jre-legacy',16:'java-runtime-alpha',17:'java-runtime-gamma',
                              21:'java-runtime-delta',25:'java-runtime-epsilon'}

def allowed(rules, features=None, os_name=None, arch=None):
    if not rules: return True
    result = False
    features = features or {}; os_name = os_name or host_os(); arch = arch or host_arch()
    for rule in rules:
        spec = rule.get('os', {})
        if spec.get('name', os_name) != os_name: continue
        if 'arch' in spec and not re.fullmatch(spec['arch'], arch): continue
        if 'version' in spec and not re.search(spec['version'], platform.release()): continue
        if any(features.get(k, False) != v for k, v in rule.get('features', {}).items()): continue
        result = rule['action'] == 'allow'
    return result

def modrinth_icon_url(value):
    """Accept only Modrinth's fixed HTTPS project-icon path; never pass API URLs through blindly."""
    from urllib.parse import urlsplit
    if not isinstance(value,str) or len(value)>2048:return ''
    try:parsed=urlsplit(value)
    except ValueError:return ''
    if parsed.scheme!='https' or parsed.netloc!='cdn.modrinth.com' or parsed.query or parsed.fragment:return ''
    path=parsed.path
    if not re.fullmatch(r'/data/[A-Za-z0-9._/-]{1,1800}',path):return ''
    if any(part in ('','.','..') for part in path.split('/')[1:]):return ''
    return 'https://cdn.modrinth.com'+path

class Network:
    def __init__(self, cancel=None, on_source=None):
        self.cancel = cancel or threading.Event(); self.local = threading.local(); self.on_source=on_source
    def fallback_message(self,url):
        from urllib.parse import urlparse
        host=urlparse(url).hostname or ''
        if host.endswith('bangbang93.com'):name='BMCLAPI'
        elif host.endswith('fastmcmirror.org'):name='FastMinecraftMirror'
        elif host=='mod.mcimirror.top':name='MCIM Modrinth 備援鏡像'
        elif host in ('gh-proxy.com','ghproxy.net','ghfast.top'):name='GitHub 備援下載來源'
        else:name='Mojang 備援主機'
        if self.on_source:self.on_source(f'主要下載來源無回應或速度過慢，正在切換至 {name}…')
    def check(self):
        if self.cancel.is_set(): raise Cancelled('已取消。已下載且通過校驗的檔案會保留，重試可繼續使用。')
    def response(self, url, extra_hosts=(), **kwargs):
        from urllib.parse import urlparse
        p = urlparse(url)
        # URLs originate in official metadata; allow only its known hosts and the pinned mirror.
        extra_hosts=set(extra_hosts or ())
        if not extra_hosts<=(COMPAT_HOSTS|MOD_FILE_HOSTS):raise UserError('下載來源不在啟動器固定的相容性來源清單內。')
        allowed_hosts=OFFICIAL_HOSTS|MIRROR_HOSTS|MOD_API_HOSTS|MOD_FILE_HOSTS|extra_hosts
        if p.scheme != 'https' or p.username or p.password or p.hostname not in allowed_hosts:
            raise UserError('下載來源不在允許的 HTTPS 網域內。')
        self.check()
        if not hasattr(self.local, 'session'): self.local.session = requests.Session()
        r = self.local.session.get(url, timeout=(10, 20), headers={'User-Agent':'MambaCraft/'+APP_VERSION}, **kwargs)
        r.raise_for_status()
        final = urlparse(r.url)
        if final.scheme != 'https' or final.hostname not in allowed_hosts:
            r.close(); raise UserError('拒絕不安全的下載轉址。')
        return r
    def mirror_urls(self, url):
        from urllib.parse import urlparse, urlunparse
        p=urlparse(url)
        if p.scheme!='https' or p.hostname not in OFFICIAL_HOSTS:return []
        if p.hostname=='libraries.minecraft.net' or p.hostname=='maven.fabricmc.net': prefix='/maven'
        elif p.hostname=='resources.download.minecraft.net': prefix='/assets'
        elif p.hostname=='meta.fabricmc.net': prefix='/fabric-meta'
        else: prefix=''
        out=[urlunparse(('https','bmclapi2.bangbang93.com',prefix+p.path,p.params,p.query,''))]
        # FastMinecraftMirror documents these host rewrites; unsupported host/path pairs
        # deliberately stay on BMCLAPI + the official origin only.
        fast_hosts={'launchermeta.mojang.com':'launchermeta.fastmcmirror.org',
                    'launcher.mojang.com':'launcher.fastmcmirror.org',
                    'resources.download.minecraft.net':'resources.fastmcmirror.org',
                    'maven.fabricmc.net':'fabric.fastmcmirror.org',
                    'meta.fabricmc.net':'fabricmeta.fastmcmirror.org'}
        if p.hostname in fast_hosts:
            out.append(urlunparse(('https',fast_hosts[p.hostname],p.path,p.params,p.query,'')))
        return out
    def official_aliases(self, url):
        from urllib.parse import urlparse, urlunparse
        p=urlparse(url)
        aliases={'piston-meta.mojang.com':'launchermeta.mojang.com',
                 'launchermeta.mojang.com':'piston-meta.mojang.com',
                 'piston-data.mojang.com':'launcher.mojang.com',
                 'launcher.mojang.com':'piston-data.mojang.com'}
        host=aliases.get(p.hostname)
        return [urlunparse(('https',host,p.path,p.params,p.query,''))] if host else []
    def json(self, url):
        last_error=None
        for index,candidate in enumerate([url,*self.official_aliases(url)]):
            try:
                if index:self.fallback_message(candidate)
                with self.response(candidate) as r: return r.json()
            except (requests.RequestException,ValueError) as exc:last_error=exc
        if last_error:raise last_error
        raise UserError('無法讀取官方資料。')
    def download(self, url, path, digest=None, size=None, sha256_digest=None, sha512_digest=None, extra_hosts=(), max_bytes=None, retries=3, fallback_urls=()):
        path = Path(path); self.check()
        extra_hosts=set(extra_hosts or ())
        if not extra_hosts<=(COMPAT_HOSTS|MOD_FILE_HOSTS):raise UserError('下載來源不在啟動器固定的相容性來源清單內。')
        if type(retries) is not int or not 1<=retries<=5:raise UserError('下載重試設定不合法。')
        from urllib.parse import urlparse
        fallback_urls=tuple(fallback_urls or ())
        if any(urlparse(candidate).scheme!='https' or urlparse(candidate).hostname not in extra_hosts for candidate in fallback_urls):
            raise UserError('下載備援來源不在啟動器固定的 HTTPS 網域清單內。')
        if path.is_file() and (size is None or path.stat().st_size == size):
            sha1_ok=not digest or sha1(path)==digest
            sha256_ok=not sha256_digest or sha256(path)==sha256_digest
            sha512_ok=not sha512_digest or sha512(path)==sha512_digest
            if sha1_ok and sha256_ok and sha512_ok and (digest or sha256_digest or sha512_digest):return False
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_name(path.name + '.' + uuid.uuid4().hex + '.part')
        # A mirror is used only when the official metadata pins a SHA-1. The final
        # official retry handles a transient mirror miss without weakening validation.
        aliases=self.official_aliases(url)
        mirrors=[]
        if isinstance(digest,str) and re.fullmatch(r'[0-9a-fA-F]{40}',digest):
            # Some current Mojang metadata uses piston-data/piston-meta. Resolve
            # mirror mappings against their documented launcher/launchermeta aliases too.
            for source in (url,*aliases):
                for mirror in self.mirror_urls(source):
                    if mirror!=url and mirror not in mirrors: mirrors.append(mirror)
        candidates=[url,*aliases,*mirrors,*fallback_urls]
        if fallback_urls:candidates.extend([url]*(min(1,retries-1)))
        else:candidates.extend([url]*(min(1,retries-1) if mirrors else retries-1))
        last_error=None
        try:
            for index,candidate in enumerate(candidates):
                self.check()
                try:
                    if index and candidate!=candidates[index-1]:self.fallback_message(candidate)
                    h = hashlib.sha1(); h256=hashlib.sha256(); h512=hashlib.sha512(); count = 0; window_bytes=0
                    with self.response(candidate, stream=True,extra_hosts=extra_hosts) as r, temp.open('wb') as out:
                        window_start=time.monotonic()
                        for chunk in r.iter_content(256 * 1024):
                            self.check()
                            if chunk:
                                next_count=count+len(chunk)
                                if size is not None and next_count>size:
                                    raise UserError(f'下載檔案大小超出預期（預期 {size:,} bytes，收到至少 {next_count:,} bytes）。')
                                if max_bytes is not None and next_count>max_bytes:
                                    raise UserError(f'下載檔案超出安全大小上限（{max_bytes:,} bytes）。')
                                out.write(chunk); h.update(chunk); h256.update(chunk); h512.update(chunk); count += len(chunk); window_bytes+=len(chunk)
                                now=time.monotonic()
                                # Switch sources when a large file is persistently below 32 KiB/s.
                                if size is not None and size>=1024*1024 and now-window_start>=15:
                                    if window_bytes/max(now-window_start,0.001)<32*1024:
                                        raise requests.Timeout('下載速度過慢，正在切換來源。')
                                    window_bytes=0; window_start=now
                        out.flush(); os.fsync(out.fileno())
                    if size is not None and count != size: raise UserError(f'下載檔案大小不符（預期 {size:,} bytes，實際 {count:,} bytes）。')
                    if digest and h.hexdigest() != digest: raise UserError('下載校驗失敗，原有檔案未被覆蓋。')
                    if sha256_digest and h256.hexdigest() != sha256_digest: raise UserError('下載 SHA-256 校驗失敗，原有檔案未被覆蓋。')
                    if sha512_digest and h512.hexdigest() != sha512_digest: raise UserError('下載 SHA-512 校驗失敗，原有檔案未被覆蓋。')
                    os.replace(temp, path); return True
                except (requests.RequestException, UserError) as exc:
                    if isinstance(exc, Cancelled): raise
                    last_error=exc; temp.unlink(missing_ok=True)
            if last_error: raise last_error
        finally: temp.unlink(missing_ok=True)

def maven_path(name):
    parts = name.split(':')
    if len(parts) not in (3, 4): raise UserError('不支援的函式庫名稱。')
    group, artifact, version = parts[:3]
    suffix = '-' + parts[3] if len(parts) == 4 else ''
    return group.replace('.', '/') + f'/{artifact}/{version}/{artifact}-{version}{suffix}.jar'

def library_plan(data, game):
    entries = []; classpath = []; natives = []
    use_arm64_bridge=use_arm64_legacy_lwjgl2(data)
    bridge_path=Path(__file__).resolve().parent/ARM64_OBJC_BRIDGE_JAR['path']
    bridge_added=False
    for lib in data['libraries']:
        if not allowed(lib.get('rules')): continue
        parts=lib.get('name','').split(':') if isinstance(lib.get('name'),str) else []
        # The Mojang 1.0.0 bridge embeds an x86_64-only libjcocoa.dylib.
        # On Apple Silicon use a pinned, universal bridge from the launcher package
        # and do not download/extract the incompatible macOS native classifier.
        if use_arm64_bridge and parts[:3]==['ca.weblite','java-objc-bridge','1.0.0']:
            if not bridge_added:
                classpath.append(bridge_path); bridge_added=True
            continue
        downloads = lib.get('downloads', {})
        artifact = downloads.get('artifact')
        if artifact is None and not downloads:
            path = maven_path(lib['name'])
            artifact = {'path':path, 'url':lib.get('url', 'https://libraries.minecraft.net/').rstrip('/')+'/'+path}
        if artifact and artifact.get('url'):
            path = inside(game / 'libraries', artifact.get('path') or maven_path(lib['name']))
            entries.append((artifact, path)); classpath.append(path)
        classifier = lib.get('natives', {}).get(host_os())
        if classifier:
            classifier = classifier.replace('${arch}', '64')
            item = downloads['classifiers'][classifier]
            path = inside(game / 'libraries', item['path'])
            entries.append((item, path)); natives.append((path, lib.get('extract', {}).get('exclude', ['META-INF/'])))
    return entries, classpath, natives

def extract_native(archive, target, exclude):
    target.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as z:
        for item in z.infolist():
            if item.is_dir() or any(item.filename.startswith(x) for x in exclude): continue
            path = inside(target, item.filename)
            if stat.S_ISLNK(item.external_attr >> 16): raise UserError('拒絕原生函式庫中的符號連結。')
            path.parent.mkdir(parents=True, exist_ok=True)
            with z.open(item) as src, path.open('wb') as dst: shutil.copyfileobj(src, dst)

def extract_zip_safely(archive,target,max_files=250000,max_unpacked=512*1024*1024):
    """Extract a pinned runtime archive without links, traversal or zip bombs."""
    target=Path(target);target.mkdir(parents=True,exist_ok=True)
    try:
        with zipfile.ZipFile(archive) as z:
            items=z.infolist()
            if len(items)>max_files or sum(item.file_size for item in items)>max_unpacked:
                raise UserError('Java 安裝檔超出安全解壓限制。')
            for item in items:
                mode=item.external_attr>>16
                if stat.S_ISLNK(mode):raise UserError('拒絕 Java 安裝檔中的符號連結。')
                path=inside(target,item.filename.rstrip('/') if item.is_dir() else item.filename)
                if item.is_dir():path.mkdir(parents=True,exist_ok=True);continue
                path.parent.mkdir(parents=True,exist_ok=True)
                written=0
                with z.open(item) as src,path.open('wb') as dst:
                    for chunk in iter(lambda:src.read(1024*1024),b''):
                        written+=len(chunk)
                        if written>item.file_size or written>max_unpacked:
                            raise UserError('Java 安裝檔內容大小與 ZIP 索引不符。')
                        dst.write(chunk)
                    if written!=item.file_size:raise UserError('Java 安裝檔內容不完整。')
                if mode&0o111:path.chmod(0o644|(mode&0o111))
    except (zipfile.BadZipFile,OSError,RuntimeError) as exc:
        if isinstance(exc,UserError):raise
        raise UserError('Java 安裝檔無法安全解壓，請按「檢查及修復」重試。') from exc

def extract_tar_gz_safely(archive,target,max_files=100000,max_unpacked=1536*1024*1024):
    """Extract a pinned JDK tarball, permitting only contained files and links."""
    target=Path(target);target.mkdir(parents=True,exist_ok=True);root=target.resolve()
    try:
        with tarfile.open(archive,'r:gz') as tf:
            members=tf.getmembers()
            if len(members)>max_files or sum(max(0,m.size) for m in members if m.isfile())>max_unpacked:
                raise UserError('Java 安裝檔超出安全解壓限制。')
            entries={}
            for m in members:
                raw=m.name.rstrip('/')
                if raw in ('','.'): 
                    if m.isdir():continue
                    raise UserError('Java 安裝檔包含不合法的根路徑。')
                p=PurePosixPath(raw)
                if p.is_absolute() or '\\' in raw or '\x00' in raw or '..' in p.parts:
                    raise UserError('Java 安裝檔包含越界路徑。')
                rel=PurePosixPath(*(part for part in p.parts if part not in ('','.'))).as_posix()
                if not rel or rel=='.':continue
                if not (m.isfile() or m.isdir() or m.issym() or m.islnk()):
                    raise UserError('Java 安裝檔包含不支援的特殊檔案。')
                if rel in entries:
                    if entries[rel].isdir() and m.isdir():continue
                    raise UserError('Java 安裝檔包含重複路徑。')
                entries[rel]=m
            symlinks={name for name,m in entries.items() if m.issym()}
            for name,m in entries.items():
                parent=PurePosixPath(name).parent
                while str(parent) not in ('','.'): 
                    if parent.as_posix() in symlinks:raise UserError('Java 安裝檔在符號連結下包含檔案。')
                    parent=parent.parent
                if m.issym():
                    if not m.linkname or m.linkname.startswith('/') or '\\' in m.linkname:
                        raise UserError('Java 安裝檔包含不安全的符號連結。')
                    link=posixpath.normpath(posixpath.join(posixpath.dirname(name),m.linkname))
                    if link=='..' or link.startswith('../') or link.startswith('/'):
                        raise UserError('Java 安裝檔符號連結超出解壓範圍。')
                elif m.islnk():
                    link=PurePosixPath(m.linkname)
                    if link.is_absolute() or '\\' in m.linkname or '..' in link.parts:
                        raise UserError('Java 安裝檔包含不安全的硬連結。')
                    target_name=PurePosixPath(*(part for part in link.parts if part not in ('','.'))).as_posix()
                    if target_name not in entries or not entries[target_name].isfile():
                        raise UserError('Java 安裝檔硬連結目標不合法。')
            def destination(name):
                out=root.joinpath(*PurePosixPath(name).parts)
                if not out.resolve(strict=False).is_relative_to(root):raise UserError('Java 安裝檔包含越界路徑。')
                return out
            dirs=sorted((n for n,m in entries.items() if m.isdir()),key=lambda n:(len(PurePosixPath(n).parts),n))
            for name in dirs:
                out=destination(name);out.mkdir(parents=True,exist_ok=True)
                if out.is_symlink() or not out.is_dir():raise UserError('Java 安裝檔目錄結構衝突。')
            for name,m in entries.items():
                if not m.isfile():continue
                out=destination(name);out.parent.mkdir(parents=True,exist_ok=True)
                if out.is_symlink() or out.exists():raise UserError('Java 安裝檔包含目的地衝突。')
                src=tf.extractfile(m)
                if src is None:raise UserError('Java 安裝檔內容不完整。')
                written=0
                with src,out.open('xb') as dst:
                    for chunk in iter(lambda:src.read(1024*1024),b''):
                        written+=len(chunk)
                        if written>m.size or written>max_unpacked:raise UserError('Java 安裝檔內容超出安全限制。')
                        dst.write(chunk)
                if written!=m.size:raise UserError('Java 安裝檔內容不完整。')
                out.chmod(0o755 if m.mode&0o111 else 0o644)
            for name,m in entries.items():
                if not m.islnk():continue
                out=destination(name);link=PurePosixPath(m.linkname)
                target_file=destination(PurePosixPath(*(part for part in link.parts if part not in ('','.'))).as_posix())
                out.parent.mkdir(parents=True,exist_ok=True)
                if out.exists() or out.is_symlink() or target_file.is_symlink() or not target_file.is_file():
                    raise UserError('Java 安裝檔硬連結無法安全建立。')
                os.link(target_file,out)
            for name,m in entries.items():
                if not m.issym():continue
                out=destination(name);out.parent.mkdir(parents=True,exist_ok=True)
                if out.exists() or out.is_symlink():raise UserError('Java 安裝檔符號連結目的地衝突。')
                out.symlink_to(m.linkname)
            for name in dirs:
                destination(name).chmod(0o755)
    except (tarfile.TarError,OSError,RuntimeError) as exc:
        if isinstance(exc,UserError):raise
        raise UserError('Java 安裝檔無法安全解壓，請按「檢查及修復」重試。') from exc

def macho_cputypes(data):
    """Read CPU types from thin or fat Mach-O headers (only a few bytes needed)."""
    if len(data)<8:return set()
    magic_be=struct.unpack('>I',data[:4])[0]
    if magic_be in (0xcafebabe,0xcafebabf):
        count=struct.unpack('>I',data[4:8])[0]
        width=32 if magic_be==0xcafebabf else 20
        if count>64 or len(data)<8+count*width:return set()
        return {struct.unpack('>I',data[8+i*width:12+i*width])[0] for i in range(count)}
    magic_le=struct.unpack('<I',data[:4])[0]
    if magic_le in (0xcafebabe,0xcafebabf):
        count=struct.unpack('<I',data[4:8])[0]
        width=32 if magic_le==0xcafebabf else 20
        if count>64 or len(data)<8+count*width:return set()
        return {struct.unpack('<I',data[8+i*width:12+i*width])[0] for i in range(count)}
    # Thin Mach-O stores cputype at offset four; arm64 is 0x0100000c.
    return {struct.unpack('<I',data[4:8])[0]}

def validate_arm64_lwjgl_native(archive):
    try:
        with zipfile.ZipFile(archive) as z:
            members={Path(item.filename).name:item for item in z.infolist() if not item.is_dir()}
            for name in ('liblwjgl.dylib','openal.dylib'):
                item=members.get(name)
                if item is None or stat.S_ISLNK(item.external_attr>>16):
                    raise UserError('Apple Silicon LWJGL 套件缺少必要原生檔。')
                with z.open(item) as source:header=source.read(4096)
                if 0x0100000c not in macho_cputypes(header):
                    raise UserError('Apple Silicon LWJGL 原生檔不是 ARM64 架構。')
    except (zipfile.BadZipFile,OSError,RuntimeError) as exc:
        if isinstance(exc,UserError):raise
        raise UserError('Apple Silicon LWJGL 套件無法讀取；原版遊戲檔未變更。') from exc

def validate_arm64_jna(archive):
    """Validate the bundled, Java 8-compatible JNA jar and its ARM64 native slice."""
    archive=Path(archive)
    try:
        if archive.is_symlink() or not archive.is_file():
            raise UserError('Apple Silicon 舊版相容套件缺少 JNA；請重新解壓縮啟動器。')
        if archive.stat().st_size!=ARM64_JNA_JAR['size']:
            raise UserError('Apple Silicon 舊版 JNA 套件大小不符；請重新解壓縮啟動器。')
        if hashlib.sha256(archive.read_bytes()).hexdigest()!=ARM64_JNA_JAR['sha256']:
            raise UserError('Apple Silicon 舊版 JNA 套件校驗失敗；請重新解壓縮啟動器。')
        with zipfile.ZipFile(archive) as z:
            native=z.getinfo(ARM64_JNA_JAR['native_path'])
            if stat.S_ISLNK(native.external_attr>>16):
                raise UserError('Apple Silicon 舊版 JNA 原生庫格式無效；請重新解壓縮啟動器。')
            with z.open(native) as source:header=source.read(4096)
            if 0x0100000c not in macho_cputypes(header):
                raise UserError('Apple Silicon 舊版 JNA 套件沒有 ARM64 原生庫；已停止啟動。')
            native_class=z.read('com/sun/jna/Native.class')
            if len(native_class)<8 or native_class[:4]!=b'\xca\xfe\xba\xbe' or struct.unpack('>H',native_class[6:8])[0]>52:
                raise UserError('Apple Silicon 舊版 JNA 不相容於 Java 8；已停止啟動。')
    except UserError:
        raise
    except (KeyError,zipfile.BadZipFile,OSError,RuntimeError) as exc:
        raise UserError('Apple Silicon 舊版 JNA 套件無法讀取；請重新解壓縮啟動器。') from exc
    return archive

def validate_arm64_objc_bridge(archive):
    """Validate the bundled Java 8-compatible bridge and its universal macOS native."""
    archive=Path(archive)
    try:
        if archive.is_symlink() or not archive.is_file():
            raise UserError('Apple Silicon 舊版相容套件缺少 Objective-C bridge；請重新解壓縮啟動器。')
        if archive.stat().st_size!=ARM64_OBJC_BRIDGE_JAR['size']:
            raise UserError('Apple Silicon Objective-C bridge 套件大小不符；請重新解壓縮啟動器。')
        if hashlib.sha256(archive.read_bytes()).hexdigest()!=ARM64_OBJC_BRIDGE_JAR['sha256']:
            raise UserError('Apple Silicon Objective-C bridge 套件校驗失敗；請重新解壓縮啟動器。')
        with zipfile.ZipFile(archive) as z:
            native=z.getinfo(ARM64_OBJC_BRIDGE_JAR['native_path'])
            if stat.S_ISLNK(native.external_attr>>16):
                raise UserError('Apple Silicon Objective-C bridge 原生庫格式無效；已停止啟動。')
            with z.open(native) as source:header=source.read(4096)
            if 0x0100000c not in macho_cputypes(header):
                raise UserError('Apple Silicon Objective-C bridge 沒有 ARM64 原生庫；已停止啟動。')
            classes=[item for item in z.infolist() if item.filename.endswith('.class')]
            if not classes or ARM64_OBJC_BRIDGE_JAR['required_class'] not in {item.filename for item in classes}:
                raise UserError('Apple Silicon Objective-C bridge 缺少必要 Java 類別；已停止啟動。')
            for item in classes:
                if stat.S_ISLNK(item.external_attr>>16):
                    raise UserError('Apple Silicon Objective-C bridge 類別格式無效；已停止啟動。')
                with z.open(item) as source:header=source.read(8)
                if len(header)<8 or header[:4]!=b'\xca\xfe\xba\xbe' or struct.unpack('>H',header[6:8])[0]>52:
                    raise UserError('Apple Silicon Objective-C bridge 不相容於 Java 8；已停止啟動。')
    except UserError:
        raise
    except (KeyError,zipfile.BadZipFile,OSError,RuntimeError) as exc:
        raise UserError('Apple Silicon Objective-C bridge 套件無法讀取；請重新解壓縮啟動器。') from exc
    return archive

def extract_arm64_objc_bridge_native(archive,target):
    """Place the pinned universal JNI library on java.library.path for LWJGL2."""
    archive=validate_arm64_objc_bridge(archive)
    target=Path(target)
    if target.is_symlink():raise UserError('Apple Silicon Objective-C 原生庫目錄為符號連結；已停止啟動。')
    temporary=None
    try:
        target.mkdir(parents=True,exist_ok=True)
        native_path=inside(target,ARM64_OBJC_BRIDGE_JAR['native_path'])
        if native_path.is_symlink():raise UserError('Apple Silicon Objective-C 原生庫是符號連結；已停止啟動。')
        with zipfile.ZipFile(archive) as z:
            native=z.getinfo(ARM64_OBJC_BRIDGE_JAR['native_path'])
            if native.file_size<=0 or native.file_size>32*1024*1024 or stat.S_ISLNK(native.external_attr>>16):
                raise UserError('Apple Silicon Objective-C 原生庫大小或格式無效；已停止啟動。')
            fd,name=tempfile.mkstemp(prefix='.libjcocoa-',suffix='.part',dir=target)
            temporary=Path(name);header=b'';count=0
            with os.fdopen(fd,'wb') as out,z.open(native) as source:
                while True:
                    block=source.read(1024*1024)
                    if not block:break
                    count+=len(block)
                    if count>native.file_size:raise UserError('Apple Silicon Objective-C 原生庫長度不符；已停止啟動。')
                    if len(header)<4096:header+=block[:4096-len(header)]
                    out.write(block)
                out.flush();os.fsync(out.fileno())
            if count!=native.file_size or 0x0100000c not in macho_cputypes(header):
                raise UserError('Apple Silicon Objective-C 原生庫不完整或沒有 ARM64 架構；已停止啟動。')
        os.chmod(temporary,0o755)
        os.replace(temporary,native_path);temporary=None
        return native_path
    except UserError:
        raise
    except (KeyError,zipfile.BadZipFile,OSError,RuntimeError) as exc:
        raise UserError('Apple Silicon Objective-C 原生庫無法安全安裝到遊戲執行目錄；已停止啟動。') from exc
    finally:
        if temporary is not None:temporary.unlink(missing_ok=True)

def arm64_lwjgl2_classpath(data,game):
    if not has_lwjgl2(data):raise UserError('這個版本沒有可替換的 LWJGL 2 Java 函式庫。')
    _,classpath,_=library_plan(data,game)
    original=set();jna_original=set();found=set()
    for lib in data.get('libraries',[]):
        if not isinstance(lib,dict) or not allowed(lib.get('rules')):continue
        parts=lib.get('name','').split(':')
        if len(parts)<3:continue
        if parts[:2]==['net.java.dev.jna','jna']:
            artifact=lib.get('downloads',{}).get('artifact')
            relative=(artifact or {}).get('path') or maven_path(lib['name'])
            jna_original.add(inside(game/'libraries',relative))
            continue
        if parts[0]!='org.lwjgl.lwjgl' or parts[1] not in ('lwjgl','lwjgl_util'):continue
        found.add(parts[1]);downloads=lib.get('downloads',{});artifact=downloads.get('artifact')
        relative=(artifact or {}).get('path') or maven_path(lib['name'])
        original.add(inside(game/'libraries',relative))
    if found!={'lwjgl','lwjgl_util'}:
        raise UserError('這個舊版的 LWJGL 2 元件不完整，為避免混用架構已停止啟動。')
    lwjgl=inside(game/'libraries',ARM64_LWJGL_JAR['path'])
    lwjgl_util=inside(game/'libraries',ARM64_LWJGL_UTIL_JAR['path'])
    bundled_jna=validate_arm64_jna(Path(__file__).resolve().parent/ARM64_JNA_JAR['path']) if jna_original else None
    output=[];inserted_lwjgl=False;inserted_jna=False
    for path in classpath:
        if path in original:
            if not inserted_lwjgl:
                output.extend([lwjgl,lwjgl_util]);inserted_lwjgl=True
        elif path in jna_original:
            if not inserted_jna:
                output.append(bundled_jna);inserted_jna=True
        else:output.append(path)
    if not inserted_lwjgl:raise UserError('找不到舊版 LWJGL 2 的 classpath 位置。')
    if jna_original and not inserted_jna:raise UserError('找不到舊版 JNA 的 classpath 位置。')
    return output

def java_info(path):
    try:
        r = subprocess.run([str(path), '-XshowSettings:properties', '-version'], capture_output=True, text=True, timeout=8)
        s = r.stdout + r.stderr
        version = re.search(r'(?:java\.version\s*=\s*|version ")(?:1\.)?(\d+)', s)
        arch = re.search(r'os\.arch\s*=\s*(\S+)', s)
        if r.returncode == 0 and version and arch: return int(version[1]), {'amd64':'x86_64','arm64':'aarch64'}.get(arch[1],arch[1])
    except (OSError, subprocess.TimeoutExpired): pass
    return None

def java_file_arch(path):
    """Inspect a macOS Java executable before running it, avoiding Rosetta prompts."""
    if host_os()!='osx':return None
    try:
        result=subprocess.run(['/usr/bin/file','-b',str(Path(path).resolve())],capture_output=True,text=True,timeout=3)
        value=result.stdout.lower()
        if result.returncode==0 and 'arm64' in value:return 'aarch64'
        if result.returncode==0 and 'x86_64' in value:return 'x86_64'
    except (OSError,RuntimeError,subprocess.TimeoutExpired):pass
    return None

def command(data, game, instance, java, name, ram, game_directory=None,classpath_override=None,natives_directory=None,auth=None):
    _, cp, _ = library_plan(data, game)
    if classpath_override is not None:cp=list(classpath_override)
    base = ident(data.get('jar', data['id']))
    cp.append(game/'versions'/base/(base+'.jar'))
    missing = [p for p in cp if not p.is_file()]
    if missing: raise UserError(f'缺少 {len(missing)} 個遊戲檔案，請按「檢查及修復」。')
    values = {'natives_directory':str(natives_directory or instance/'natives'), 'launcher_name':'MambaCraft', 'launcher_version':APP_VERSION,
      'classpath':os.pathsep.join(map(str,cp)), 'auth_player_name':username(name), 'version_name':data['id'],
      'game_directory':str(game_directory or instance), 'assets_root':str(game/'assets'), 'assets_index_name':data.get('assetIndex',{}).get('id',data.get('assets',data['id'])),
      'auth_uuid':offline_uuid(name).replace('-',''), 'auth_access_token':'0', 'user_type':'legacy',
      'version_type':data.get('type','release'), 'user_properties':'{}', 'library_directory':str(game/'libraries'),
      'classpath_separator':os.pathsep, 'clientid':'', 'auth_xuid':'', 'game_assets':str(game/'assets')}
    values['auth_session']='token:'+values['auth_access_token']+':'+values['auth_uuid']
    if auth:
        values.update(auth_player_name=username(auth['name']),auth_uuid=auth['uuid'],auth_access_token=auth['token'],user_type='msa' if auth.get('kind')=='microsoft' else 'mojang', clientid=auth.get('client_id',''), auth_xuid=auth.get('xuid',''))
        values['auth_session']=auth['token']
    def replace(s):
        result = re.sub(r'\$\{([^}]+)\}', lambda m: values.get(m[1],m[0]), s)
        if '${' in result: raise UserError('這個版本使用尚未支援的啟動參數，已停止啟動。')
        return result
    def args(items):
        out=[]
        for item in items:
            if isinstance(item,str): out.append(replace(item))
            elif allowed(item.get('rules', item.get('compatibilityRules'))):
                val=item['value']; out.extend(replace(x) for x in ([val] if isinstance(val,str) else val))
        return out
    modern_arguments=isinstance(data.get('arguments'),dict)
    if modern_arguments: result=[str(java),f'-Xmx{ram}M','-Xms512M'] + args(data['arguments'].get('jvm',[]))
    else: result=[str(java),f'-Xmx{ram}M','-Xms512M','-Djava.library.path='+values['natives_directory'],'-cp',values['classpath']]
    if auth and auth.get('kind') != 'microsoft':
        result.insert(1,'-javaagent:'+auth['injector']+'='+auth['server'])
        result.insert(2,'-Dauthlibinjector.yggdrasil.prefetched='+auth['metadata'])
    if host_os() == 'osx':
        # GLFW/LWJGL 3 needs the first thread. Legacy LWJGL 2 uses the AWT/
        # AppKit event loop and must not inherit this GLFW-specific option.
        first_thread='-XstartOnFirstThread'
        declared=first_thread in result[1:]
        glfw=any(isinstance(lib,dict) and isinstance(lib.get('name'),str) and
                 lib.get('name','').split(':')[:2]==['org.lwjgl','lwjgl-glfw'] and
                 allowed(lib.get('rules')) for lib in data.get('libraries',[]))
        result=[result[0]]+[item for item in result[1:] if item!=first_thread]
        if not has_lwjgl2(data) and (declared or glfw):result.insert(1,first_thread)
    log=data.get('logging',{}).get('client')
    if log: result.append(log['argument'].replace('${path}',str(inside(game/'assets/log_configs',log['file']['id']))))
    if 'minecraftArguments' in data:
        import shlex
        game_args=[replace(x) for x in shlex.split(data['minecraftArguments'])]
    else: game_args=args(data['arguments']['game'])
    return result+[data['mainClass']]+game_args

def command_for_log(command):
    """Return a useful launch trace without recording credentials or identity."""
    sensitive={'--accessToken','--clientToken','--sessionId','--session','--username','--uuid'}
    result=[]; redact_next=False
    for item in command:
        if redact_next:
            result.append('<redacted>');redact_next=False;continue
        value=str(item)
        for key in sensitive:
            if value.startswith(key+'='):
                value=key+'=<redacted>'
                break
        result.append(value)
        if value in sensitive:redact_next=True
    return result

class Engine:
    def __init__(self, root):
        self.root=Path(root).resolve(); self.root.mkdir(parents=True,exist_ok=True)
        self.game=self.root/'game'; self.logs=self.root/'logs'
        self.logs.mkdir(exist_ok=True); self.lock=threading.RLock()
        self.cancel=threading.Event(); self.job={'status':'idle','message':'準備就緒','done':0,'total':0}
        self.config_path=self.root/'settings.json'; self.roots_path=self.root/'external-roots.json'; self.warning=''; self.discovered={}; self.scan_time=0
        try:
            self.config=read_json(self.config_path) if self.config_path.exists() else {}
            if not isinstance(self.config,dict): raise ValueError('settings must be an object')
            names=self.config.get('profiles',['Steve'])
            if not isinstance(names,list) or not names or len(names)>30 or any(not isinstance(x,str) or not NAME_RE.fullmatch(x) for x in names): raise ValueError('invalid profiles')
            if self.config.get('selected','Steve') not in names: raise ValueError('invalid selected player')
            if type(self.config.get('ram',0)) is not int or self.config.get('ram',0) not in (0,2048,3072,4096,6144,8192): raise ValueError('invalid memory')
        except (ValueError,OSError):
            backup=self.config_path.with_name('settings-damaged-'+str(time.time_ns())+'.json')
            shutil.copy2(self.config_path,backup); self.config={}; self.warning='設定檔損壞，已保留副本並重設。'
        self.config.setdefault('profiles',['Steve']); self.config.setdefault('selected','Steve'); self.config.setdefault('ram',0)
        if self.config.get('edition') not in ('java','bedrock'):self.config['edition']='java'
        if self.config.get('theme') not in ('dark','light'):self.config['theme']='dark'
        if self.config.get('language') not in ('zh-Hant','zh-Hans','en'):self.config.pop('language',None)
        self.recommended_java_root=self.root/'runtimes'
        selected_java_root=self.config.get('java_root')
        try:
            selected=Path(selected_java_root).expanduser() if isinstance(selected_java_root,str) and selected_java_root.strip() else self.recommended_java_root
            self.java_root=selected.resolve(strict=False) if selected.is_absolute() else self.recommended_java_root
        except (OSError,RuntimeError):self.java_root=self.recommended_java_root
        self.process=None; self.running=None; self.last_exit=None; self.last_log=None; self.closing=False; self.java_source=None
        self.last_auth_token=None
        from java_accounts import AccountManager
        self.java_accounts=AccountManager(self)
        from microsoft_accounts import MicrosoftAccountManager
        self.microsoft_accounts=MicrosoftAccountManager(self)
        self.catalog=[]
        self.market={'kind':'mod','query':'','gameVersion':'','loader':'any','results':[],
                     'versions':{},'source':'','error':'','manualUrl':''}
        self.mod_projects={}; self.mod_versions={}
        try:
            cached=read_json(self.root/'catalog.json').get('versions',[])
            if isinstance(cached,list):self.catalog=[v for v in cached if isinstance(v,dict) and supported(v.get('id','')) and v.get('type') in VERSION_TYPES]
        except (ValueError,OSError,KeyError,AttributeError): pass
    def progress(self,message=None,done=None,total=None):
        with self.lock:
            if message is not None: self.job['message']=message
            if done is not None: self.job['done']=done
            if total is not None: self.job['total']=total
    def managed_instances(self):
        result=[]
        for p in sorted((self.root/'instances').glob('*/instance.json')):
            try:
                d=read_json(p); ident(d['id']);
                if d['id']!=p.parent.name or p.parent.is_symlink():continue
                version=ident(d.get('version',d['id']))
                d.update(managed=True,instancePath=str(p.parent.resolve()),gamePath=str(self.game/'versions'/version),
                         savesPath=str(p.parent/'saves'),modsPath=str(p.parent/'mods'),configPath=str(p.parent/'config'))
                stored=d.get('java')
                if isinstance(stored,str):
                    java=Path(stored).expanduser()
                    d['javaPath']=str(java.resolve() if java.is_absolute() else inside(self.root,stored))
                else:d['javaPath']=''
                result.append(d)
            except (OSError,ValueError,KeyError,TypeError,UserError): continue
        return result
    def root_candidates(self):
        home=Path.home(); app=home/'Library/Application Support'
        candidates=[home/'.minecraft',app/'minecraft',app/'.minecraft']
        for launcher in ('PrismLauncher','MultiMC','PolyMC','ATLauncher'):
            base=app/launcher/'instances'
            if base.is_dir():
                try: folders=sorted(base.iterdir())[:150]
                except OSError: folders=[]
                for inst in folders: candidates.extend((inst/'.minecraft',inst/'minecraft',inst))
        for base in (app/'CurseForge/Minecraft/Instances',app/'technic/modpacks',home/'Library/ATLauncher/instances'):
            if base.is_dir():
                try:candidates.extend(sorted(base.iterdir())[:150])
                except OSError:pass
        try:
            data=read_json(self.roots_path); configured=data.get('roots',[])
            if isinstance(configured,list): candidates.extend(Path(x) for x in configured if isinstance(x,str))
        except (OSError,ValueError,AttributeError):pass
        result=[];seen=set()
        for candidate in candidates:
            try:
                resolved=candidate.expanduser().resolve(strict=True)
                if resolved.is_dir() and (resolved/'versions').is_dir() and resolved not in seen:
                    seen.add(resolved);result.append(resolved)
            except OSError:continue
        return result
    def scan_external(self,force=False):
        if not force and time.monotonic()-self.scan_time<5:return self.discovered
        result={};managed={x['id'] for x in self.managed_instances()}
        for root in self.root_candidates():
            try:
                if root.samefile(self.game):continue
            except OSError:pass
            try:folders=list((root/'versions').iterdir())[:1500]
            except OSError:continue
            for folder in folders:
                if not folder.is_dir() or folder.is_symlink() or not supported(folder.name):continue
                manifest=folder/(folder.name+'.json');jar=folder/(folder.name+'.jar')
                try:
                    if manifest.is_symlink() or not manifest.is_file() or manifest.stat().st_size>8_000_000 or not jar.is_file() or jar.is_symlink():continue
                    data=read_json(manifest)
                    if not isinstance(data,dict) or data.get('id')!=folder.name or not isinstance(data.get('mainClass'),str):continue
                    entries,classpath,_=library_plan(data,root)
                    if any(not p.is_file() for p in classpath):continue
                    idx=data.get('assetIndex')
                    if idx and not inside(root/'assets/indexes',ident(idx.get('id',''))+'.json').is_file():continue
                    key='import-'+hashlib.sha256(str(root).encode()).hexdigest()[:12]+'-'+hashlib.sha256(folder.name.encode()).hexdigest()[:16]
                    if key in managed:continue
                    result[key]={'id':key,'version':folder.name,'loader':'Existing','managed':False,
                      'sourceRoot':str(root),'instancePath':str(root),'gamePath':str(folder),
                      'savesPath':str(root/'saves'),'modsPath':str(root/'mods'),'configPath':str(root/'config'),
                      'javaPath':'','java_major':java_major_for(data,folder.name),'releaseTime':data.get('releaseTime','')}
                except (OSError,ValueError,TypeError,AttributeError,UserError):continue
        self.discovered=result;self.scan_time=time.monotonic();return result
    def installed(self):return self.managed_instances()+list(self.scan_external().values())
    def save_external_root(self,folder):
        try:root=Path(folder).expanduser().resolve(strict=True)
        except (OSError,TypeError):raise UserError('找不到選取的資料夾。')
        if not root.is_dir():raise UserError('選取的路徑不是資料夾。')
        roots=[]; seen=set()
        def add(candidate):
            try:
                candidate=Path(candidate).resolve(strict=True)
                if candidate.is_dir() and (candidate/'versions').is_dir() and candidate not in seen:
                    seen.add(candidate);roots.append(candidate)
            except OSError:pass
        # Accept the game root itself, its versions folder, or an item inside
        # versions (a common choice when navigating to a specific installation).
        add(root)
        if not roots and root.name.casefold()=='versions':add(root.parent)
        if not roots and root.parent.name.casefold()=='versions':add(root.parent.parent)
        if not roots:
            for name in ('.minecraft','minecraft','Minecraft','game'):
                add(root/name)
        # Prism/MultiMC-style users may choose a custom instances directory.
        if not roots and root.name.casefold() in ('instances','instance'):
            try:children=sorted(root.iterdir())[:150]
            except OSError:children=[]
            for child in children:
                add(child)
                for name in ('.minecraft','minecraft','Minecraft','game'):add(child/name)
        if not roots:
            for parent in list(root.parents)[:3]:add(parent)
        if not roots:
            raise UserError(f'在「{root.name}」中找不到 versions 資料夾。請選 Minecraft 遊戲根目錄、versions 資料夾，或啟動器的 instances 資料夾。')
        try:existing=read_json(self.roots_path).get('roots',[])
        except (OSError,ValueError,AttributeError):existing=[]
        if not isinstance(existing,list):existing=[]
        additions=[str(path) for path in roots if str(path) not in existing]
        if len(existing)+len(additions)>40:raise UserError('最多新增 40 個遊戲資料夾。請刪除不再使用的資料夾後重試。')
        if additions:atomic_json(self.roots_path,{'roots':existing+additions})
        self.scan_time=0;self.scan_external(force=True)
        count=sum(x['sourceRoot'] in {str(path) for path in roots} for x in self.discovered.values())
        return f'已加入／檢查 {len(roots)} 個 Minecraft 資料夾：找到 {count} 個可辨識版本。'
    def state(self):
        with self.lock:
            if self.process and self.process.poll() is not None:
                self.last_exit=self.process.returncode; self.process=None; self.running=None
            versions=[{'id':v['id'],'releaseTime':v.get('releaseTime',''),'type':v.get('type','release')} for v in self.catalog if supported(v.get('id')) and v.get('type') in ('release','snapshot','old_beta','old_alpha')]
            active=self.microsoft_accounts.active() or self.java_accounts.active()
            return {'version':APP_VERSION,'profiles':self.config['profiles'][:], 'selected':self.config['selected'], 'javaAccounts':self.java_accounts.state(), 'javaAccount':active, 'ram':self.config['ram'],'theme':self.config['theme'],'language':self.config.get('language'),'edition':self.config.get('edition','java'),
              'microsoftAccounts':self.microsoft_accounts.state(),
              'versions':versions, 'installed':self.installed(), 'job':dict(self.job), 'running':self.running,
              'market':json.loads(json.dumps(self.market,ensure_ascii=False)),
              'lastExit':self.last_exit,'lastLog':self.last_log,'warning':self.warning,'root':str(self.root),
              'javaRoot':str(self.java_root),'recommendedJavaRoot':str(self.recommended_java_root),
              'platform':platform.system()+' '+platform.machine(),'freeGB':round(shutil.disk_usage(self.root).free/2**30,1)}
    def set_java_root(self,path):
        with self.lock:
            if self.job['status']=='running' or self.process and self.process.poll() is None:raise UserError('請等候目前工作或遊戲結束後，再更改 Java 位置。')
            new_config=dict(self.config)
            if path is None or path=='':
                new_config.pop('java_root',None);candidate=self.recommended_java_root
            else:
                if not isinstance(path,str) or len(path)>2048:raise UserError('Java 資料夾路徑不合法。')
                try:candidate=Path(path).expanduser().resolve(strict=True)
                except (OSError,RuntimeError):raise UserError('找不到選取的 Java 資料夾。')
                if not candidate.is_dir():raise UserError('選取的 Java 位置不是資料夾。')
                try:
                    with tempfile.NamedTemporaryFile(prefix='.mambacraft-write-test-',dir=candidate):pass
                except OSError:raise UserError('這個資料夾無法寫入。請選擇可寫入的 Java 安裝位置。')
                new_config['java_root']=str(candidate)
            atomic_json(self.config_path,new_config)
            self.config=new_config;self.java_root=candidate
        return 'Java 安裝／搜尋位置：'+str(self.java_root)
    def save_profile(self, name):
        name=username(name)
        with self.lock:
            if self.java_accounts.changing: raise UserError('正在更新皮膚站帳號，請稍候。')
            if self.job['status']=='running' or self.process and self.process.poll() is None: raise UserError('請先等候工作／遊戲結束，再更改玩家。')
            if name not in self.config['profiles']:
                if len(self.config['profiles'])>=30: raise UserError('最多保留 30 個本地玩家。')
                self.config['profiles'].append(name)
            self.config['selected']=name; self.config.pop('java_account',None); self.config.pop('microsoft_account',None); atomic_json(self.config_path,self.config)
    def remove_profile(self, name):
        name=username(name)
        with self.lock:
            if self.java_accounts.changing: raise UserError('正在更新皮膚站帳號，請稍候。')
            if self.job['status']=='running' or self.process and self.process.poll() is None:
                raise UserError('請先等候工作／遊戲結束，再更改玩家。')
            if name not in self.config['profiles']:
                raise UserError('找不到已儲存的本地玩家。')
            if len(self.config['profiles'])<=1:
                raise UserError('至少要保留一個本地玩家。')
            new_config=dict(self.config)
            new_config['profiles']=[profile for profile in self.config['profiles'] if profile!=name]
            if new_config['selected']==name:new_config['selected']=new_config['profiles'][0]
            atomic_json(self.config_path,new_config)
            self.config=new_config
    def memory(self, value):
        if type(value) is not int or value not in (0,2048,3072,4096,6144,8192): raise UserError('記憶體設定不合法。')
        with self.lock:
            if self.job['status']=='running': raise UserError('請等候目前工作完成。')
            self.config['ram']=value; atomic_json(self.config_path,self.config)
    def set_theme(self, value):
        if value not in ('dark','light'):raise UserError('外觀主題設定不合法。')
        with self.lock:
            new_config=dict(self.config);new_config['theme']=value
            atomic_json(self.config_path,new_config);self.config=new_config
        return '已切換至'+('淺色' if value=='light' else '深色')+'主題。'
    def set_language(self, value):
        if value not in ('zh-Hant','zh-Hans','en'):raise UserError('語言設定不合法。')
        with self.lock:
            new_config=dict(self.config);new_config['language']=value
            atomic_json(self.config_path,new_config);self.config=new_config
        return '已儲存介面語言。'
    def set_edition(self, value):
        if value not in ('java','bedrock'):raise UserError('遊戲版本管理偏好不合法。')
        with self.lock:
            new_config=dict(self.config);new_config['edition']=value
            atomic_json(self.config_path,new_config);self.config=new_config
        return '已儲存遊戲版本管理偏好。'
    def mod_json(self,url):
        from urllib.parse import urlparse
        parsed=urlparse(url)
        if parsed.scheme!='https' or parsed.hostname!='api.modrinth.com' or not parsed.path.startswith('/v2/'):
            raise UserError('拒絕不安全的 Modrinth API 要求。')
        mirror=MCIM_API+parsed.path[len('/v2'):]
        if parsed.query:mirror+='?'+parsed.query
        last_error=None
        for index,candidate in enumerate((url,mirror)):
            if self.cancel.is_set():raise Cancelled('已取消搜尋。')
            if index:self.progress('Modrinth 官方 API 連線失敗，正在切換中國大陸 MCIM 鏡像…')
            try:
                with Network(self.cancel,lambda msg:self.progress(msg)).response(candidate) as response:
                    if int(response.headers.get('Content-Length','0') or 0)>20*1024*1024:
                        raise UserError('Modrinth API 回應超過安全大小上限。')
                    return response.json(),('Modrinth 官方' if index==0 else 'MCIM 鏡像')
            except (requests.RequestException,ValueError) as exc:last_error=exc
        if last_error:raise UserError('Modrinth 官方來源與 MCIM 備援均無法連線。請稍後重試，或開啟 Modrinth 專案頁手動下載。') from last_error
        raise UserError('無法取得 Modrinth 資料。')
    def mod_search(self,payload):
        from urllib.parse import urlencode
        kind=payload.get('kind','mod');query=payload.get('query','')
        game_version=payload.get('game_version','');loader=payload.get('loader','any')
        if kind not in ('mod','modpack'):raise UserError('搜尋類型不合法。')
        if not isinstance(query,str) or len(query)>120 or any(ord(c)<32 for c in query):raise UserError('搜尋關鍵字最多 120 個字元。')
        query=query.strip()
        if game_version:
            if not isinstance(game_version,str) or len(game_version)>64 or not supported(game_version):raise UserError('Minecraft 版本篩選不合法。')
        if loader not in ('any','fabric','forge','neoforge','quilt'):raise UserError('模組載入器篩選不合法。')
        self.mod_projects={};self.mod_versions={}
        self.market={'kind':kind,'query':query,'gameVersion':game_version,'loader':loader,
                     'results':[],'versions':{},'source':'','error':'','manualUrl':'https://modrinth.com/'+kind}
        facets=[[f'project_type:{kind}']]
        if game_version:facets.append([f'versions:{game_version}'])
        if loader!='any' and kind=='mod':facets.append([f'categories:{loader}'])
        params={'facets':json.dumps(facets,separators=(',',':')),'index':'downloads' if not query else 'relevance','limit':'24'}
        if query:params['query']=query
        url=MODRINTH_API+'/search?'+urlencode(params)
        self.progress('正在搜尋 Modrinth '+('整合包' if kind=='modpack' else 'Mods')+'…')
        data,source=self.mod_json(url)
        if not isinstance(data,dict) or not isinstance(data.get('hits'),list):raise UserError('Modrinth 搜尋回傳格式不完整。')
        results=[];projects={}
        for item in data['hits'][:24]:
            if not isinstance(item,dict):continue
            project_id=item.get('project_id');slug=item.get('slug');project_type=item.get('project_type')
            if not isinstance(project_id,str) or not re.fullmatch(r'[A-Za-z0-9]{8,16}',project_id):continue
            if not isinstance(slug,str) or len(slug)>100 or any(ord(c)<32 or c in '/\\?#' for c in slug):continue
            if project_type!=kind:continue
            clean={'project_id':project_id,'slug':slug,'project_type':kind,
                   'title':str(item.get('title',''))[:180],'description':str(item.get('description',''))[:500],
                   'author':str(item.get('author',''))[:100],
                   'downloads':max(0,int(item.get('downloads',0) or 0)),
                   'versions':[v for v in item.get('versions',[]) if isinstance(v,str) and len(v)<=64][:40],
                   'categories':[v for v in item.get('categories',[]) if isinstance(v,str) and len(v)<=40][:12]}
            icon_url=modrinth_icon_url(item.get('icon_url'))
            if icon_url:clean['icon_url']=icon_url
            results.append(clean);projects[project_id]=clean
        self.mod_projects=projects;self.mod_versions={}
        self.market={'kind':kind,'query':query,'gameVersion':game_version,'loader':loader,
                     'results':results,'versions':{},'source':source,'error':'',
                     'manualUrl':'https://modrinth.com/'+('modpack' if kind=='modpack' else 'mod')}
        return f'找到 {len(results)} 個'+('整合包' if kind=='modpack' else 'Mod')+'。來源：'+source+'。'
    def mod_versions_for_project(self,payload):
        from urllib.parse import quote,urlencode
        project_id=payload.get('project_id');game_version=payload.get('game_version','');loader=payload.get('loader','any')
        project=self.mod_projects.get(project_id) if isinstance(project_id,str) else None
        if not project:raise UserError('搜尋結果已過期；請重新搜尋後再選版本。')
        if game_version and (not isinstance(game_version,str) or len(game_version)>64 or not supported(game_version)):
            raise UserError('Minecraft 版本篩選不合法。')
        if loader not in ('any','fabric','forge','neoforge','quilt'):raise UserError('模組載入器篩選不合法。')
        params={'include_changelog':'false'}
        if game_version:params['game_versions']=json.dumps([game_version],separators=(',',':'))
        if loader!='any':params['loaders']=json.dumps([loader],separators=(',',':'))
        url=MODRINTH_API+'/project/'+quote(project_id,safe='')+'/version?'+urlencode(params)
        self.progress('正在讀取 '+project['title']+' 的相容版本…')
        data,source=self.mod_json(url)
        if not isinstance(data,list):raise UserError('Modrinth 版本資料格式不完整。')
        items=[];cache={}
        for raw in data[:100]:
            if not isinstance(raw,dict):continue
            version_id=raw.get('id');files=raw.get('files')
            if not isinstance(version_id,str) or not re.fullmatch(r'[A-Za-z0-9]{8,32}',version_id) or not isinstance(files,list) or not files:continue
            safe_files=[]
            for file in files[:10]:
                if not isinstance(file,dict):continue
                filename=safe_download_name(file.get('filename'),'download.bin')
                url_value=file.get('url');hashes=file.get('hashes')
                if not isinstance(url_value,str) or not isinstance(hashes,dict):continue
                safe_files.append({'filename':filename,'primary':bool(file.get('primary')),
                                   'size':file.get('size') if type(file.get('size')) is int else None,
                                   'url':url_value,'hashes':hashes})
            if not safe_files:continue
            version={'id':version_id,'version_number':str(raw.get('version_number',''))[:80],
                     'name':str(raw.get('name',''))[:180],
                     'game_versions':[v for v in raw.get('game_versions',[]) if isinstance(v,str) and len(v)<=64][:40],
                     'loaders':[v for v in raw.get('loaders',[]) if isinstance(v,str) and len(v)<=40][:8],
                     'date_published':str(raw.get('date_published',''))[:40],
                     'version_type':str(raw.get('version_type','release'))[:30],
                     'downloads':max(0,int(raw.get('downloads',0) or 0)),
                     'files':[{'filename':f['filename'],'primary':f['primary'],'size':f['size']} for f in safe_files]}
            items.append(version);cache[version_id]={'project_id':project_id,'version':version,'files':safe_files}
        self.mod_versions.update(cache)
        self.market['versions'][project_id]={'items':items,'source':source}
        self.market['source']=source;self.market['error']=''
        if not items:return '找不到符合所選 Minecraft 版本／載入器的檔案；請調整篩選或在 Modrinth 專案頁檢查。'
        return f'找到 {len(items)} 個相容版本。來源：{source}。'
    def _mod_file_sources(self,file):
        from urllib.parse import urlparse
        url=file.get('url')
        parsed=urlparse(url) if isinstance(url,str) else None
        if not parsed or parsed.scheme!='https' or parsed.hostname!='cdn.modrinth.com' or parsed.username or parsed.password:
            raise UserError('這個檔案不在啟動器允許的 Modrinth CDN；請從專案頁面手動下載。')
        mirrors=[modrinth_file_mirror(url)]
        return url,[candidate for candidate in mirrors if candidate]
    def _verified_download(self,file,destination,net,max_bytes=1024*1024*1024):
        url,fallback_urls=self._mod_file_sources(file)
        hashes=file.get('hashes') if isinstance(file.get('hashes'),dict) else {}
        sha1_digest=hashes.get('sha1');sha512_digest=hashes.get('sha512')
        if not (isinstance(sha1_digest,str) and re.fullmatch(r'[a-fA-F0-9]{40}',sha1_digest)) and not (isinstance(sha512_digest,str) and re.fullmatch(r'[a-fA-F0-9]{128}',sha512_digest)):
            raise UserError('來源未提供有效 SHA-1／SHA-512，為保護遊戲檔案已停止下載。')
        size=file.get('size')
        if type(size) is not int or size<0 or size>max_bytes:raise UserError('來源檔案大小不合法或超過安全上限。')
        return net.download(url,destination,digest=sha1_digest.lower() if isinstance(sha1_digest,str) else None,
                            size=size,sha512_digest=sha512_digest.lower() if isinstance(sha512_digest,str) else None,
                            extra_hosts=MOD_FILE_HOSTS,max_bytes=max_bytes,fallback_urls=fallback_urls)
    def _downloads_directory(self):
        path=Path.home()/'Downloads'
        try:path.mkdir(parents=True,exist_ok=True)
        except OSError as exc:raise UserError('無法建立系統 Downloads 資料夾；請在設定中確認家目錄可寫入。') from exc
        if not path.is_dir():raise UserError('系統 Downloads 路徑不是資料夾。')
        return path.resolve()
    def _unique_file(self,directory,name):
        name=safe_download_name(name)
        target=inside(directory,name)
        if target.exists() or target.is_symlink():
            stem=Path(name).stem;suffix=Path(name).suffix
            for index in range(2,10000):
                candidate=inside(directory,f'{stem} ({index}){suffix}')
                if not candidate.exists() and not candidate.is_symlink():return candidate
            raise UserError('同名檔案過多，請清理下載資料夾後重試。')
        return target
    def download_mod(self,payload):
        project_id=payload.get('project_id');version_id=payload.get('version_id');destination=payload.get('destination','downloads')
        project=self.mod_projects.get(project_id) if isinstance(project_id,str) else None
        selected=self.mod_versions.get(version_id) if isinstance(version_id,str) else None
        if not project or not selected or selected['project_id']!=project_id:raise UserError('搜尋結果已過期；請重新搜尋並選擇版本。')
        if project['project_type']!='mod':raise UserError('所選項目不是 Mod。')
        if destination not in ('downloads','mods'):raise UserError('下載目的地不合法。')
        file=next((item for item in selected['files'] if item.get('primary')),selected['files'][0])
        if Path(file['filename']).suffix.lower()!='.jar':raise UserError('所選版本不是 JAR Mod；請在專案頁面確認下載檔案。')
        if destination=='downloads':target=self._unique_file(self._downloads_directory(),file['filename'])
        else:
            instance_id=payload.get('instance_id')
            folder,record=self.get_instance({'id':instance_id})
            version=record.get('version')
            if version not in selected['version'].get('game_versions',[]):raise UserError('這個 Mod 版本與所選 Minecraft 版本不相容。')
            loader=record.get('loader')
            supported_loaders=selected['version'].get('loaders',[])
            if loader=='fabric' and 'fabric' not in supported_loaders:raise UserError('這個 Mod 版本不支援所選 Fabric 遊戲。')
            if loader=='vanilla':raise UserError('原版遊戲沒有 Mods 載入器；請先安裝相容的 Fabric，或選擇已安裝的 Forge／Fabric 遊戲。')
            if loader=='Existing':
                requested_loader=payload.get('loader')
                if requested_loader not in ('fabric','forge','neoforge','quilt'):
                    raise UserError('外部遊戲的 Mod 載入器無法辨識；請先在搜尋條件選擇該遊戲實際使用的 Fabric、Forge、NeoForge 或 Quilt。')
                if requested_loader not in supported_loaders:raise UserError('這個 Mod 版本與所選外部遊戲載入器不相容。')
            if loader not in ('fabric','Existing') and loader not in supported_loaders:raise UserError('這個 Mod 版本與遊戲載入器不相容。')
            mods=Path(record.get('modsPath') or folder/'mods')
            try:mods.mkdir(parents=True,exist_ok=True)
            except OSError as exc:raise UserError('無法建立目標遊戲的 Mods 資料夾。') from exc
            if mods.is_symlink() or not mods.is_dir():raise UserError('目標 Mods 路徑不安全；為保護資料已停止安裝。')
            target=self._unique_file(mods.resolve(),file['filename'])
        net=Network(self.cancel,lambda msg:self.progress(msg))
        self.progress('正在下載並校驗 '+file['filename']+'…',0,1)
        try:self._verified_download(file,target,net,200*1024*1024)
        except (requests.RequestException,UserError) as exc:
            if isinstance(exc,Cancelled):raise
            raise UserError('Modrinth 官方檔案與 MCIM 備援均未能提供有效檔案；未覆蓋既有資料。請手動開啟 '+
                            'https://modrinth.com/mod/'+project['slug']+' 下載。') from exc
        self.progress('Mod 已下載並通過 SHA 校驗。',1,1)
        remember_download(self.root,target)
        return f'{project["title"]} {selected["version"].get("version_number","")} 已下載至：{target}'
    def download_modpack(self,payload):
        project_id=payload.get('project_id');version_id=payload.get('version_id')
        project=self.mod_projects.get(project_id) if isinstance(project_id,str) else None
        selected=self.mod_versions.get(version_id) if isinstance(version_id,str) else None
        if not project or not selected or selected['project_id']!=project_id:raise UserError('搜尋結果已過期；請重新搜尋並選擇整合包版本。')
        if project['project_type']!='modpack':raise UserError('所選項目不是整合包。')
        file=next((item for item in selected['files'] if item.get('primary')),selected['files'][0])
        if Path(file['filename']).suffix.lower()!='.mrpack':raise UserError('所選檔案不是 .mrpack 整合包；請開啟專案頁面手動下載。')
        target=self._unique_file(self._downloads_directory(),file['filename']);net=Network(self.cancel,lambda msg:self.progress(msg))
        self.progress('正在下載並校驗整合包…',0,1)
        try:self._verified_download(file,target,net,1536*1024*1024)
        except (requests.RequestException,UserError) as exc:
            if isinstance(exc,Cancelled):raise
            raise UserError('整合包官方檔案與 MCIM 備援均未能提供有效檔案；未覆蓋既有資料。請手動開啟 https://modrinth.com/modpack/'+project['slug']+' 下載。') from exc
        self.progress('整合包已下載並通過 SHA 校驗。',1,1)
        remember_download(self.root,target)
        return f'{project["title"]} 已下載至：{target}'
    def import_modpack(self,payload):
        project_id=payload.get('project_id');version_id=payload.get('version_id')
        project=self.mod_projects.get(project_id) if isinstance(project_id,str) else None
        selected=self.mod_versions.get(version_id) if isinstance(version_id,str) else None
        if not project or not selected or selected['project_id']!=project_id:raise UserError('搜尋結果已過期；請重新搜尋並選擇整合包版本。')
        if project['project_type']!='modpack':raise UserError('所選項目不是整合包。')
        file=next((item for item in selected['files'] if item.get('primary')),selected['files'][0])
        if Path(file['filename']).suffix.lower()!='.mrpack':raise UserError('目前一鍵匯入只支援 Modrinth .mrpack；請改存到 Downloads 再用原平台匯入。')
        net=Network(self.cancel,lambda msg:self.progress(msg));temp_root=self.root/'tmp';temp_root.mkdir(parents=True,exist_ok=True)
        if temp_root.is_symlink():raise UserError('暫存目錄路徑不安全。')
        archive=inside(temp_root,'modpack-'+uuid.uuid4().hex+'.mrpack');stage_id='pack-stage-'+uuid.uuid4().hex[:12]
        stage=inside(self.root/'instances',stage_id);final_id=''
        try:
            self.progress('正在下載並校驗整合包…',0,1)
            try:self._verified_download(file,archive,net,1536*1024*1024)
            except (requests.RequestException,UserError) as exc:
                if isinstance(exc,Cancelled):raise
                raise UserError('整合包官方檔案與 MCIM 備援均未能提供有效檔案；未建立實例。請手動開啟 https://modrinth.com/modpack/'+project['slug']+' 下載。') from exc
            with zipfile.ZipFile(archive) as pack:
                entries=pack.infolist()
                if len(entries)>30000 or sum(item.file_size for item in entries)>2*1024*1024*1024:
                    raise UserError('整合包超過安全檔案數或解壓大小上限。')
                index=next((item for item in entries if item.filename=='modrinth.index.json'),None)
                if index is None or index.file_size>8*1024*1024:raise UserError('整合包缺少可讀的 modrinth.index.json。')
                index_data=json.loads(pack.read(index).decode('utf-8'))
                if not isinstance(index_data,dict) or index_data.get('formatVersion')!=1 or index_data.get('game')!='minecraft':
                    raise UserError('不支援這個 Modrinth 整合包格式。')
                dependencies=index_data.get('dependencies')
                if not isinstance(dependencies,dict):raise UserError('整合包缺少版本需求。')
                game_version=dependencies.get('minecraft')
                if not isinstance(game_version,str) or not supported(game_version):raise UserError('整合包 Minecraft 版本不合法。')
                supported_pack_loaders=('fabric-loader','forge','neoforge','quilt-loader')
                pack_loaders=[name for name in dependencies if name!='minecraft']
                if any(name not in supported_pack_loaders for name in pack_loaders) or len(pack_loaders)>1:
                    raise UserError('這個整合包使用 Forge、NeoForge 或 Quilt；目前一鍵匯入只支援原版與 Fabric。請選「下載到 Downloads」並使用相應啟動器匯入。')
                if pack_loaders==['fabric-loader']:
                    loader='fabric';fabric_version=ident(dependencies['fabric-loader'])
                elif not pack_loaders:loader='vanilla';fabric_version=None
                else:raise UserError('這個整合包使用 Forge、NeoForge 或 Quilt；目前一鍵匯入只支援原版與 Fabric。請選「下載到 Downloads」並使用相應啟動器匯入。')
                files=index_data.get('files')
                if not isinstance(files,list) or len(files)>20000:raise UserError('整合包檔案清單不合法或超過安全上限。')
                overrides=[];required=[];seen=set();total=0
                for entry in entries:
                    path=entry.filename
                    if not (path.startswith('overrides/') or path.startswith('client-overrides/')) or entry.is_dir():continue
                    relative=path.split('/',1)[1]
                    relative=safe_archive_path(relative)
                    if PurePosixPath(relative).parts[0] in ('instance.json','launch.json','natives'):
                        raise UserError('整合包嘗試覆蓋啟動器管理檔案，為保護遊戲已停止匯入。')
                    if entry.external_attr>>16 and stat.S_ISLNK(entry.external_attr>>16):
                        raise UserError('整合包覆蓋檔包含符號連結。')
                    total+=entry.file_size
                    if total>1024*1024*1024:raise UserError('整合包覆蓋檔解壓後超過 1 GB 安全上限。')
                    overrides.append((entry,relative))
                total_download=0
                for entry in files:
                    if not isinstance(entry,dict):raise UserError('整合包檔案資料不完整。')
                    env=entry.get('env') if isinstance(entry.get('env'),dict) else {}
                    if env.get('client')=='unsupported' or env.get('client')=='optional':continue
                    relative=safe_archive_path(entry.get('path'))
                    if PurePosixPath(relative).parts[0] in ('instance.json','launch.json','natives'):
                        raise UserError('整合包嘗試覆蓋啟動器管理檔案，為保護遊戲已停止匯入。')
                    if relative in seen:raise UserError('整合包含重複安裝路徑，為避免覆蓋已停止。')
                    seen.add(relative)
                    downloads=entry.get('downloads');hashes=entry.get('hashes');size=entry.get('fileSize')
                    if not isinstance(downloads,list) or not downloads or not isinstance(hashes,dict) or type(size) is not int or size<0:
                        raise UserError('整合包中有檔案缺少下載位址、雜湊或大小。')
                    total_download+=size
                    if total_download>1024*1024*1024:raise UserError('整合包必要檔案總大小超過 1 GB 安全上限。')
                    url=downloads[0]
                    if not isinstance(url,str):raise UserError('整合包檔案下載位址不合法。')
                    safe_file={'url':url,'hashes':hashes,'size':size,'filename':Path(relative).name}
                    # Modrinth packs may use non-Modrinth URLs. Keep the network boundary
                    # explicit: only the publisher CDN and its documented mirror are trusted.
                    if not modrinth_file_mirror(url):
                        raise UserError('整合包包含非 Modrinth CDN 的第三方檔案，為保護安全未自動下載。請先選「下載到 Downloads」並使用原平台匯入。')
                    required.append((relative,safe_file))
                self.progress('正在準備獨立整合包實例…')
                # Install into a unique staging instance; it is only made visible after
                # every override and required file is extracted and verified.
                self.install({'version':game_version,'loader':loader,'fabric_version':fabric_version},staging_id=stage_id)
                for entry,relative in overrides:
                    target=inside(stage,relative);target.parent.mkdir(parents=True,exist_ok=True)
                    if target.is_symlink():raise UserError('整合包覆蓋路徑包含符號連結。')
                    with pack.open(entry) as src,target.open('wb') as dst:shutil.copyfileobj(src,dst)
                for index_file,(relative,safe_file) in enumerate(required,1):
                    if self.cancel.is_set():raise Cancelled('已取消整合包匯入；暫存實例已清理。')
                    target=inside(stage,relative);target.parent.mkdir(parents=True,exist_ok=True)
                    self.progress(f'正在下載／校驗整合包檔案 {index_file}/{len(required)}…',index_file-1,len(required))
                    try:self._verified_download(safe_file,target,net,512*1024*1024)
                    except (requests.RequestException,UserError) as exc:
                        if isinstance(exc,Cancelled):raise
                        raise UserError('整合包檔案無法從官方來源及 MCIM 備援下載並校驗；暫存實例會清除。請手動開啟 https://modrinth.com/modpack/'+project['slug']+' 或稍後重試。') from exc
                if self.cancel.is_set():raise Cancelled('已取消整合包匯入；暫存實例已清理。')
                title=str(index_data.get('name') or project['title'])[:100]
                slug=re.sub(r'[^a-z0-9]+','-',title.lower()).strip('-')[:32] or 'modpack'
                final_id=ident(f'pack-{slug}-{game_version}-{uuid.uuid4().hex[:8]}')
                final=inside(self.root/'instances',final_id)
                if final.exists() or final.is_symlink():raise UserError('建立整合包實例時發生名稱衝突，請重試。')
                record=read_json(stage/'instance.json');record.update(id=final_id,modpack_name=title,modpack_project=project['slug'])
                atomic_json(stage/'instance.json',record)
                stage.rename(final)
                self.progress('整合包已匯入並完成檔案校驗。',len(required),len(required))
                return f'{title} 已安裝為獨立實例「{final_id}」，使用 Minecraft {game_version}。'
        except (zipfile.BadZipFile,json.JSONDecodeError,UnicodeDecodeError,OSError) as exc:
            if isinstance(exc,UserError):raise
            raise UserError('整合包無法安全讀取或寫入；未建立可見的半成品實例。') from exc
        finally:
            archive.unlink(missing_ok=True)
            if stage.exists():shutil.rmtree(stage,ignore_errors=True)
    def start(self, action, payload):
        with self.lock:
            self.state()
            if self.java_accounts.changing: raise UserError('正在更新皮膚站帳號，請稍候。')
            if self.closing: raise UserError('啟動器正在結束，請重新開啟 App。')
            if self.job['status']=='running': raise UserError('已有工作正在進行，請等候或取消。')
            if self.process and action not in ('refresh','diagnostics'): raise UserError('遊戲仍在執行；請先儲存世界並正常離開遊戲。')
            functions={'refresh':self.refresh,'scan':self.scan,'install':self.install,'repair':self.repair,'launch':self.launch,'backup':self.backup,'diagnostics':self.diagnostics,'delete':self.delete_instance,
                       'mod-search':self.mod_search,'mod-versions':self.mod_versions_for_project,
                       'mod-download':self.download_mod,'modpack-download':self.download_modpack,
                       'modpack-import':self.import_modpack}
            functions.update(getattr(self,'bedrock_actions',{}))
            if action not in functions: raise UserError('未知操作。')
            self.cancel=threading.Event(); self.job={'status':'running','action':action,'message':'開始處理…','done':0,'total':0,'result':None}
            def run():
                try:
                    result=functions[action](payload)
                    # A committed launch or backup is successful even if cancel arrives just afterward.
                    with self.lock: self.job.update(status='done',message='已完成',result=result)
                except Cancelled as exc:
                    with self.lock: self.job.update(status='cancelled',message=str(exc))
                except Exception as exc:
                    with (self.logs/'helper.log').open('a',encoding='utf-8') as f: traceback.print_exc(file=f)
                    msg=str(exc) if isinstance(exc,UserError) else ('網絡連線失敗。檢查網絡後重試；已完成的檔案會保留。' if isinstance(exc,requests.RequestException) else '操作失敗。請查看日誌或匯出診斷包。')
                    with self.lock: self.job.update(status='error',message=msg)
            threading.Thread(target=run,daemon=True).start()
    def refresh(self,payload):
        self.progress('正在取得官方版本清單…')
        data=Network(self.cancel,lambda msg:self.progress(msg)).json(MANIFEST_URL)
        if not isinstance(data,dict) or not isinstance(data.get('versions'),list): raise UserError('版本伺服器回傳資料不完整。')
        # Keep the last known-good catalog if a proxy or server returns only one family.
        versions=[];seen=set()
        for item in data['versions']:
            if not isinstance(item,dict) or item.get('type') not in VERSION_TYPES or not supported(item.get('id','')):continue
            if item['id'] in seen:continue
            seen.add(item['id']);versions.append(item)
        counts={kind:sum(v.get('type')==kind for v in versions) for kind in VERSION_TYPES}
        missing=[kind for kind,count in counts.items() if count==0]
        if missing:
            labels={'release':'正式版','snapshot':'快照／愚人節','old_beta':'Beta','old_alpha':'Alpha'}
            absent='、'.join(labels[x] for x in missing)
            raise UserError(f'收到的官方版本清單不完整，缺少{absent}；已保留舊清單，請稍後再更新。')
        short=[kind for kind,count in counts.items() if count<MIN_VERSION_COUNTS[kind]]
        if short:
            labels={'release':'正式版','snapshot':'快照／愚人節','old_beta':'Beta','old_alpha':'Alpha'}
            summary='、'.join(f'{labels[kind]} {counts[kind]}/{MIN_VERSION_COUNTS[kind]}' for kind in short)
            raise UserError(f'收到的官方版本清單疑似遭截斷（{summary}）；已保留舊清單，請稍後再更新。')
        data['versions']=versions
        for v in versions: ident(v['id'])
        atomic_json(self.root/'catalog.json',data)
        with self.lock: self.catalog=data['versions']
        self.scan_time=0;self.scan_external(force=True)
        return (f'版本清單已更新：正式版 {counts["release"]}、快照／愚人節 {counts["snapshot"]}、'
                f'Beta {counts["old_beta"]}、Alpha {counts["old_alpha"]}；另找到 {len(self.discovered)} 個本機版本。')
    def scan(self,payload):
        self.scan_time=0
        found=self.scan_external(force=True)
        return f'重新掃描完成：找到 {len(found)} 個本機版本。'
    def metadata(self,version,net):
        ident(version)
        item=next((v for v in self.catalog if v['id']==version and v.get('type') in ('release','snapshot','old_beta','old_alpha')),None)
        if not item or not supported(version): raise UserError('請先更新版本清單，再選擇正式版、快照或舊版本。')
        path=self.game/'versions'/version/(version+'.json')
        net.download(item['url'],path,item['sha1'])
        data=read_json(path)
        if data.get('id')!=version or not isinstance(data.get('mainClass'),str) or not ('arguments' in data or 'minecraftArguments' in data): raise UserError('版本啟動資料不受支援。')
        return data
    def batch(self,entries,net,label):
        # Deduplicate shared assets; 6 workers keeps disk/network pressure bounded.
        entries=list({str(p):(d,p) for d,p in entries}.values()); self.progress(label,0,len(entries))
        def one(item):
            d,p=item; net.download(d['url'],p,d.get('sha1'),d.get('size'))
        with futures.ThreadPoolExecutor(max_workers=6) as pool:
            pending=[pool.submit(one,x) for x in entries]
            try:
                for n,f in enumerate(futures.as_completed(pending),1):
                    f.result(); net.check(); self.progress(done=n)
            except Exception:
                self.cancel.set()
                for f in pending: f.cancel()
                raise
    def install_arm64_java8(self,net):
        """Install a pinned Apple Silicon Java 8 runtime, switching publishers on failure."""
        if host_os()!='osx' or host_arch()!='aarch64':
            raise UserError('Apple Silicon Java 8 相容 runtime 只適用於 macOS ARM64。')
        self.java_root.mkdir(parents=True,exist_ok=True)
        if not os.access(self.java_root,os.W_OK):
            raise UserError(f'Java 安裝位置無法寫入：{self.java_root}。請選擇可寫入的資料夾。')
        for component in (self.java_root/'mac-os-arm64',self.java_root/'mac-os-arm64'/'java8-arm64',self.java_root/'.downloads'):
            if component.is_symlink():raise UserError('Java 安裝目錄包含符號連結；為保護資料已停止安裝。')
        base=inside(self.java_root,'mac-os-arm64/java8-arm64')
        claim_new_tree(self.root,base)
        if base.is_symlink():raise UserError('Java 安裝路徑為符號連結；為保護資料已停止安裝。')
        candidates=sorted(base.rglob('Contents/Home/bin/java'))+sorted(base.rglob('bin/java')) if base.is_dir() else []
        for candidate in candidates:
            if java_file_arch(candidate)!='aarch64':continue
            info=java_info(candidate)
            if info and info[0]==8 and info[1]=='aarch64':
                self.java_source='managed'
                return candidate
        archive=inside(self.java_root,'.downloads/apple-silicon-java8.archive')
        sources=[('Azul Zulu',ARM64_LEGACY_JAVA_URL,{'cdn.azul.com'},ARM64_LEGACY_JAVA_SHA256,ARM64_LEGACY_JAVA_SIZE,'zip')]
        sources.extend(('Amazon Corretto',url,{'corretto.aws','github.com','release-assets.githubusercontent.com','objects.githubusercontent.com'},ARM64_LEGACY_CORRETTO_SHA256,None,'tar') for url in ARM64_LEGACY_CORRETTO_URLS)
        source_error=None;archive_kind=None
        for source_name,url,hosts,digest,size,kind in sources:
            try:
                self.progress(f'正在下載並校驗 Apple Silicon Java 8（{source_name}）…')
                net.download(url,archive,size=size,sha256_digest=digest,extra_hosts=hosts,
                             max_bytes=256*1024*1024,retries=1)
                archive_kind=kind;break
            except Cancelled:raise
            except (UserError,requests.RequestException) as exc:
                source_error=exc;archive.unlink(missing_ok=True)
        if archive_kind is None:
            raise UserError(f'無法從可用來源取得相容的 Apple Silicon Java 8，下載檔案未通過大小或 SHA-256 驗證。最後錯誤：{source_error}')
        staging=base.with_name(base.name+'.staging-'+uuid.uuid4().hex)
        backup=base.with_name(base.name+'.replaced-'+uuid.uuid4().hex)
        try:
            if archive_kind=='zip':extract_zip_safely(archive,staging,max_unpacked=1536*1024*1024)
            else:extract_tar_gz_safely(archive,staging)
            candidates=sorted(staging.rglob('Contents/Home/bin/java'))+sorted(staging.rglob('bin/java'))
            java=None
            for candidate in candidates:
                if java_file_arch(candidate)!='aarch64':continue
                info=java_info(candidate)
                if info and info[0]==8 and info[1]=='aarch64':java=candidate;break
            if java is None:raise UserError('下載的 Java 8 無法在 Apple Silicon 執行，已停止安裝。')
            relative=java.relative_to(staging)
            base.parent.mkdir(parents=True,exist_ok=True)
            if base.exists():os.replace(base,backup)
            try:os.replace(staging,base)
            except Exception:
                if backup.exists() and not base.exists():os.replace(backup,base)
                raise
            if backup.exists():shutil.rmtree(backup)
            installed=base/relative
            self.java_source='managed'
            archive.unlink(missing_ok=True)
            return installed
        except Exception:
            if staging.exists():shutil.rmtree(staging,ignore_errors=True)
            if backup.exists() and not base.exists():os.replace(backup,base)
            raise
    def prepare_arm64_lwjgl2(self,data,game,net):
        """Fetch fixed, checksummed Apple Silicon LWJGL files without editing metadata."""
        if not use_arm64_legacy_lwjgl2(data):
            raise UserError('Apple Silicon LWJGL 2 相容層不適用於這個版本或電腦。')
        validate_arm64_objc_bridge(Path(__file__).resolve().parent/ARM64_OBJC_BRIDGE_JAR['path'])
        root=Path(game)/'libraries'
        lwjgl=inside(root,ARM64_LWJGL_JAR['path'])
        lwjgl_util=inside(root,ARM64_LWJGL_UTIL_JAR['path'])
        native=inside(root,ARM64_LWJGL_NATIVE['path'])
        downloads=(
            ('LWJGL Java library',ARM64_LWJGL_JAR,lwjgl,{}),
            ('LWJGL utility library',ARM64_LWJGL_UTIL_JAR,lwjgl_util,{}),
            ('ARM64 native library',ARM64_LWJGL_NATIVE,native,{
                'sha256_digest':ARM64_LWJGL_NATIVE['sha256'],
                'extra_hosts':{'github.com','release-assets.githubusercontent.com','objects.githubusercontent.com',
                               'gh-proxy.com','ghproxy.net','ghfast.top'},
                'fallback_urls':ARM64_LWJGL_NATIVE_MIRRORS,
            }),
        )
        for label,item,path,options in downloads:
            try:net.download(item['url'],path,item['sha1'],item['size'],**options)
            except Cancelled:raise
            except (UserError,requests.RequestException) as exc:
                raise UserError(f'Apple Silicon 舊版視窗元件（{label}）下載失敗；已保留已校驗檔案，請重試。詳細原因：{exc}') from exc
        if not zipfile.is_zipfile(lwjgl) or not zipfile.is_zipfile(lwjgl_util):
            raise UserError('Apple Silicon LWJGL Java 函式庫損壞，請按「檢查及修復」重試。')
        validate_arm64_lwjgl_native(native)
        classpath=arm64_lwjgl2_classpath(data,game)
        return classpath,native
    def runtime(self,data,net):
        self.java_source=None
        comp=ident(data['javaVersion']['component']); major=data['javaVersion']['majorVersion']
        if needs_intel_java8(major,data) and not rosetta_installed():raise UserError(rosetta_message())
        self.progress(f'正在尋找可用的本機 Java {major}…')
        local=self.find_existing_java(major,[self.java_root,self.root,self.game,*self.root_candidates()],strict=False,data=data)
        if local:
            info=java_info(local)
            self.java_source='local'
            self.progress(f'找到本機 Java {info[0]}，直接使用：{local}')
            return local
        if use_arm64_legacy_lwjgl2(data):
            return self.install_arm64_java8(net)
        if self.java_root==self.recommended_java_root:
            self.java_root.mkdir(parents=True,exist_ok=True)
        if not self.java_root.is_dir():raise UserError(f'Java 安裝位置不存在或目前無法使用：{self.java_root}。請重新連接磁碟或在「玩家與設定」選擇其他位置。')
        if not os.access(self.java_root,os.W_OK):raise UserError(f'Java 安裝位置無法寫入：{self.java_root}。請選擇可寫入的資料夾。')
        key='mac-os-arm64' if host_arch()=='aarch64' else 'mac-os'
        if host_os()!='osx': key='linux' # Linux is for automated core checks, not a distributed platform claim.
        all_data=net.json(RUNTIME_URL)
        # Mojang publishes no Java 8 runtime for Apple Silicon. Its official Intel
        # macOS Java 8 build runs old Minecraft's Intel natives through Rosetta.
        if needs_intel_java8(major,data):
            key='mac-os';comp='jre-legacy'
        choices=all_data.get(key,{}).get(comp,[])
        if not choices:
            fallback=RUNTIME_COMPONENT_BY_MAJOR.get(major)
            if fallback and fallback!=comp:
                comp=fallback;choices=all_data.get(key,{}).get(comp,[])
        if not choices:raise UserError(f'官方未提供此機型可執行的 Java {major} runtime（{comp}）。請稍後重試或查看診斷包。')
        desc=choices[0]['manifest']; base=self.java_root/key/comp
        claim_new_tree(self.root,base)
        meta=self.root/'runtime-manifests'/(key+'-'+comp+'.json')
        net.download(desc['url'],meta,desc.get('sha1'),desc.get('size'))
        manifest=read_json(meta); entries=[]; links=[]
        for name,item in manifest['files'].items():
            path=inside(base,name)
            if item['type']=='directory': path.mkdir(parents=True,exist_ok=True)
            elif item['type']=='file': entries.append((item['downloads']['raw'],path))
            elif item['type']=='link': links.append((path,item['target']))
        self.batch(entries,net,'正在安裝／校驗 Java…')
        for name,item in manifest['files'].items():
            if item['type']=='file' and item.get('executable'): inside(base,name).chmod(0o755)
        for path,target in links:
            if Path(target).is_absolute() or not (path.parent/target).resolve().is_relative_to(base.resolve()): raise UserError('Java 連結路徑超出安裝範圍。')
            path.parent.mkdir(parents=True,exist_ok=True)
            if not path.is_symlink():
                if path.exists(): raise UserError('Java 安裝路徑衝突。')
                path.symlink_to(target)
        candidates=[base/'jre.bundle/Contents/Home/bin/java',base/'bin/java']
        for candidate in candidates:
            info=java_info(candidate) if candidate.is_file() else None
            if info and java_compatible(major,info[0]) and java_arch_compatible(major,info[1],data):
                self.java_source='managed'
                return candidate
        raise UserError(f'Java {major} 無法在這台電腦執行。請檢查 macOS 版本及機型；詳情見診斷包。')
    def java_candidates(self, roots, required=None):
        found=[]; seen=set()
        def add(p):
            try:
                p=Path(p).expanduser()
                if not p.is_file() or not os.access(p,os.X_OK):return
                p=p.resolve(strict=True)
                key=str(p)
                if key not in seen:seen.add(key);found.append(p)
            except OSError:pass
        # Explicit Java install/search location takes precedence over environment
        # variables and system launch stubs when a compatible JDK is present.
        for root in roots[:2]:
            root=Path(root).expanduser()
            for relative in ('bin/java','Contents/Home/bin/java','jre.bundle/Contents/Home/bin/java',
                             '*/bin/java','*/Contents/Home/bin/java','*/jre.bundle/Contents/Home/bin/java',
                             '*/*/bin/java','*/*/Contents/Home/bin/java','*/*/jre.bundle/Contents/Home/bin/java'):
                for candidate in sorted(root.glob(relative))[:100]:add(candidate)
        for variable in ('JAVA_HOME','JDK_HOME','JRE_HOME'):
            value=os.environ.get(variable)
            if value:
                home=Path(value).expanduser()
                add(home if home.name in ('java','java.exe') else home/'bin/java')
        path_java=shutil.which('java')
        # macOS /usr/bin/java is only an installer stub on systems without a JDK.
        if path_java and not (host_os()=='osx' and Path(path_java)==Path('/usr/bin/java')):add(path_java)
        for root in roots:
            root=Path(root).expanduser()
            for folder in ('runtime','runtimes'):
                base=root/folder
                if base.is_dir():
                    # Search only launcher-managed runtime folders, never the whole disk.
                    for pattern in ('*/bin/java','*/jre.bundle/Contents/Home/bin/java',
                                    '*/*/bin/java','*/*/jre.bundle/Contents/Home/bin/java',
                                    '*/*/*/bin/java','*/*/*/jre.bundle/Contents/Home/bin/java',
                                    '*/*/*/*/bin/java'):
                        for candidate in sorted(base.glob(pattern))[:200]:add(candidate)
        # PrismLauncher and MultiMC keep managed Java installs beside their instances.
        app=Path.home()/'Library/Application Support'
        for base in (app/'PrismLauncher/java',app/'MultiMC/java',app/'PolyMC/java',app/'ATLauncher/java'):
            for pattern in ('*/bin/java','*/*/bin/java','*/*/Contents/Home/bin/java','*/*/*/Contents/Home/bin/java'):
                for candidate in sorted(base.glob(pattern))[:200]:add(candidate)
        # Common package-manager and version-manager locations are not always on Finder's PATH.
        for base in (Path('/opt/homebrew/opt'),Path('/usr/local/opt')):
            for pattern in ('openjdk*/bin/java','openjdk*/libexec/openjdk.jdk/Contents/Home/bin/java'):
                for candidate in sorted(base.glob(pattern))[:40]:add(candidate)
        for base in (Path.home()/'.sdkman/candidates/java',Path.home()/'.asdf/installs/java'):
            for candidate in sorted(base.glob('*/bin/java'))[:100]:add(candidate)
        for candidate in sorted(Path('/usr/lib/jvm').glob('*/bin/java'))[:100]:add(candidate)
        for base in (Path('/Library/Java/JavaVirtualMachines'),Path.home()/'Library/Java/JavaVirtualMachines'):
            try:
                for bundle in sorted(base.iterdir()):add(bundle/'Contents/Home/bin/java')
            except OSError:pass
        majors=tuple(dict.fromkeys((required,8,11,16,17,21,25)))
        for major in majors:
            if not isinstance(major,int):continue
            try:
                if host_os()=='osx':
                    r=subprocess.run(['/usr/libexec/java_home','-v',str(major)],capture_output=True,text=True,timeout=3)
                    if r.returncode==0:add(Path(r.stdout.strip())/'bin/java')
            except (OSError,subprocess.TimeoutExpired):pass
        return found
    def find_existing_java(self,required,roots,strict=True,data=None):
        if needs_intel_java8(required,data) and not rosetta_installed():
            if strict:raise UserError(rosetta_message())
            return None
        for candidate in self.java_candidates(roots,required):
            if use_arm64_legacy_lwjgl2(data) and java_file_arch(candidate)!='aarch64':continue
            info=java_info(candidate)
            if not info or not java_compatible(required,info[0]) or not java_arch_compatible(required,info[1],data):continue
            return candidate
        if strict:raise UserError(f'這個版本需要 Java {required}。已檢查 JAVA_HOME、系統 Java、常見 JDK 安裝位置及其他啟動器的 Java，仍找不到相容版本。')
        return None
    def external_instance(self,instance_id):
        matches=self.scan_external(force=True)
        record=matches.get(instance_id)
        if not record:raise UserError('找不到這個外部 Minecraft 安裝。請重新掃描資料夾。')
        root=Path(record['sourceRoot']).resolve(strict=True)
        return root,record
    def install(self,payload,staging_id=None):
        version=ident(payload.get('version')); loader=payload.get('loader','vanilla')
        if loader not in ('vanilla','fabric'): raise UserError('不支援的遊戲類型。')
        if shutil.disk_usage(self.root).free < 2*2**30: raise UserError('可用空間少於 2 GB，請先清理磁碟。')
        net=Network(self.cancel,lambda msg:self.progress(msg))
        if not self.catalog: self.refresh({})
        self.progress('讀取版本資料…',0,0); data=self.metadata(version,net)
        fabric_version=payload.get('fabric_version')
        if loader=='fabric':
            if not isinstance(data.get('arguments'),dict):raise UserError('此經典版本不支援 Fabric 安裝；請選 Vanilla。')
            if not fabric_version:
                loaders=net.json('https://meta.fabricmc.net/v2/versions/loader/'+version)
                stable=next((x for x in loaders if x['loader'].get('stable')),None)
                if not stable: raise UserError('Fabric 暫未提供此版本的穩定 Loader。')
                fabric_version=stable['loader']['version']
            ident(fabric_version)
            profile=net.json(f'https://meta.fabricmc.net/v2/versions/loader/{version}/{fabric_version}/profile/json')
            if profile.get('inheritsFrom')!=version: raise UserError('Fabric 版本資料不相符。')
            data=json.loads(json.dumps(data)); data['jar']=version; data['id']=ident(profile['id']); data['mainClass']=profile['mainClass']
            replace_names={':'.join(x['name'].split(':')[:2]) for x in profile['libraries']}
            data['libraries']=[x for x in data['libraries'] if ':'.join(x['name'].split(':')[:2]) not in replace_names]+profile['libraries']
            for k in ('jvm','game'): data['arguments'][k]+=profile.get('arguments',{}).get(k,[])
        instance_id=ident(staging_id or (('fabric-'+fabric_version+'-' if loader=='fabric' else 'vanilla-')+version))
        folder=inside(self.root/'instances',instance_id)
        if staging_id and (folder.exists() or folder.is_symlink()):raise UserError('整合包暫存實例名稱衝突，請重試。')
        folder.mkdir(parents=True,exist_ok=True)
        # Never rewrite an existing ready instance until all downloads and Java verification succeed.
        major=java_major_for(data,version)
        runtime_data=data
        if not data.get('javaVersion'):
            runtime_data=dict(data);runtime_data['javaVersion']={'component':'jre-legacy','majorVersion':major}
        java=self.runtime(runtime_data,net)
        java_source=self.java_source
        entries,cp,natives=library_plan(data,self.game)
        entries.append((data['downloads']['client'],self.game/'versions'/version/(version+'.jar')))
        logging=data.get('logging',{}).get('client')
        if logging: entries.append((logging['file'],inside(self.game/'assets/log_configs',logging['file']['id'])))
        label='正在下載／校驗遊戲與函式庫…'
        if java_source=='local':label+=f'（沿用本機 Java {major}）'
        self.batch(entries,net,label)
        if use_arm64_legacy_lwjgl2(data):
            self.progress('正在準備 Apple Silicon 舊版視窗相容元件…')
            self.prepare_arm64_lwjgl2(data,self.game,net)
        # Fabric metadata lacks hashes for some Maven files; validate JAR structure as well.
        for path in cp:
            if not zipfile.is_zipfile(path): raise UserError('函式庫檔案損壞，請重試修復。')
        index=data['assetIndex']; indexpath=inside(self.game/'assets/indexes',ident(index['id'])+'.json')
        net.download(index['url'],indexpath,index['sha1'],index.get('size'))
        objects=read_json(indexpath)['objects']; assets=[]
        for obj in objects.values():
            h=obj['hash']
            if not re.fullmatch('[0-9a-f]{40}',h): raise UserError('素材雜湊格式錯誤。')
            assets.append(({'url':f'https://resources.download.minecraft.net/{h[:2]}/{h}','sha1':h,'size':obj['size']},self.game/'assets/objects'/h[:2]/h))
        self.batch(assets,net,'正在下載／校驗聲音與素材…')
        (folder/'natives').mkdir(exist_ok=True)
        for archive,exclude in natives: net.check(); extract_native(archive,folder/'natives',exclude)
        (folder/'mods').mkdir(exist_ok=True); (folder/'saves').mkdir(exist_ok=True)
        net.check()
        try:java_record=str(java.resolve().relative_to(self.root))
        except ValueError:java_record=str(java.resolve())
        record={'id':instance_id,'version':version,'loader':loader,'fabric_version':fabric_version,'managed':True,'java':java_record, 'java_major':major,'created':time.strftime('%Y-%m-%d %H:%M:%S')}
        atomic_json(folder/'launch.json',data); atomic_json(folder/'instance.json',record)
        java_label=f'沿用本機 Java {major}' if java_source=='local' else f'使用 MambaCraft 管理的 Java {major}'
        return f'{instance_id} 安裝完成，可以開始遊戲。{java_label}。'
    def get_instance(self,payload):
        value=ident(payload.get('id'))
        if value.startswith('import-'):
            return self.external_instance(value)
        folder=inside(self.root/'instances',value)
        try:record=read_json(folder/'instance.json')
        except (OSError,ValueError):raise UserError('找不到完整安裝的實例，請先安裝。')
        record.setdefault('managed',True)
        return folder,record
    def launch_check(self,payload):
        """Read-only preflight used to ask before installing Java for an external game."""
        folder,record=self.get_instance(payload)
        if record.get('managed',True):return {'needsInstall':False}
        version=ident(record.get('version'))
        manifest=inside(folder,'versions/'+version+'/'+version+'.json')
        if not manifest.is_file():raise UserError('原啟動器的版本資料已移動。請重新掃描資料夾。')
        data=read_json(manifest);required=record.get('java_major') or java_major_for(data,version)
        roots=[folder,self.java_root,self.root,self.game,*self.root_candidates()]
        java=self.find_existing_java(required,roots,strict=False,data=data)
        return {'needsInstall':java is None,'javaMajor':required,'version':version}
    def repair(self,payload):
        _,record=self.get_instance(payload)
        if not record.get('managed',True):raise UserError('這是另一個啟動器管理的版本。為保護原有檔案，請用該啟動器修復；也可在 MambaCraft 安裝相同版本。')
        return self.install(record)
    def _cache_file(self,base,relative):
        """Resolve a metadata path only when every existing component is a real file/dir."""
        try:
            base=Path(base)
            if base.is_symlink():return None
            path=inside(base,relative)
            parts=PurePosixPath(relative).parts; current=base
            for part in parts:
                current=current/part
                if current.is_symlink():return None
            if not path.is_relative_to(base.resolve()):return None
            return path
        except (OSError,TypeError,ValueError,UserError):return None
    def delete_instance(self,payload):
        value=ident(payload.get('id'))
        if value.startswith('import-'):raise UserError('外部版本由原啟動器管理，MambaCraft 不會刪除外部遊戲資料。')
        with self.lock:
            if self.running==value or self.process and self.process.poll() is None:raise UserError('遊戲仍在執行；請正常退出後再刪除。')
        instances=self.root/'instances';folder=instances/value
        try:
            if instances.is_symlink() or folder.is_symlink():raise UserError('拒絕刪除包含符號連結的實例路徑。')
            base=instances.resolve(strict=True);resolved=folder.resolve(strict=True)
            if resolved.parent!=base or not resolved.is_dir():raise UserError('實例路徑不在 MambaCraft 管理範圍內。')
            record=read_json(resolved/'instance.json')
            if not isinstance(record,dict) or record.get('id')!=value:raise UserError('實例資料與資料夾不符，為保護資料已停止刪除。')
            launch=read_json(resolved/'launch.json')
            if not isinstance(launch,dict):raise UserError('實例版本資料不完整，無法安全清理。')
        except UserError:raise
        except (OSError,ValueError,TypeError):raise UserError('找不到完整的 MambaCraft 實例，未刪除任何資料。')
        deleted_base=ident(launch.get('jar',launch.get('id',record.get('version',value))))
        deleted_index=launch.get('assetIndex',{}).get('id') if isinstance(launch.get('assetIndex'),dict) else None
        deleted_libraries=[];deleted_objects=[];references=[];safe_cache=True
        def library_files(data):
            files=[]
            try:entries=library_plan(data,self.game)[0]
            except (KeyError,TypeError,ValueError,UserError):return None
            for item,_ in entries:
                relative=item.get('path')
                if not isinstance(relative,str):return None
                path=self._cache_file(self.game/'libraries',relative)
                if path is None:return None
                files.append(path)
            return files
        deleted_libraries=library_files(launch)
        if deleted_libraries is None:safe_cache=False
        for other in self.managed_instances():
            if other['id']==value:continue
            try:
                other_folder=inside(instances,other['id']);data=read_json(other_folder/'launch.json')
                base_id=ident(data.get('jar',data.get('id',other.get('version',other['id']))))
                libs=library_files(data)
                index_id=data.get('assetIndex',{}).get('id') if isinstance(data.get('assetIndex'),dict) else None
                if libs is None:safe_cache=False;libs=[]
                references.append((base_id,libs,index_id))
            except (OSError,ValueError,TypeError,UserError):safe_cache=False
        index_path=None
        if isinstance(deleted_index,str) and ID_RE.fullmatch(deleted_index):
            index_path=self._cache_file(self.game/'assets'/'indexes',deleted_index+'.json')
            if index_path and index_path.is_file():
                try:
                    objects=read_json(index_path).get('objects',{})
                    if not isinstance(objects,dict):safe_cache=False
                    else:
                        for item in objects.values():
                            h=item.get('hash') if isinstance(item,dict) else None
                            if not isinstance(h,str) or not re.fullmatch('[0-9a-f]{40}',h):safe_cache=False;continue
                            p=self._cache_file(self.game/'assets'/'objects',h[:2]+'/'+h)
                            if p is None:safe_cache=False
                            else:deleted_objects.append(p)
                except (OSError,ValueError,AttributeError):safe_cache=False
        shutil.rmtree(resolved)
        if safe_cache:
            used_bases={base for base,_,_ in references}
            if deleted_base not in used_bases:
                versions=self.game/'versions';candidate=versions/deleted_base
                try:
                    if not versions.is_symlink() and not candidate.is_symlink() and candidate.resolve(strict=True).parent==versions.resolve(strict=True):shutil.rmtree(candidate)
                except OSError:pass
            used_libraries={p for _,files,_ in references for p in files}
            libraries_root=(self.game/'libraries').resolve()
            for candidate in set(deleted_libraries or [])-used_libraries:
                try:
                    if candidate.is_file() and not candidate.is_symlink() and candidate.resolve().is_relative_to(libraries_root):candidate.unlink()
                except OSError:pass
            if deleted_index and not any(index==deleted_index for _,_,index in references) and index_path:
                try:
                    if index_path.is_file() and not index_path.is_symlink():index_path.unlink()
                except OSError:pass
                used_objects=set()
                for _,_,index in references:
                    if not isinstance(index,str) or not ID_RE.fullmatch(index):continue
                    other_index=self._cache_file(self.game/'assets'/'indexes',index+'.json')
                    try:
                        if not other_index or not other_index.is_file():safe_cache=False;break
                        for item in read_json(other_index).get('objects',{}).values():
                            h=item.get('hash') if isinstance(item,dict) else None
                            if isinstance(h,str) and re.fullmatch('[0-9a-f]{40}',h):used_objects.add(h)
                            else:safe_cache=False;break
                    except (OSError,ValueError,AttributeError):safe_cache=False;break
                if safe_cache:
                    assets_root=(self.game/'assets'/'objects').resolve()
                    for candidate in deleted_objects:
                        if candidate.name not in used_objects:
                            try:
                                if candidate.is_file() and not candidate.is_symlink() and candidate.resolve().is_relative_to(assets_root):candidate.unlink()
                            except OSError:pass
        return f'已刪除實例「{value}」及其世界、Mods、設定。仍被其他版本使用的共用檔案會保留。'
    def launch(self,payload):
        folder,record=self.get_instance(payload);Network(self.cancel).check()
        managed=record.get('managed',True)
        if managed:
            stored_java=Path(record['java']).expanduser()
            java=stored_java.resolve() if stored_java.is_absolute() else inside(self.root,str(stored_java))
            data=read_json(folder/'launch.json');game=self.game;work=folder;game_directory=folder
            required=record.get('java_major') or java_major_for(data,record.get('version',data['id']))
            native_legacy=use_arm64_legacy_lwjgl2(data)
            static_arch=java_file_arch(java) if native_legacy else None
            info=java_info(java) if (not native_legacy or static_arch=='aarch64') and not (needs_intel_java8(required,data) and not rosetta_installed()) else None
            if not info or not java_compatible(required,info[0]) or not java_arch_compatible(required,info[1],data):
                replacement=self.find_existing_java(required,[self.java_root,self.root,self.game,*self.root_candidates()],strict=False,data=data)
                info=java_info(replacement) if replacement else None
                if replacement and info and java_compatible(required,info[0]) and java_arch_compatible(required,info[1],data):java=replacement
                else:
                    runtime_data=data
                    if not data.get('javaVersion'):
                        runtime_data=dict(data);runtime_data['javaVersion']={'component':'jre-legacy','majorVersion':required}
                    java=self.runtime(runtime_data,Network(self.cancel,lambda msg:self.progress(msg)))
                    info=java_info(java)
                    if not info or not java_compatible(required,info[0]) or not java_arch_compatible(required,info[1],data):
                        raise UserError(f'無法取得可用的 Java {required}。請檢查網絡、macOS 版本及 CPU 架構後重試。')
                try:record['java']=str(java.resolve().relative_to(self.root))
                except ValueError:record['java']=str(java.resolve())
                record['java_major']=required
                atomic_json(folder/'instance.json',record)
        else:
            version=ident(record['version']);manifest=inside(folder/'versions',version+'/'+version+'.json')
            if not manifest.is_file():raise UserError('原啟動器的版本資料已移動。請重新掃描資料夾。')
            data=read_json(manifest);game=folder;work=inside(self.root/'external-work',record['id']);work.mkdir(parents=True,exist_ok=True);game_directory=folder
            required=record.get('java_major') or java_major_for(data,version)
            roots=[folder,self.java_root,self.root,self.game,*self.root_candidates()]
            java=self.find_existing_java(required,roots,strict=False,data=data)
            if java is None:
                if payload.get('install_java') is not True:
                    raise UserError(f'外部遊戲 {version} 需要 Java {required}。請先確認是否由 MambaCraft 下載安裝相應 Java。')
                runtime_data=data
                if not data.get('javaVersion'):
                    runtime_data=dict(data);runtime_data['javaVersion']={'component':RUNTIME_COMPONENT_BY_MAJOR.get(required,'jre-legacy'),'majorVersion':required}
                java=self.runtime(runtime_data,Network(self.cancel,lambda msg:self.progress(msg)))
            info=java_info(java)
        if not info or not java_compatible(required,info[0]) or not java_arch_compatible(required,info[1],data):raise UserError(f'Java {required} 缺失或架構不相容。請安裝相同架構的 Java，再按「檢查及修復」。')
        ram=self.config['ram'] or 3072
        if host_os()=='osx':
            try:
                total=int(subprocess.check_output(['/usr/sbin/sysctl','-n','hw.memsize'],timeout=3))//2**20
                if self.config['ram']==0: ram=min(4096,max(2048,total//4))
                if ram>total-2048: raise UserError('記憶體分配太多，請改用自動。')
            except (OSError,ValueError,subprocess.TimeoutExpired): pass
        compatibility_classpath=None;compatibility_native=None
        if use_arm64_legacy_lwjgl2(data):
            self.progress('正在準備並校驗 Apple Silicon 舊版視窗相容元件…')
            compatibility_classpath,compatibility_native=self.prepare_arm64_lwjgl2(data,game,Network(self.cancel,lambda msg:self.progress(msg)))
        # Rebuild natives on every start so a previous x86/ARM attempt cannot leave stale files.
        natives_directory=work/'natives'
        if natives_directory.is_symlink():raise UserError('原生函式庫路徑為符號連結；為保護資料已停止啟動。')
        if natives_directory.exists():
            if not natives_directory.is_dir():raise UserError('原生函式庫路徑不是資料夾；請按「檢查及修復」。')
            shutil.rmtree(natives_directory)
        for archive,exclude in library_plan(data,game)[2]:extract_native(archive,natives_directory,exclude)
        if compatibility_native:extract_native(compatibility_native,natives_directory,['META-INF/'])
        if compatibility_classpath:
            bridge_path=Path(__file__).resolve().parent/ARM64_OBJC_BRIDGE_JAR['path']
            if bridge_path not in compatibility_classpath:
                raise UserError('Apple Silicon Objective-C bridge 沒有加入啟動 classpath；已停止啟動。')
            extract_arm64_objc_bridge_native(bridge_path,natives_directory)
        auth=self.microsoft_accounts.launch_credentials() or self.java_accounts.launch_credentials()
        self.last_auth_token=auth['token'] if auth else None
        cmd=command(data,game,work,java,self.config['selected'],ram,game_directory=game_directory,
                    classpath_override=compatibility_classpath,natives_directory=natives_directory,auth=auth)
        log=self.logs/('game-'+time.strftime('%Y%m%d-%H%M%S')+'.log')
        Network(self.cancel).check()
        with log.open('w',encoding='utf-8') as f:
            f.write(('Existing installation: '+str(game)+'\n' if not managed else '')+f'MambaCraft {APP_VERSION}\nInstance: {record["id"]}\nJava: {info}\nRAM: {ram} MB\n')
            if compatibility_classpath:f.write('Compatibility: Apple Silicon ARM64 Java 8 + pinned LWJGL 2.9.4 ARM64 natives + bundled JNA 5.7.0 + universal java-objc-bridge 1.1.0-mmachina.1 + extracted libjcocoa.dylib on java.library.path\n')
            safe_command=command_for_log(cmd)
            if auth:safe_command=[str(x).replace(auth['token'],'<redacted>') for x in safe_command]
            f.write('Java command (sensitive values redacted): '+json.dumps(safe_command,ensure_ascii=False)+'\n'); f.flush()
            proc=subprocess.Popen(cmd,cwd=game,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
        with self.lock: self.process=proc; self.running=record['id']; self.last_exit=None; self.last_log=log.name
        self.progress('Java 已啟動，等候遊戲視窗…'); time.sleep(1.5)
        if proc.poll() is not None: raise UserError(f'遊戲立即結束（代碼 {proc.returncode}）。請查看遊戲日誌。')
        return '遊戲程序已啟動；請確認已進入 Minecraft 主畫面。'
    def backup(self,payload):
        folder,record=self.get_instance(payload); directory=self.root/'backups'; directory.mkdir(exist_ok=True)
        dest=directory/(record['id']+'-'+time.strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:6]+'.zip'); temp=dest.with_suffix('.part')
        self.progress('正在備份世界、模組及遊戲設定…',0,0)
        try:
            with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED) as z:
                for name in ('saves','mods','config','options.txt','servers.dat'):
                    source=folder/name
                    if not source.exists(): continue
                    for p in ([source] if source.is_file() else source.rglob('*')):
                        Network(self.cancel).check()
                        if p.is_file() and not p.is_symlink() and p.resolve().is_relative_to(folder): z.write(p,p.relative_to(folder))
            Network(self.cancel).check(); os.replace(temp,dest)
        finally: temp.unlink(missing_ok=True)
        return '備份已建立：'+dest.name+'（「開啟備份」可找到）'
    def diagnostics(self,payload):
        dest=self.root/'diagnostics'; dest.mkdir(exist_ok=True)
        report={'version':APP_VERSION,'platform':platform.platform(),'architecture':host_arch(),'python':platform.python_version(),
          'freeGB':round(shutil.disk_usage(self.root).free/2**30,1),'instances':[{'id':x['id'],'version':x['version'],'managed':x.get('managed',True)} for x in self.installed()],'lastExit':self.last_exit,
          'javaRoot':str(self.java_root).replace(str(Path.home()),'~')}
        path=dest/('diagnostics-'+time.strftime('%Y%m%d-%H%M%S')+'.zip')
        def redact(raw):
            raw=raw.replace(str(Path.home()),'~').replace(str(self.root),'<MambaCraft>')
            if self.last_auth_token:raw=raw.replace(self.last_auth_token,'<redacted>')
            raw=re.sub(r'(--(?:accessToken|clientToken|sessionId|session|username|uuid)\s+)(\S+)',r'\1<redacted>',raw,flags=re.I)
            raw=re.sub(r'(--(?:accessToken|clientToken|sessionId|session|username|uuid)=)(\S+)',r'\1<redacted>',raw,flags=re.I)
            return raw
        with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
            z.writestr('report.json',json.dumps(report,ensure_ascii=False,indent=2))
            # A hung/invisible window need not produce a crash report. Capture
            # only this launcher's live child when the user requests diagnostics.
            proc=self.process
            if host_os()=='osx' and proc is not None and proc.poll() is None:
                try:
                    sampled=subprocess.run(['/usr/bin/sample',str(proc.pid),'2','1','-file','/dev/stdout'],
                                           capture_output=True,text=True,timeout=8)
                    raw=f'PID: {proc.pid}; sample exit: {sampled.returncode}\n'+sampled.stdout+'\n'+sampled.stderr
                except (OSError,subprocess.TimeoutExpired) as exc:
                    raw='Live process sampling unavailable: '+type(exc).__name__
                z.writestr('live-process/sample.txt',redact(raw[-2_000_000:]))
            for p in sorted(self.logs.glob('*.log'),key=lambda p:p.stat().st_mtime)[-4:]:
                with p.open('rb') as f:
                    f.seek(max(0,p.stat().st_size-256000)); raw=f.read().decode('utf-8','replace')
                z.writestr('logs/'+p.name,redact(raw))
            crashes=sorted((p for p in self.game.glob('hs_err_pid*.log') if p.is_file() and not p.is_symlink()),key=lambda p:p.stat().st_mtime)[-2:]
            for p in crashes:
                with p.open('rb') as f:
                    f.seek(max(0,p.stat().st_size-512000));raw=f.read().decode('utf-8','replace')
                z.writestr('jvm-crashes/'+p.name,redact(raw))
        return '診斷包已建立：'+path.name+'。遊戲仍在執行時會嘗試擷取 Mac 執行緒；分享前請檢查玩家名稱與伺服器地址。'
    def open_folder(self,payload):
        kind=payload.get('kind')
        if kind in ('logs','backups','diagnostics'): path=self.root/kind
        elif kind in ('instance','mods','saves','game'):
            path,record=self.get_instance(payload)
            if kind=='game':
                if record.get('managed',True):
                    data=read_json(path/'launch.json')
                    path=self.game/'versions'/ident(data.get('jar',data.get('id',record.get('version',''))))
                else:path=path/'versions'/ident(record.get('version',''))
            elif kind!='instance':path=path/kind
            if not record.get('managed',True) and kind=='mods':path.mkdir(parents=True,exist_ok=True)
        else: raise UserError('未知資料夾。')
        path.mkdir(parents=True,exist_ok=True)
        if host_os()!='osx': raise UserError('開啟 Finder 功能只適用於 macOS。')
        subprocess.Popen(['/usr/bin/open',str(path)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    def log_text(self):
        path=self.logs/(self.last_log or 'helper.log')
        if not path.exists(): return '暫時沒有日誌。'
        with path.open('rb') as f:
            f.seek(max(0,path.stat().st_size-48000)); text=f.read().decode('utf-8','replace')
        if self.last_auth_token:text=text.replace(self.last_auth_token,'<redacted>')
        return re.sub(r'(?i)(--(?:accessToken|clientToken|sessionId|session)[\s=]+)\S+',r'\1<redacted>',text)
