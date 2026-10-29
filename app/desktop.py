"""Start/reuse the matching local helper, or stop it safely before an update."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import webbrowser


def read_session(root):
    try:
        data=json.loads((root/'session.json').read_text())
        port=data['port']; token=data['token']
        if type(port) is not int or not 1<=port<=65535 or not isinstance(token,str): return None
        url=f'http://127.0.0.1:{port}'
        request=Request(url+'/api/state',headers={'Authorization':'Bearer '+token})
        with urlopen(request,timeout=1) as response:
            state=json.load(response)
        if not isinstance(state,dict): return None
        return {'url':url,'token':token,'version':state.get('version'),'state':state}
    except (OSError,ValueError,KeyError,TypeError,URLError): return None


def wait_for_helper_exit(root, timeout=8):
    lock_paths=(root/'install.lock',root/'server.lock'); deadline=time.monotonic()+timeout
    while time.monotonic()<deadline:
        locks=[]
        try:
            for lock_path in lock_paths:
                lock=lock_path.open('a'); locks.append(lock)
                fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            for lock in reversed(locks):fcntl.flock(lock,fcntl.LOCK_UN)
            for lock in locks:lock.close()
            return
        except BlockingIOError:
            for lock in reversed(locks):
                try:fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
                except OSError:pass
            time.sleep(.1)
        except OSError:
            for lock in reversed(locks):
                try:lock.close()
                except OSError:pass
            time.sleep(.1)
    raise RuntimeError('舊版 Helper 尚未完全退出。請稍候再開啟，或先結束 Minecraft 遊戲。')


def stop_helper(root, session):
    if not session: return
    # RC12 can be stuck in its removed account job. Cancel that job before
    # requesting a normal shutdown; never terminate a game or other work here.
    job=session.get('state',{}).get('job',{})
    if job.get('status')=='running' and job.get('action')=='bedrock-account':
        request=Request(session['url']+'/api/cancel',data=b'{}',method='POST',
                        headers={'Authorization':'Bearer '+session['token'],'Content-Type':'application/json'})
        try:
            with urlopen(request,timeout=3) as response:json.load(response)
        except (URLError,ValueError):
            raise RuntimeError('舊版登入工作未能取消；請關閉舊版登入視窗後重新更新。') from None
        deadline=time.monotonic()+8
        while time.monotonic()<deadline:
            current=read_session(root)
            if not current: return
            if current['state'].get('job',{}).get('status')!='running':
                session=current; break
            time.sleep(.2)
        else: raise RuntimeError('舊版登入仍未退出；請關閉登入視窗後重新更新。')
    request=Request(session['url']+'/api/quit',data=b'{}',method='POST',
                    headers={'Authorization':'Bearer '+session['token'],'Content-Type':'application/json'})
    try:
        with urlopen(request,timeout=3) as response:
            if response.status!=200: raise RuntimeError('無法安全關閉目前的 Helper。')
    except HTTPError as exc:
        try:
            detail=json.loads(exc.read()).get('error','')
        except (ValueError,AttributeError): detail=''
        raise RuntimeError(detail or 'Helper 正在執行工作，請等候完成後再更新。')
    except URLError:
        raise RuntimeError('目前的 Helper 沒有回應；請先結束 MambaCraft.app，再重試。')
    wait_for_helper_exit(root)


def set_java_root(root,path,app_version):
    session=read_session(root)
    if session and session['version']!=app_version:
        stop_helper(root,session)
        session=None
    if session:
        payload=json.dumps({'path':path}).encode()
        request=Request(session['url']+'/api/java-root',data=payload,method='POST',
                        headers={'Authorization':'Bearer '+session['token'],'Content-Type':'application/json'})
        try:
            with urlopen(request,timeout=5) as response:json.load(response)
            return '已更新目前 Helper 的 Java 位置。'
        except HTTPError as exc:
            try:detail=json.loads(exc.read()).get('error','')
            except (ValueError,AttributeError):detail=''
            raise RuntimeError(detail or '目前 Helper 拒絕更改 Java 位置。')
        except URLError as exc:
            raise RuntimeError('目前 Helper 沒有回應，請重新開啟 MambaCraft 後再設定 Java 位置。') from exc
    from core import Engine, UserError
    try:return Engine(root).set_java_root(path)
    except UserError as exc:raise RuntimeError(str(exc)) from exc


def set_bedrock_root(root,path,app_version):
    session=read_session(root)
    if session and session['version']!=app_version:
        stop_helper(root,session)
        session=None
    if session:
        payload=json.dumps({'path':path}).encode()
        request=Request(session['url']+'/api/bedrock-root',data=payload,method='POST',
                        headers={'Authorization':'Bearer '+session['token'],'Content-Type':'application/json'})
        try:
            with urlopen(request,timeout=5) as response:json.load(response)
            return '已更新目前 Helper 的 Bedrock 資料位置。'
        except HTTPError as exc:
            try:detail=json.loads(exc.read()).get('error','')
            except (ValueError,AttributeError):detail=''
            raise RuntimeError(detail or '目前 Helper 拒絕更改 Bedrock 資料位置。')
        except URLError as exc:
            raise RuntimeError('目前 Helper 沒有回應，請重新開啟 MambaCraft 後再設定 Bedrock 資料位置。') from exc
    from bedrock import BedrockManager
    try:return BedrockManager(root).set_root(path)
    except UserError as exc:raise RuntimeError(str(exc)) from exc


def find_session(root, app_version):
    session=read_session(root)
    if not session: return None
    if session['version']!=app_version:
        old=session['version'] or '未知'
        stop_helper(root,session)
        print(f'已關閉舊版 Helper {old}，正在啟動 {app_version}。')
        return None
    return session['url']+'/#'+session['token']


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--data',required=True)
    parser.add_argument('--add-root')
    parser.add_argument('--set-java-root')
    parser.add_argument('--reset-java-root',action='store_true')
    parser.add_argument('--set-bedrock-root')
    parser.add_argument('--reset-bedrock-root',action='store_true')
    parser.add_argument('--stop-helper',action='store_true')
    parser.add_argument('--import-bedrock',nargs='+')
    opts=parser.parse_args()
    if opts.set_java_root and opts.reset_java_root:parser.error('choose either --set-java-root or --reset-java-root')
    if opts.set_bedrock_root and opts.reset_bedrock_root:parser.error('choose either --set-bedrock-root or --reset-bedrock-root')
    root=Path(opts.data).resolve(); root.mkdir(parents=True,exist_ok=True); os.chmod(root,0o700)
    if opts.stop_helper:
        stop_helper(root,read_session(root))
        return 0
    # The installer calls --stop-helper before creating/updating the venv.
    # Keep that path stdlib-only so a clean install never needs requests first.
    from core import APP_VERSION, Engine, UserError
    if opts.add_root:
        try: print(Engine(root).save_external_root(opts.add_root))
        except UserError as exc:
            print(str(exc),file=sys.stderr); return 2
        return 0
    if opts.set_java_root or opts.reset_java_root:
        try: print(set_java_root(root,opts.set_java_root,APP_VERSION))
        except RuntimeError as exc:print(str(exc),file=sys.stderr); return 2
        return 0
    if opts.set_bedrock_root or opts.reset_bedrock_root:
        try: print(set_bedrock_root(root,None if opts.reset_bedrock_root else opts.set_bedrock_root,APP_VERSION))
        except RuntimeError as exc:print(str(exc),file=sys.stderr); return 2
        return 0
    url=find_session(root,APP_VERSION)
    if not url:
        (root/'logs').mkdir(exist_ok=True)
        with (root/'logs/server.log').open('a') as log:
            subprocess.Popen([sys.executable,str(Path(__file__).with_name('server.py')),'--data',str(root)],
                             stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True,close_fds=True)
        for _ in range(60):
            url=find_session(root,APP_VERSION)
            if url: break
            time.sleep(.2)
    if not url: raise RuntimeError('MambaCraft 無法啟動，請查看資料夾內 logs/server.log。')
    if opts.import_bedrock:
        session=read_session(root)
        if not session: raise RuntimeError('Helper 尚未就緒，請重新開啟 MambaCraft。')
        payload=json.dumps({'paths':opts.import_bedrock}).encode()
        if len(payload)>8192: raise RuntimeError('選擇的檔案太多或路徑過長。')
        request=Request(session['url']+'/api/bedrock-install',data=payload,method='POST',
                        headers={'Authorization':'Bearer '+session['token'],'Content-Type':'application/json'})
        try:
            with urlopen(request,timeout=5) as response:json.load(response)
        except HTTPError as exc:
            try:detail=json.loads(exc.read()).get('error','')
            except (ValueError,AttributeError):detail=''
            raise RuntimeError(detail or 'Helper 拒絕匯入安裝包。') from None
        except URLError:
            raise RuntimeError('Helper 沒有回應，請重新開啟 MambaCraft。') from None
        print('匯入已開始，請在基岩版管理頁查看進度。')
        return 0
    webbrowser.open(url)
    return 0


if __name__=='__main__':
    try: raise SystemExit(main())
    except RuntimeError as exc:
        print(str(exc),file=sys.stderr); raise SystemExit(1)
