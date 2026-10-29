"""Microsoft account authentication for Minecraft Java Edition.

The launcher is a public desktop client: Microsoft passwords never enter this
process. Device-code OAuth obtains a refresh token, which is kept in the same
macOS Keychain vault used by the skin-site account manager.
"""
import hashlib
import json
import re
import time
import uuid
from urllib.parse import urlsplit

import requests

from core import UserError, atomic_json, read_json, username
from java_accounts import Keychain

CLIENT_ID = 'ded3fd8a-0f8b-4bf8-8780-0c67a5d2a6b1'
DEVICE_URL = 'https://login.microsoftonline.com/consumers/oauth2/v2.0/devicecode'
TOKEN_URL = 'https://login.microsoftonline.com/consumers/oauth2/v2.0/token'
XBL_URL = 'https://user.auth.xboxlive.com/user/authenticate'
XSTS_URL = 'https://xsts.auth.xboxlive.com/xsts/authorize'
MC_LOGIN_URL = 'https://api.minecraftservices.com/authentication/login_with_xbox'
ENTITLEMENTS_URL = 'https://api.minecraftservices.com/entitlements/mcstore'
PROFILE_URL = 'https://api.minecraftservices.com/minecraft/profile'
SERVICE = 'org.mambacraft.microsoft'


def _json(response, message, raise_http=True):
    try:
        value = response.json()
    except (ValueError, requests.RequestException):
        raise UserError(message) from None
    if not isinstance(value, dict):
        raise UserError(message)
    if raise_http and response.status_code >= 400:
        detail = value.get('errorMessage') or value.get('error_description') or value.get('error')
        if isinstance(detail, str) and detail and len(detail) <= 240:
            if 'invalid app registration' in detail.lower():
                raise UserError('Minecraft 官方服務未接受此 Client ID。請參閱 https://aka.ms/AppRegInfo 了解官方審核流程。')
            raise UserError(message + '（官方訊息：' + detail + '）')
        raise UserError(message)
    return value


class MicrosoftAccountManager:
    def __init__(self, engine, vault=None):
        self.engine = engine
        self.vault = vault or Keychain()
        self.path = engine.root / 'microsoft-accounts.json'
        self.pending = {}
        self.accounts = []
        try:
            data = read_json(self.path) if self.path.exists() else []
            if isinstance(data, list):
                self.accounts = [a for a in data if isinstance(a, dict)
                                 and a.get('provider') == 'microsoft'
                                 and re.fullmatch(r'[a-f0-9]{32}', str(a.get('id', '')))
                                 and re.fullmatch(r'[a-f0-9]{32}', str(a.get('uuid', '')))
                                 and isinstance(a.get('name'), str)]
        except (OSError, ValueError, TypeError):
            self.accounts = []

    def state(self):
        return [dict(a) for a in self.accounts]

    def active(self):
        ident = self.engine.config.get('microsoft_account')
        return next((a for a in self.accounts if a['id'] == ident), None)

    def _check_idle(self):
        if self.engine.job.get('status') == 'running' or (self.engine.process and self.engine.process.poll() is None):
            raise UserError('請先等候工作／遊戲結束，再更改玩家。')

    def start(self, _data=None):
        self._check_idle()
        try:
            response = requests.post(DEVICE_URL, data={'client_id': CLIENT_ID, 'scope': 'XboxLive.signin offline_access'}, timeout=(8, 15))
            if response.status_code != 200:
                raise UserError('Microsoft 登入服務暫時無法使用，請稍後重試。')
            data = _json(response, 'Microsoft 登入回應格式不正確。')
            device_code = data.get('device_code'); user_code = data.get('user_code')
            verify = data.get('verification_uri') or data.get('verification_url')
            if not all(isinstance(x, str) and x for x in (device_code, user_code, verify)):
                raise UserError('Microsoft 登入回應格式不正確。')
            key = uuid.uuid4().hex
            self.pending[key] = {'device_code': device_code, 'interval': max(2, int(data.get('interval', 5))),
                                 'expires': time.monotonic() + int(data.get('expires_in', 900)), 'last': 0}
            return {'pending': key, 'verificationUri': verify, 'userCode': user_code,
                    'message': data.get('message', '請在瀏覽器完成 Microsoft 登入。'),
                    'expiresIn': int(data.get('expires_in', 900))}
        except (requests.RequestException, ValueError, TypeError):
            raise UserError('無法連線 Microsoft 登入服務，請檢查網絡。') from None

    def _xbox(self, microsoft_token):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        payload = {'Properties': {'AuthMethod': 'RPS', 'SiteName': 'user.auth.xboxlive.com',
                                  'RpsTicket': 'd=' + microsoft_token},
                   'RelyingParty': 'http://auth.xboxlive.com', 'TokenType': 'JWT'}
        response = requests.post(XBL_URL, headers=headers, json=payload, timeout=(8, 15))
        xbl = _json(response, 'Xbox Live 登入失敗，請確認這是可用的 Microsoft 帳號。')
        token = xbl.get('Token'); claims = xbl.get('DisplayClaims', {}).get('xui', [])
        if not isinstance(token, str) or not claims or not isinstance(claims[0], dict) or not claims[0].get('uhs'):
            raise UserError('Xbox Live 登入回應不完整。')
        response = requests.post(XSTS_URL, headers=headers, json={'Properties': {'SandboxId': 'RETAIL', 'UserTokens': [token]},
                                  'RelyingParty': 'rp://api.minecraftservices.com/', 'TokenType': 'JWT'}, timeout=(8, 15))
        xsts = _json(response, 'Xbox Live 身份驗證失敗。')
        xsts_token = xsts.get('Token')
        if not isinstance(xsts_token, str):
            raise UserError('Xbox Live 身份驗證回應不完整。')
        return claims[0]['uhs'], xsts_token, str(claims[0].get('xid') or '')

    def _minecraft(self, microsoft_token):
        uhs, xsts, xuid = self._xbox(microsoft_token)
        response = requests.post(MC_LOGIN_URL, json={'identityToken': f'XBL3.0 x={uhs};{xsts}'}, timeout=(8, 15))
        data = _json(response, 'Minecraft 官方登入失敗。')
        token = data.get('access_token')
        if not isinstance(token, str) or not token:
            detail = data.get('errorMessage') or data.get('error_description') or data.get('error')
            if isinstance(detail, str) and detail and len(detail) <= 240:
                if 'invalid app registration' in detail.lower():
                    raise UserError('Minecraft 官方服務未接受此 Client ID。請參閱 https://aka.ms/AppRegInfo 了解官方審核流程。')
                raise UserError('Minecraft 官方登入失敗（官方訊息：' + detail + '）。')
            raise UserError('Minecraft 官方登入回應不完整；請確認 Microsoft 帳號已啟用 Xbox Live，然後重試。')
        response = requests.get(ENTITLEMENTS_URL, headers={'Authorization': 'Bearer ' + token}, timeout=(8, 15))
        entitlements = _json(response, '無法確認 Minecraft 正版擁有權。')
        items = entitlements.get('items') or []
        if not isinstance(items, list) or not any(isinstance(x, dict) and x.get('name') in ('minecraft', 'product_minecraft') for x in items):
            raise UserError('這個 Microsoft 帳號沒有 Minecraft Java & Bedrock Edition 擁有權。')
        response = requests.get(PROFILE_URL, headers={'Authorization': 'Bearer ' + token}, timeout=(8, 15))
        profile = _json(response, '找不到 Minecraft 玩家資料；請先在 minecraft.net 完成玩家名稱設定。')
        try:
            ident = uuid.UUID(profile['id']).hex
            name = username(profile['name'])
        except (KeyError, ValueError, TypeError, UserError):
            raise UserError('Minecraft 玩家資料格式不正確。') from None
        return {'token': token, 'uuid': ident, 'name': name, 'xuid': xuid, 'skins': profile.get('skins') or []}

    def poll(self, data):
        self._check_idle()
        key = data.get('pending')
        entry = self.pending.get(key)
        if not entry or entry['expires'] <= time.monotonic():
            self.pending.pop(key, None)
            raise UserError('Microsoft 登入代碼已過期，請重新開始登入。')
        if time.monotonic() - entry['last'] < entry['interval']:
            return {'pending': key, 'waiting': True}
        entry['last'] = time.monotonic()
        try:
            response = requests.post(TOKEN_URL, data={'client_id': CLIENT_ID, 'grant_type': 'urn:ietf:params:oauth:grant-type:device_code', 'device_code': entry['device_code']}, timeout=(8, 15))
            # Device-code OAuth deliberately returns HTTP 400 while the user
            # has not entered the code yet. Parse that response below instead
            # of turning the normal authorization_pending state into an error.
            result = _json(response, 'Microsoft 登入回應格式不正確。', raise_http=False)
        except requests.RequestException:
            raise UserError('無法連線 Microsoft 登入服務，請稍後重試。') from None
        error = result.get('error')
        if error == 'authorization_pending': return {'pending': key, 'waiting': True}
        if error == 'slow_down': entry['interval'] += 5; return {'pending': key, 'waiting': True}
        if error in ('expired_token', 'invalid_grant'):
            self.pending.pop(key, None); raise UserError('Microsoft 登入代碼已過期，請重新開始登入。')
        if error: raise UserError('Microsoft 登入未完成：' + str(result.get('error_description') or error))
        microsoft_token = result.get('access_token'); refresh = result.get('refresh_token')
        if not isinstance(microsoft_token, str) or not isinstance(refresh, str): raise UserError('Microsoft 登入回應不完整。')
        try: profile = self._minecraft(microsoft_token)
        except requests.RequestException: raise UserError('無法連線 Minecraft 官方服務，請稍後重試。') from None
        account_id = hashlib.sha256(('microsoft\0' + profile['uuid']).encode()).hexdigest()[:32]
        account = {'id': account_id, 'provider': 'microsoft', 'name': profile['name'], 'uuid': profile['uuid'], 'serverName': 'Microsoft 正版', 'xuid': profile['xuid']}
        self.vault.set(account_id, {'refresh_token': refresh})
        self.accounts = [a for a in self.accounts if a['id'] != account_id] + [account]
        atomic_json(self.path, self.accounts)
        self.engine.config['microsoft_account'] = account_id
        self.engine.config.pop('java_account', None)
        atomic_json(self.engine.config_path, self.engine.config)
        self.pending.pop(key, None)
        return {'ok': True, 'account': account}

    def launch_credentials(self):
        account = self.active()
        if not account:
            if self.engine.config.get('microsoft_account'): raise UserError('找不到 Microsoft 帳號，請重新登入。')
            return None
        stored = self.vault.get(account['id']); refresh = stored.get('refresh_token')
        if not isinstance(refresh, str) or not refresh: raise UserError('Microsoft 登入資料已遺失，請重新登入。')
        response = requests.post(TOKEN_URL, data={'client_id': CLIENT_ID, 'grant_type': 'refresh_token', 'refresh_token': refresh, 'scope': 'XboxLive.signin offline_access'}, timeout=(8, 15))
        result = _json(response, 'Microsoft 登入資料已過期，請重新登入。')
        token = result.get('access_token'); new_refresh = result.get('refresh_token') or refresh
        if not isinstance(token, str): raise UserError('Microsoft 登入資料已過期，請重新登入。')
        profile = self._minecraft(token)
        if profile['uuid'] != account['uuid']: raise UserError('Microsoft 帳號玩家資料已變更，請重新登入。')
        self.vault.set(account['id'], {'refresh_token': new_refresh})
        return {'kind': 'microsoft', 'name': profile['name'], 'uuid': profile['uuid'], 'token': profile['token'],
                'xuid': profile.get('xuid') or account.get('xuid', ''), 'client_id': CLIENT_ID}

    def remove(self, data):
        self._check_idle(); ident = data.get('id')
        account = next((a for a in self.accounts if a['id'] == ident), None)
        if not account: raise UserError('找不到 Microsoft 帳號，請重新登入。')
        self.vault.delete(ident)
        self.accounts = [a for a in self.accounts if a['id'] != ident]
        atomic_json(self.path, self.accounts)
        if self.engine.config.get('microsoft_account') == ident:
            self.engine.config.pop('microsoft_account', None)
            atomic_json(self.engine.config_path, self.engine.config)

