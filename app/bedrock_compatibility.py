"""Pinned, side-by-side compatibility bridge for observed Apple Silicon failures.

Original game files and game authentication are never changed. The native ELF
module uses the existing core's public mod API to register missing host hooks
and preload a standard Microsoft PlayFab SDK with the same SONAME.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import struct
import tempfile
import uuid
import zipfile
from bedrock import _safe_under
from bedrock_content import safe_mkdir
from bedrock_packages import download_package
from core import UserError, Cancelled, atomic_json

ASSETS = Path(__file__).parent / 'bedrock_compat'
MANIFEST = ASSETS / 'manifest.json'
READY_MARKER = '[MambaCompat] READY:'


def digest(path):
    hasher=hashlib.sha256()
    with Path(path).open('rb') as source:
        while chunk:=source.read(1024*1024):hasher.update(chunk)
    return hasher.hexdigest()


def elf_arm64(path):
    with Path(path).open('rb') as stream:header=stream.read(20)
    return len(header)==20 and header[:6]==b'\x7fELF\x02\x01' and struct.unpack_from('<H',header,18)[0]==183


class CompatibilityBridge:
    def __init__(self,manager):
        self.manager=manager
        self.spec=json.loads(MANIFEST.read_text())
        self.spec_hash=digest(MANIFEST)
        self.base=manager.launcher_data_root/'bedrock-compat'
        self.home=self.base/self.spec['id']

    def required(self,version):
        return self.manager.arch=='arm64' and version in self.spec['games']

    def ready(self,full=False):
        try:
            if not _safe_under(self.manager.launcher_data_root,self.home):return False
            record=json.loads((self.home/'receipt.json').read_text())
            if record.get('manifest')!=self.spec_hash:return False
            files=[(self.home/'libmamba_compat.so',self.spec['module']['sha256']),
                   (self.home/'patches/libPlayFabMultiplayer.so',self.spec['sdk']['librarySha256'])]
            return all(_safe_under(self.home,p) and p.is_file() and (not full or digest(p)==sha) for p,sha in files)
        except (OSError,ValueError,KeyError):return False

    def prepare(self,version):
        if not self.required(version):return None
        game=self.manager._configured_path()[0]/'versions'/version
        receipt=game/'mambacraft-version.json'
        if receipt.is_symlink():raise UserError('遊戲版本資料不安全，請重新匯入。')
        if receipt.is_file():
            metadata=json.loads(receipt.read_text())
            if metadata.get('code')!=self.spec['games'][version]:
                raise UserError('安裝包內的版本識別碼與相容補丁不符，未套用。')
        if self.ready(full=True):return self.home
        safe_mkdir(self.manager.launcher_data_root,self.base)
        module=ASSETS/'libmamba_compat.so'
        if module.is_symlink() or digest(module)!=self.spec['module']['sha256'] or not elf_arm64(module):
            raise UserError('隨附相容橋接程式校驗失敗，請重新解壓啟動器。')
        engine=self.manager.engine
        with tempfile.TemporaryDirectory(prefix='.prepare-',dir=self.base) as temporary:
            temp=Path(temporary);archive=temp/'sdk.zip'
            engine.progress('正在準備基岩版相容補丁：下載並校驗 PlayFab SDK…',0,0)
            sdk=self.spec['sdk']
            def sdk_progress(message=None,done=None,total=None):
                engine.progress('正在下載相容補丁 PlayFab SDK…',done,total)
            download_package(sdk['url'],archive,sdk['sha256'],engine.cancel,sdk_progress,limit=sdk['size'])
            if archive.stat().st_size!=sdk['size']:raise UserError('相容補丁下載大小不符。')
            payload=temp/'payload';payload.mkdir();(payload/'patches').mkdir()
            shutil.copyfile(module,payload/'libmamba_compat.so')
            output=payload/'patches/libPlayFabMultiplayer.so'
            try:
                with zipfile.ZipFile(archive) as z:
                    entries=[i for i in z.infolist() if i.filename==sdk['member']]
                    if len(entries)!=1 or stat.S_ISLNK(entries[0].external_attr>>16) or entries[0].file_size!=sdk['librarySize']:
                        raise UserError('SDK 未包含預期的 ARM64 相容程式庫。')
                    with z.open(entries[0]) as source,output.open('xb') as destination:
                        written=0
                        while chunk:=source.read(1024*1024):
                            if engine.cancel.is_set():raise Cancelled('已取消相容補丁準備。')
                            written+=len(chunk)
                            if written>sdk['librarySize']:raise UserError('相容程式庫大小不符。')
                            destination.write(chunk)
            except (zipfile.BadZipFile,RuntimeError,KeyError) as exc:
                raise UserError('相容補丁壓縮檔損壞，未安裝。') from exc
            if digest(output)!=sdk['librarySha256'] or not elf_arm64(output):
                raise UserError('PlayFab ARM64 程式庫校驗失敗，未安裝。')
            atomic_json(payload/'receipt.json',{'manifest':self.spec_hash,'bridge':self.spec['id'],'sdk':sdk['version']})
            if engine.cancel.is_set():raise Cancelled('已取消相容補丁準備。')
            previous=None
            if self.home.exists() or self.home.is_symlink():
                if not _safe_under(self.base,self.home):raise UserError('相容補丁目錄不安全。')
                previous=self.base/('.previous-'+uuid.uuid4().hex);os.rename(self.home,previous)
            try:os.rename(payload,self.home)
            except BaseException:
                if previous:os.rename(previous,self.home)
                raise
        engine.progress('相容補丁已準備，正在交給基岩版核心載入…')
        return self.home


def bridge_loaded(log_path):
    try:
        with Path(log_path).open('rb') as stream:
            return READY_MARKER.encode() in stream.read(262144)
    except OSError:return False


def failure_detail(log_path,code,compatibility_expected):
    try:
        with Path(log_path).open('rb') as f:
            head=f.read(262144);f.seek(max(len(head),Path(log_path).stat().st_size-65536));text=(head+f.read()).decode('utf-8',errors='replace')
    except OSError:text=''
    if 'invalid flags to dlopen:' in text and 'PlayFab preload failed' in text:
        return 'PlayFab 相容程式庫被核心拒絕載入（dlopen 旗標不相容），修補尚未生效。請更新至 RC20 或更新版本。'
    if '[MambaCompat] ERROR: storage query failed for path:' in text:
        return '遊戲無法讀取存檔位置的可用空間；日誌已列出實際查詢路徑，請檢查該位置的權限與磁碟狀態。'
    if compatibility_expected and READY_MARKER not in text:
        return '相容補丁未完成載入；請查看日誌中的 [MambaCompat] 或 ModLoader 錯誤。'
    if 'cannot locate symbol "pthread_sigmask"' in text:
        return '核心仍未解析 pthread_sigmask；請查看相容橋接程式載入記錄。'
    if 'bad_function_call' in text and 'libPlayFabMultiplayer.so' in text:
        return 'PlayFab 初始化仍拋出例外，需要依此版本的新堆疊進一步修復。'
    if 'libPlayFabMultiplayer.so' in text and ('Signal 10 received' in text or 'Signal 11 received' in text):
        return 'PlayFab 相容程式庫在目前的 Apple Silicon 核心上崩潰。此核心公布支援的版本最高為 1.21.73；請改用該範圍內的版本。'
    return f'基岩版程式已結束（代碼 {code}）。'
