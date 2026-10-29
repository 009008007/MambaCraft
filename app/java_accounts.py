"""Java external authentication. Secrets stay in the macOS Keychain."""
import base64
import hashlib
import ipaddress
import json
import re
import secrets
import socket
import struct
import subprocess
import threading
import time
import uuid
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit

import requests
from core import Network, UserError, atomic_json, read_json, username

LITTLESKIN = 'https://littleskin.cn/api/yggdrasil/'
INJECTOR = 'https://authlib-injector.yushi.moe/artifact/56/authlib-injector-1.2.8.jar'
INJECTOR_MIRROR = 'https://bmclapi2.bangbang93.com/mirrors/authlib-injector/artifact/56/authlib-injector-1.2.8.jar'
INJECTOR_SHA256 = '9c7f4343e6c82034958ffb48c14a2cb0c85928be7283103ce17da00c6d5a7b10'
SERVICE = 'org.mambacraft.yggdrasil'
MAX_RESPONSE = 256 * 1024


class Keychain:
    def get(self, key):
        try:
            result = subprocess.run(['/usr/bin/security','find-generic-password','-a',key,'-s',SERVICE,'-w'],
                                    capture_output=True,timeout=30,check=True)
            return json.loads(base64.b64decode(result.stdout.strip(),validate=True))
        except (OSError, subprocess.SubprocessError, ValueError, TypeError):
            raise UserError('無法讀取鑰匙圈中的登入資料，請重新登入。') from None

    def set(self, key, value):
        # Feed the command over stdin so the credential never appears in process arguments.
        encoded=base64.b64encode(json.dumps(value,ensure_ascii=True,separators=(',',':')).encode()).decode()
        command=f'add-generic-password -a {key} -s {SERVICE} -w {encoded} -U\n'
        try:
            subprocess.run(['/usr/bin/security','-i'],input=command.encode(),capture_output=True,timeout=30,check=True)
            if self.get(key)!=value: raise ValueError('keychain write did not persist')
        except (OSError,subprocess.SubprocessError,ValueError,UserError):
            raise UserError('無法儲存登入資料到 macOS 鑰匙圈。') from None

    def delete(self, key):
        try:
            subprocess.run(['/usr/bin/security','delete-generic-password','-a',key,'-s',SERVICE],
                           capture_output=True,timeout=30,check=True)
        except (OSError,subprocess.SubprocessError):
            raise UserError('無法從鑰匙圈移除登入資料。') from None


def safe_url(value, resolve=True):
    if not isinstance(value,str) or not value or len(value)>2048 or any(ord(c)<33 for c in value):
        raise UserError('請輸入有效的公開 HTTPS 皮膚站網址。')
    if '://' not in value:value='https://'+value
    try:
        p=urlsplit(value)
        if p.scheme!='https' or not p.hostname or p.username or p.password or p.fragment or p.query or p.port not in (None,443) or '\\' in value:
            raise ValueError()
        host=p.hostname.lower().rstrip('.')
        if host=='localhost' or host.endswith(('.localhost','.local')):raise ValueError()
        try: address=ipaddress.ip_address(host)
        except ValueError: address=None
        if address is not None and not address.is_global:raise ValueError()
        if resolve:
            addresses={entry[4][0] for entry in socket.getaddrinfo(host,443,type=socket.SOCK_STREAM)}
            if not addresses or any(not ipaddress.ip_address(addr).is_global for addr in addresses):raise ValueError()
        path=p.path or '/'
        return urlunsplit(('https',p.netloc,path,'',''))
    except (ValueError,OSError):
        raise UserError('請輸入有效的公開 HTTPS 皮膚站網址。') from None


def request(method,url,payload=None):
    """Never follow redirects while sending credentials; bound responses and sanitize errors."""
    url=safe_url(url)
    try:
        with requests.request(method,url,json=payload,timeout=(8,15),allow_redirects=False,stream=True,
                              headers={'Accept':'application/json','User-Agent':'MambaCraft-JavaAccounts'}) as response:
            if response.status_code in (301,302,303,307,308):
                if method!='GET':raise UserError('皮膚站要求重新導向登入，為保護登入資料已停止。')
                return response.status_code,response.headers.get('Location',''),None
            if response.status_code==204:return 204,'',None
            if response.status_code>=400:
                if response.status_code in (401,403):raise UserError('皮膚站登入資料無效或已過期，請重新登入。')
                raise UserError('皮膚站暫時無法處理要求，請稍後重試。')
            if response.status_code!=200:raise UserError('皮膚站回應格式不正確。')
            raw=bytearray()
            for chunk in response.iter_content(16384):
                raw.extend(chunk)
                if len(raw)>MAX_RESPONSE:raise UserError('皮膚站回應過大。')
            try:data=json.loads(raw)
            except (ValueError,UnicodeDecodeError):raise UserError('皮膚站回應格式不正確。') from None
            return 200,response.headers.get('X-Authlib-Injector-API-Location',''),data
    except requests.RequestException:
        raise UserError('無法連線皮膚站，請檢查網址與網絡。') from None


def discover(value):
    current=safe_url(value)
    for _ in range(6):
        status,location,data=request('GET',current)
        if status!=200:
            if not location:raise UserError('皮膚站重新導向不完整。')
            current=safe_url(urljoin(current,location));continue
        if location:
            target=safe_url(urljoin(current,location))
            if target.rstrip('/')!=current.rstrip('/'):current=target;continue
        if not isinstance(data,dict) or not any(k in data for k in ('meta','skinDomains','signaturePublickey')):
            raise UserError('找不到相容的 Yggdrasil 驗證服務。')
        meta=data.get('meta') if isinstance(data.get('meta'),dict) else {}
        name=meta.get('serverName') if isinstance(meta.get('serverName'),str) else urlsplit(current).hostname
        return current.rstrip('/')+'/',str(name)[:100],data
    raise UserError('皮膚站重新導向過多。')


def profile(value):
    if not isinstance(value,dict):raise UserError('皮膚站沒有可用的遊戲角色。')
    try:
        uid=uuid.UUID(value.get('id','')).hex
        name=username(value.get('name'))
    except (ValueError,TypeError,AttributeError,UserError):raise UserError('皮膚站回傳的角色資料不正確。') from None
    return {'id':uid,'name':name}


class AccountManager:
    def __init__(self,engine,vault=None):
        self.engine=engine;self.vault=vault or Keychain();self.path=engine.root/'java-accounts.json'
        self.discoveries={};self.pending={};self.skin_cache={};self.lock=threading.RLock();self.changing=False
        try:
            data=read_json(self.path) if self.path.exists() else []
            self.accounts=[a for a in data if isinstance(a,dict) and re.fullmatch('[a-f0-9]{32}',str(a.get('id',''))) and isinstance(a.get('server'),str) and isinstance(a.get('name'),str) and re.fullmatch('[a-f0-9]{32}',str(a.get('uuid','')))] if isinstance(data,list) else []
        except (OSError,ValueError,TypeError):self.accounts=[]

    def state(self):
        self.clean()
        return [dict(a) for a in self.accounts]
    def active(self):
        current=self.engine.config.get('java_account')
        return next((a for a in self.accounts if a['id']==current),None)
    def check_idle(self):
        if self.changing or self.engine.job.get('status')=='running' or self.engine.process and self.engine.process.poll() is None:
            raise UserError('請先等候工作／遊戲結束，再更改玩家。')
    def clean(self):
        now=time.monotonic()
        with self.lock:
            self.discoveries={k:v for k,v in self.discoveries.items() if v['expires']>now}
            self.pending={k:v for k,v in self.pending.items() if v['expires']>now}
    def discover(self,data):
        value=data.get('url',LITTLESKIN)
        url,name,metadata=discover(value)
        key=secrets.token_urlsafe(24);self.clean()
        with self.lock:self.discoveries[key]={'url':url,'name':name,'metadata':metadata,'expires':time.monotonic()+600}
        return {'discovery':key,'server':url,'serverName':name}
    def login(self,data):
        self.check_idle();self.clean()
        with self.lock:entry=self.discoveries.get(data.get('discovery'))
        login=data.get('login');password=data.get('password')
        if not entry:raise UserError('皮膚站確認已過期，請重新確認網址。')
        if not isinstance(login,str) or not login.strip() or len(login)>320 or not isinstance(password,str) or not password or len(password)>1024:
            raise UserError('請輸入皮膚站帳號和密碼。')
        client=uuid.uuid4().hex
        _,_,reply=request('POST',urljoin(entry['url'],'authserver/authenticate'),{'agent':{'name':'Minecraft','version':1},'username':login.strip(),'password':password,'clientToken':client,'requestUser':True})
        if not isinstance(reply,dict) or not isinstance(reply.get('accessToken'),str) or not reply.get('accessToken') or reply.get('clientToken')!=client:
            raise UserError('皮膚站回應格式不正確。')
        available=reply.get('availableProfiles') or []
        if not isinstance(available,list) or len(available)>100:raise UserError('皮膚站回應格式不正確。')
        selected=reply.get('selectedProfile'); choices=[profile(x) for x in available]
        if selected:
            selected=profile(selected)
            if not choices:choices=[selected]
        if not choices:raise UserError('皮膚站沒有可用的遊戲角色。')
        key=secrets.token_urlsafe(24)
        with self.lock:self.pending[key]={'entry':entry,'login':login.strip(),'reply':reply,'choices':choices,'selected':selected,'expires':time.monotonic()+300}
        if selected or len(choices)==1:return self.finish({'pending':key,'profile':(selected or choices[0])['id']})
        return {'pending':key,'profiles':choices}
    def finish(self,data):
        self.check_idle();self.clean();key=data.get('pending')
        with self.lock:pending=self.pending.get(key)
        if not pending:raise UserError('角色選擇已過期，請重新登入。')
        chosen=next((p for p in pending['choices'] if p['id']==data.get('profile')),None)
        if not chosen:raise UserError('請選擇有效的皮膚站角色。')
        reply=pending['reply'];entry=pending['entry']
        if pending['selected'] and pending['selected']['id']!=chosen['id']:
            raise UserError('請重新登入以選擇其他角色。')
        with self.lock:
            if self.pending.pop(key,None) is None:raise UserError('角色選擇已過期，請重新登入。')
        if not pending['selected']:
            _,_,reply=request('POST',urljoin(entry['url'],'authserver/refresh'),{'accessToken':reply['accessToken'],'clientToken':reply['clientToken'],'selectedProfile':chosen,'requestUser':True})
            if not isinstance(reply,dict) or profile(reply.get('selectedProfile'))['id']!=chosen['id'] or not reply.get('accessToken') or not reply.get('clientToken'):
                raise UserError('皮膚站回應格式不正確。')
        account_id=hashlib.sha256((entry['url']+'\0'+pending['login']+'\0'+chosen['id']).encode()).hexdigest()[:32]
        credential={'accessToken':reply['accessToken'],'clientToken':reply['clientToken'],'login':pending['login']}
        account={'id':account_id,'name':chosen['name'],'uuid':chosen['id'],'server':entry['url'],'serverName':entry['name']}
        with self.engine.lock:
            self.check_idle()
            self.changing=True
        try:
            self.vault.set(account_id,credential)
            with self.engine.lock:
                self.accounts=[x for x in self.accounts if x['id']!=account_id]+[account]
                atomic_json(self.path,self.accounts)
                self.engine.config['java_account']=account_id;self.engine.config.pop('microsoft_account',None);atomic_json(self.engine.config_path,self.engine.config)
        finally:
            with self.engine.lock:self.changing=False
        return {'ok':True,'account':account}
    def select(self,data):
        with self.engine.lock:
            self.check_idle();ident=data.get('id')
            if not any(a['id']==ident for a in self.accounts):raise UserError('找不到皮膚站帳號，請重新登入。')
            self.engine.config['java_account']=ident;self.engine.config.pop('microsoft_account',None);atomic_json(self.engine.config_path,self.engine.config)
    def remove(self,data):
        with self.engine.lock:
            self.check_idle();ident=data.get('id')
            if not any(a['id']==ident for a in self.accounts):raise UserError('找不到皮膚站帳號，請重新登入。')
            self.changing=True
        try:
            self.vault.delete(ident)
            with self.engine.lock:
                self.accounts=[a for a in self.accounts if a['id']!=ident];atomic_json(self.path,self.accounts)
                if self.engine.config.get('java_account')==ident:
                    self.engine.config.pop('java_account',None);atomic_json(self.engine.config_path,self.engine.config)
                with self.lock:self.skin_cache.pop(ident,None)
        finally:
            with self.engine.lock:self.changing=False
    def skin_preview(self,data):
        account=next((a for a in self.accounts if a['id']==data.get('id')),None)
        if not account:raise UserError('找不到皮膚站帳號，請重新登入。')
        with self.lock:cached=self.skin_cache.get(account['id'])
        if cached and cached[0]>time.monotonic():return {'skin':cached[1]}
        server=safe_url(account['server'])
        _,_,metadata=request('GET',server)
        _,_,info=request('GET',urljoin(server,'sessionserver/session/minecraft/profile/'+account['uuid']))
        if not isinstance(metadata,dict) or not isinstance(info,dict):return {'skin':None}
        domains=metadata.get('skinDomains') or []
        if not isinstance(domains,list) or len(domains)>100:return {'skin':None}
        props=info.get('properties') or []
        if not isinstance(props,list) or len(props)>100:return {'skin':None}
        entry=next((x.get('value') for x in props if isinstance(x,dict) and x.get('name')=='textures'),None)
        if not isinstance(entry,str) or len(entry)>65536:return {'skin':None}
        try:
            textures=json.loads(base64.b64decode(entry,validate=True))
            url=textures['textures']['SKIN']['url']
            url=safe_url(url);host=urlsplit(url).hostname.lower().rstrip('.')
            allowed=any(isinstance(d,str) and re.fullmatch(r'\.?[A-Za-z0-9.-]+',d) and
                        (host==d.lower().lstrip('.') or d.startswith('.') and host.endswith(d.lower())) for d in domains)
            if not allowed:return {'skin':None}
            with requests.get(url,timeout=(8,12),allow_redirects=False,stream=True) as response:
                if response.status_code!=200:return {'skin':None}
                raw=bytearray()
                for chunk in response.iter_content(16384):
                    raw.extend(chunk)
                    if len(raw)>512*1024:return {'skin':None}
            if len(raw)<24 or raw[:8]!=b'\x89PNG\r\n\x1a\n' or bytes(raw[12:16])!=b'IHDR' or struct.unpack('>II',raw[16:24]) not in ((64,64),(64,32)):
                return {'skin':None}
            skin='data:image/png;base64,'+base64.b64encode(raw).decode()
            with self.lock:self.skin_cache[account['id']]=(time.monotonic()+300,skin)
            return {'skin':skin}
        except (requests.RequestException,ValueError,TypeError,KeyError,UnicodeDecodeError):return {'skin':None}
    def launch_credentials(self):
        account=self.active()
        if not account:
            if self.engine.config.get('java_account'):raise UserError('找不到皮膚站帳號，請重新登入。')
            return None
        token=self.vault.get(account['id']);server=safe_url(account['server'])
        try:
            status,_,_=request('POST',urljoin(server,'authserver/validate'),{'accessToken':token['accessToken'],'clientToken':token['clientToken']})
            if status!=204:raise UserError('皮膚站登入資料無效或已過期，請重新登入。')
        except UserError as exc:
            if str(exc)!='皮膚站登入資料無效或已過期，請重新登入。':raise
            _,_,new=request('POST',urljoin(server,'authserver/refresh'),{'accessToken':token['accessToken'],'clientToken':token['clientToken'],'requestUser':True})
            if not isinstance(new,dict) or not new.get('accessToken') or new.get('clientToken')!=token['clientToken'] or profile(new.get('selectedProfile'))['id']!=account['uuid']:
                raise UserError('皮膚站登入資料無效或已過期，請重新登入。')
            token.update(accessToken=new['accessToken'],clientToken=new['clientToken']);self.vault.set(account['id'],token)
        _,_,metadata=request('GET',server)
        if not isinstance(metadata,dict):raise UserError('找不到相容的 Yggdrasil 驗證服務。')
        injector=self.engine.root/'authlib-injector'/'authlib-injector-1.2.8.jar'
        self.engine.progress('正在下載並校驗皮膚站登入元件…')
        Network(self.engine.cancel,lambda msg:self.engine.progress(msg)).download(INJECTOR,injector,sha256_digest=INJECTOR_SHA256,max_bytes=16*1024*1024,
            extra_hosts={'authlib-injector.yushi.moe','bmclapi2.bangbang93.com','github.com','release-assets.githubusercontent.com','objects.githubusercontent.com'},fallback_urls=(INJECTOR_MIRROR,))
        return {'name':account['name'],'uuid':account['uuid'],'token':token['accessToken'],'server':server,
                'injector':str(injector),'metadata':base64.b64encode(json.dumps(metadata,ensure_ascii=False,separators=(',',':')).encode()).decode()}
