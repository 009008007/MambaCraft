"""Same-origin loopback UI. Random port + bearer token; no arbitrary file server."""
import argparse
import hmac
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import secrets
import threading
import time
from urllib.parse import urlparse
from core import Engine, UserError, atomic_json
from bedrock import BedrockManager
from bedrock_runtime import IntegratedBedrockManager

UI_LEASE_SECONDS=90
UI_STARTUP_GRACE_SECONDS=60
UI_CLOSE_GRACE_SECONDS=3

class Server(ThreadingHTTPServer):
    daemon_threads=True
    def __init__(self, engine, token=None):
        super().__init__(('127.0.0.1',0), Handler)
        self.engine=engine; self.token=token or secrets.token_urlsafe(32)
        self.bedrock=IntegratedBedrockManager(engine)
        engine.bedrock_actions={
            'bedrock-runtime':self.bedrock.prepare_runtime,
            'bedrock-catalog':self.bedrock.refresh_catalog,
            'bedrock-install':self.bedrock.install_game,
            'bedrock-play':self.bedrock.launch_game,
            'bedrock-instance':self.bedrock.instance_action,
            'bedrock-compat':self.bedrock.prepare_compatibility,
            'bedrock-resource-install':self.bedrock.install_resource,
            'bedrock-resource-auto-install':self.bedrock.auto_import_resource,
            'bedrock-world-backup':self.bedrock.content_backup,
            'bedrock-remove':self.bedrock.remove_version,
        }
        self.origin=f'http://127.0.0.1:{self.server_port}'
        self.web=Path(__file__).parent/'web'
        self.ui_lock=threading.Lock(); self.ui_clients={}; self.ui_seen=False; self.started_at=time.monotonic(); self.ui_empty_since=self.started_at
    def touch_ui(self,window):
        if not isinstance(window,str) or not re.fullmatch(r'[A-Za-z0-9_-]{12,80}',window):return
        with self.ui_lock:self.ui_clients[window]=time.monotonic(); self.ui_seen=True; self.ui_empty_since=None
    def close_ui(self,window):
        if not isinstance(window,str):return
        with self.ui_lock:
            self.ui_clients.pop(window,None)
            if not self.ui_clients:self.ui_empty_since=time.monotonic()

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args): pass # Never log bearer tokens or launch URLs.
    def setup(self):
        super().setup(); self.connection.settimeout(10)
    def send(self,code,body,content='application/json; charset=utf-8'):
        if isinstance(body,(dict,list)): body=json.dumps(body,ensure_ascii=False).encode()
        elif isinstance(body,str): body=body.encode()
        self.send_response(code); self.send_header('Content-Type',content)
        self.send_header('Content-Length',str(len(body)))
        self.send_header('Cache-Control','no-store'); self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Referrer-Policy','no-referrer')
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data: https://cdn.modrinth.com https://mod.mcimirror.top; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
        self.end_headers()
        try: self.wfile.write(body)
        except (BrokenPipeError,ConnectionResetError): pass
    def valid_host(self):
        if self.headers.get('Host')!=self.server.origin.removeprefix('http://'):
            self.send(403,{'error':'拒絕未知 Host。'}); return False
        return True
    def authorized(self):
        if not self.valid_host(): return False
        origin=self.headers.get('Origin')
        if origin and origin!=self.server.origin:
            self.send(403,{'error':'拒絕跨來源要求。'}); return False
        if not hmac.compare_digest(self.headers.get('Authorization',''),'Bearer '+self.server.token):
            self.send(401,{'error':'連線已失效，請重新開啟 MambaCraft.app。'}); return False
        self.server.touch_ui(self.headers.get('X-Mamba-Window'))
        return True
    def do_GET(self):
        path=urlparse(self.path).path
        if path.startswith('/api/'):
            if not self.authorized(): return
            if path=='/api/state': self.send(200,self.server.engine.state())
            elif path=='/api/log': self.send(200,{'text':self.server.engine.log_text()})
            elif path=='/api/bedrock': self.send(200,self.server.bedrock.state())
            elif path=='/api/bedrock-log':
                log=self.server.bedrock.game_log
                if log.is_file():
                    with log.open('rb') as f:
                        f.seek(max(0,log.stat().st_size-65536)); text=f.read().decode('utf-8',errors='replace')
                else:text='尚未產生基岩版遊戲日誌。'
                text=re.sub(r'(?i)(token|authorization|cookie|password)([\s=:]+)[^\s]+',r'\1\2[REDACTED]',text)
                self.send(200,{'text':text})
            else: self.send(404,{'error':'未知 API。'})
        else:
            if not self.valid_host(): return
            files={'/bedrock_pages.js':('bedrock_pages.js','text/javascript; charset=utf-8'),'/':('index.html','text/html; charset=utf-8'),'/app.js':('app.js','text/javascript; charset=utf-8'),'/i18n.js':('i18n.js','text/javascript; charset=utf-8'),'/style.css':('style.css','text/css; charset=utf-8')}
            if path not in files: self.send(404,{'error':'找不到頁面。'}); return
            name,mime=files[path]; self.send(200,(self.server.web/name).read_bytes(),mime)
    def do_POST(self):
        if not self.authorized(): return
        try:
            if self.headers.get('Content-Type','').split(';')[0]!='application/json': raise UserError('只接受 JSON。')
            length=int(self.headers.get('Content-Length','0'))
            if not 1<=length<=8192: raise UserError('要求大小不合法。')
            data=json.loads(self.rfile.read(length))
            if not isinstance(data,dict): raise UserError('資料格式錯誤。')
            action=urlparse(self.path).path.removeprefix('/api/'); engine=self.server.engine
            if action=='window-close':
                self.server.close_ui(self.headers.get('X-Mamba-Window')); self.send(200,{'ok':True}); return
            elif action=='launch-check':
                self.send(200,engine.launch_check(data)); return
            elif action=='profile': engine.save_profile(data.get('name'))
            elif action=='profile-remove': engine.remove_profile(data.get('name'))
            elif action=='java-account-discover':
                self.send(200,engine.java_accounts.discover(data)); return
            elif action=='java-account-login':
                self.send(200,engine.java_accounts.login(data)); return
            elif action=='java-account-finish':
                self.send(200,engine.java_accounts.finish(data)); return
            elif action=='java-account-skin':
                self.send(200,engine.java_accounts.skin_preview(data)); return
            elif action=='java-account-select':
                engine.java_accounts.select(data)
            elif action=='java-account-remove':
                engine.java_accounts.remove(data)
            elif action=='microsoft-account-start':
                self.send(200,engine.microsoft_accounts.start(data)); return
            elif action=='microsoft-account-poll':
                self.send(200,engine.microsoft_accounts.poll(data)); return
            elif action=='microsoft-account-remove':
                engine.microsoft_accounts.remove(data)
            elif action=='memory': engine.memory(data.get('ram'))
            elif action=='theme': engine.set_theme(data.get('theme'))
            elif action=='language': engine.set_language(data.get('language'))
            elif action=='edition': engine.set_edition(data.get('edition'))
            elif action=='java-root':
                if 'path' not in data:raise UserError('Java 資料夾路徑欄位缺失。')
                engine.set_java_root(data['path'])
            elif action=='bedrock-content':
                self.send(200,self.server.bedrock.content_state(data)); return
            elif action=='bedrock-resource-watch':
                self.send(200,self.server.bedrock.configure_resource_auto_import(data)); return
            elif action=='bedrock-content-open':
                message=self.server.bedrock.content_open(data)
                self.send(200,{'ok':True,'message':message}); return
            elif action=='bedrock-support-open':
                message=self.server.bedrock.support_open(data)
                self.send(200,{'ok':True,'message':message}); return
            elif action=='bedrock-root':
                if 'path' not in data:raise UserError('Bedrock 資料夾路徑欄位缺失。')
                message=self.server.bedrock.set_root(data['path'])
                self.send(200,{'ok':True,'message':message}); return
            elif action=='bedrock-scan':
                self.send(200,self.server.bedrock.state()); return
            elif action=='bedrock-open':
                message=self.server.bedrock.open_folder(data.get('kind'),data.get('world_id'),data.get('pack_type'))
                self.send(200,{'ok':True,'message':message}); return
            elif action=='bedrock-launcher':
                message=self.server.bedrock.launch_upstream()
                self.send(200,{'ok':True,'message':message}); return
            elif action=='bedrock-backup':
                if engine.job.get('status')=='running':raise UserError('請先完成目前工作或退出遊戲。')
                message=self.server.bedrock.backup_world(data.get('world_id'))
                self.send(200,{'ok':True,'message':message}); return
            elif action=='cancel':
                if engine.job.get('action')=='bedrock-play' and self.server.bedrock.game and self.server.bedrock.game.poll() is None:
                    raise UserError('請在基岩版遊戲中儲存並正常退出。')
                if engine.job.get('action')=='launch': raise UserError('遊戲正在啟動，請在遊戲內正常退出。')
                engine.cancel.set()
            elif action=='folder': engine.open_folder(data)
            elif action=='quit':
                with engine.lock:
                    state=engine.state()
                    if state['running'] or state['job']['status']=='running': raise UserError('請先等候工作完成並正常退出遊戲。')
                    engine.closing=True
                self.send(200,{'ok':True}); threading.Thread(target=self.server.shutdown,daemon=True).start(); return
            else: engine.start(action,data)
            self.send(200,{'ok':True})
        except (UserError,ValueError,TypeError) as exc: self.send(400,{'error':str(exc)})
        except Exception:
            import traceback
            with (self.server.engine.logs/'helper.log').open('a') as f: traceback.print_exc(file=f)
            self.send(500,{'error':'操作失敗，請查看日誌。'})
    def do_OPTIONS(self): self.send(403,{'error':'不接受跨來源請求。'})

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--data',required=True); opts=parser.parse_args()
    root=Path(opts.data).resolve(); root.mkdir(parents=True,exist_ok=True); os.chmod(root,0o700)
    import fcntl
    install_guard=(root/'install.lock').open('a')
    try: fcntl.flock(install_guard,fcntl.LOCK_SH|fcntl.LOCK_NB)
    except BlockingIOError: raise SystemExit('安裝器正在更新，請完成後再開啟。')
    lock=(root/'server.lock').open('a')
    try: fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError: return
    server=Server(Engine(root)); session=root/'session.json'
    atomic_json(session,{'pid':os.getpid(),'port':server.server_port,'token':server.token})
    threading.Thread(target=monitor_ui, args=(server,), daemon=True).start()
    try: server.serve_forever(poll_interval=0.2)
    finally:
        server.server_close(); session.unlink(missing_ok=True); lock.close()

def monitor_ui(server):
    # A pagehide request normally closes the helper within a few seconds. The
    # lease handles browser crashes; active Minecraft/game work keeps the helper alive.
    while not server.engine.closing:
        time.sleep(1)
        if not idle_shutdown_due(server):continue
        with server.engine.lock:server.engine.closing=True
        threading.Thread(target=server.shutdown,daemon=True).start()
        return

def idle_shutdown_due(server,now=None):
    now=time.monotonic() if now is None else now
    with server.ui_lock:
        expired=[key for key,last in server.ui_clients.items() if now-last>UI_LEASE_SECONDS]
        for key in expired:server.ui_clients.pop(key,None)
        if server.ui_clients:server.ui_empty_since=None
        elif server.ui_empty_since is None:server.ui_empty_since=now
        empty_since=server.ui_empty_since
        if server.ui_clients or (not server.ui_seen and now-server.started_at<UI_STARTUP_GRACE_SECONDS):return False
        if empty_since is None or now-empty_since<UI_CLOSE_GRACE_SECONDS:return False
    state=server.engine.state()
    return not state['running'] and state['job']['status']!='running'

if __name__=='__main__': main()
