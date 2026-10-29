'use strict';
let brPage=sessionStorage.getItem('mamba-br-page')||'play',brVersion=sessionStorage.getItem('mamba-br-version')||'',brDataVersion='',brContent=null,brContentRequest=0,brCatalogSignature='',brJobSignature='';
const brTitles={play:'開始遊戲',versions:'遊戲版本',worlds:'世界存檔',resources:'資源',help:'日誌與支援'};
function brNavigate(page){brPage=Object.prototype.hasOwnProperty.call(brTitles,page)?page:'play';sessionStorage.setItem('mamba-br-page',brPage);document.querySelectorAll('.tab').forEach(el=>el.hidden=el.id!=='tab-library');document.querySelectorAll('[data-br-page]').forEach(el=>el.hidden=el.dataset.brPage!==brPage);document.querySelectorAll('.nav').forEach(el=>{const active=el.dataset.brTab===brPage;el.classList.toggle('active',active);if(active)el.setAttribute('aria-current','page');else el.removeAttribute('aria-current');});$('brPageTitle').textContent=brTitles[brPage];$('breadcrumb').textContent=tr('基岩版')+' / '+tr(brTitles[brPage]);if(bedrockState){renderBrPages(bedrockState);if(['worlds','resources'].includes(brPage))brLoadContent();}localize();}
async function brCopy(value){try{await navigator.clipboard.writeText(value);notice('已複製路徑。');}catch{const input=document.createElement('textarea');input.value=value;document.body.append(input);input.select();const ok=document.execCommand&&document.execCommand('copy');input.remove();notice(ok?'已複製路徑。':'無法自動複製，請選取畫面上的完整路徑後複製。');}}
function brPath(label,value,open){const row=document.createElement('div');row.className='br-path';const text=document.createElement('div'),title=document.createElement('strong'),code=document.createElement('code');title.textContent=label;code.textContent=value||'尚未建立';text.append(title,code);row.append(text);const actions=document.createElement('div');actions.className='br-path-actions';if(value){const copy=bedrockButton('複製路徑',()=>brCopy(value));delete copy.dataset.bedrockControl;actions.append(copy);if(open)actions.append(bedrockButton('開啟資料夾',open));}row.append(actions);return row;}
function brOpen(id,kind,world_id,pack_type){return bedrockAction('bedrock-content-open',{id,kind,world_id,pack_type});}
function brCollapsePathGroup(id,label){const target=$(id);if(!target||target.parentElement?.tagName==='DETAILS')return;const details=document.createElement('details');details.className='br-location-details';const summary=document.createElement('summary');summary.textContent=label;const parent=target.parentElement;parent.insertBefore(details,target);details.append(summary,target);}
function brSelectVersion(id){brVersion=id;brDataVersion=id;sessionStorage.setItem('mamba-br-version',id);brContent=null;brContentRequest++;if(bedrockState){brCatalogSignature='';renderBrPages(bedrockState);}brLoadContent();}
function renderBrPages(b){
 const busy=bedrockBusy||b.job?.status==='running',items=b.versions||[];
 if(!items.some(v=>v.id===brVersion))brVersion=items[0]?.id||'';
 const contentIds=b.contentVersions||items.map(v=>v.id);
 if(brDataVersion!=='external'&&!contentIds.includes(brDataVersion))brDataVersion=brVersion||'external';
 const signature=JSON.stringify([items.map(v=>[v.id,v.compatibility,v.canLaunch,v.launchBlockReason]),contentIds,b.dataRoot,brVersion,brDataVersion]);
 if(signature!==brCatalogSignature){brCatalogSignature=signature;for(const id of ['brPlayVersion','brWorldVersion','brResourceVersion']){const el=$(id),selected=id==='brPlayVersion'?brVersion:brDataVersion;el.replaceChildren(...items.map(v=>option(v.id,v.id+(!v.canLaunch?' · 無法啟動':v.compatibility==='unverified'?' · 相容性未驗證':''))));if(id!=='brPlayVersion'){for(const saved of contentIds.filter(v=>!items.some(item=>item.id===v)))el.append(option(saved,saved+' · 已保留的世界'));el.append(option('external','外部／共用資料位置'));}if(!el.options.length)el.append(option('','尚未安裝遊戲'));el.value=selected;} }
 const selected=items.find(v=>v.id===brVersion),canLaunch=selected&&selected.canLaunch;
 $('brPlay').disabled=busy||!canLaunch;$('brPlay').textContent=b.running?'遊戲執行中':'開始遊戲 ▶';
 $('brPlayHint').textContent=!selected?'尚未安裝遊戲。請先新增遊戲版本。':!canLaunch?(selected.launchBlockReason||'此版本缺少適合這台 Mac 的遊戲檔案。'):selected.compatibility==='unverified'?'此版本相容性尚未驗證，可以按「開始遊戲」嘗試啟動。':'每個版本使用獨立存檔。';
 $('brLaunchError').hidden=!(b.job?.status==='error'&&b.job?.action==='bedrock-play');
 const bridge=b.compatibilityBridge,needsBridge=selected&&bridge?.games?.includes(selected.id);
 $('brCompatHint').hidden=!needsBridge;$('brPrepareCompat').hidden=!needsBridge;
 $('brPrepareCompat').disabled=busy||!!bridge?.ready;
 $('brCompatHint').textContent=bridge?.ready?'相容補丁已準備；啟動時會驗證並載入。':'首次啟動會自動下載並準備相容補丁。';
 $('brRuntimeBadge').textContent=b.runtime?.ready?'核心已就緒':'首次啟動會準備核心';
 $('brPlayPaths').replaceChildren(...(selected?[brPath('遊戲檔案',selected.path,()=>bedrockAction('bedrock-open',{kind:'version',world_id:selected.id})),brPath('世界與資源位置',selected.dataPath||'',()=>brOpen(selected.id,'root'))]:[]));
 const storage=selected?.storage;
 $('brStorageHint').textContent=!selected?'':!storage||storage.freeBytes==null?'無法讀取存檔磁碟空間；啟動前會重新檢查。':'存檔磁碟可用空間：'+(storage.freeBytes/1073741824).toFixed(2)+' GiB（'+storage.freeBytes+' bytes）。啟動前會檢查寫入權限。';
 const loc=b.locations||{};
 $('brRuntimePaths').replaceChildren(brPath('基岩版核心',loc.runtime,()=>bedrockAction('bedrock-support-open',{kind:'runtime'})),brPath('相容補丁位置',loc.compatibility,()=>bedrockAction('bedrock-support-open',{kind:'compatibility'})));
 $('brVersionPaths').replaceChildren(brPath('遊戲版本安裝位置',b.paths?.versions||b.dataRoot+'/versions',()=>bedrockAction('bedrock-open',{kind:'versions'})));
 $('brSupportPaths').replaceChildren(brPath('遊戲日誌',loc.gameLog,()=>bedrockAction('bedrock-support-open',{kind:'logs'})),brPath('啟動器日誌',loc.logs,()=>bedrockAction('bedrock-support-open',{kind:'logs'})),brPath('世界備份',loc.backups,()=>bedrockAction('bedrock-support-open',{kind:'backups'})),brPath('基岩版核心',loc.runtime,()=>bedrockAction('bedrock-support-open',{kind:'runtime'})),brPath('相容補丁位置',loc.compatibility,()=>bedrockAction('bedrock-support-open',{kind:'compatibility'})));
 for(const id of ['brResourceDownload','brResourceImport'])$(id).disabled=busy||!items.some(v=>v.id===brDataVersion);
 $('brAutoImport').disabled=busy||bedrockBusy||!items.some(v=>v.id===brDataVersion&&v.id!=='external');
 for(const id of ['brPlayVersion','brWorldVersion','brResourceVersion'])$(id).disabled=busy;
 document.querySelectorAll('[data-bedrock-control]').forEach(button=>button.disabled=busy||button.dataset.unavailable==='true');
 $('bedrockLaunch').disabled=busy||!!b.runtime?.ready;
 const job=JSON.stringify([b.job?.status,b.job?.result,b.dataRoot]);if(job!==brJobSignature){brJobSignature=job;brContent=null;if(['worlds','resources'].includes(brPage))brLoadContent();}
 localize();
}
async function brLoadContent(){if(!bedrockState||!['worlds','resources'].includes(brPage))return;const id=brDataVersion;if(brContent?.id===id)return;const ticket=++brContentRequest;try{const content=await api('bedrock-content',{id});if(ticket!==brContentRequest||id!==brDataVersion)return;brContent=content;renderBrContent(content);}catch(e){if(ticket!==brContentRequest)return;notice(e.message);for(const name of ['bedrockWorlds','bedrockResourcePacks','bedrockBehaviorPacks'])bedrockEmpty($(name),'無法讀取內容，請重新掃描。');}}
function renderBrContent(c){const id=c.id,paths=c.paths||{};
 $('brWorldPaths').replaceChildren(brPath('世界存檔位置',paths.worlds,()=>brOpen(id,'worlds')),brPath('備份儲存位置',c.backupPath,()=>bedrockAction('bedrock-support-open',{kind:'backups'})));
 $('brResourcePaths').replaceChildren(brPath('資源包位置',paths['resource-packs'],()=>brOpen(id,'resource-packs')),brPath('行為包位置',paths['behavior-packs'],()=>brOpen(id,'behavior-packs')));
 renderBrAutoImport(c.autoImport||{});
 $('bedrockWorldCount').textContent=`${c.worlds.length} 個世界`;
 const list=$('bedrockWorlds');list.replaceChildren();if(!c.worlds.length)bedrockEmpty(list,'這個版本尚未建立世界。進入遊戲建立世界後，按「重新掃描」。');
 for(const world of c.worlds){const card=document.createElement('article');card.className='card bedrock-card';const main=document.createElement('div');main.className='bedrock-card-main';const name=document.createElement('b');name.textContent=world.name;main.append(name,brPath('世界存檔',world.path,()=>brOpen(id,'world',world.id)));card.append(main,bedrockButton('備份 .mcworld',()=>bedrockJob('bedrock-world-backup',{id,world_id:world.id})));list.append(card);}
 for(const [element,kind] of [['bedrockResourcePacks','resource-packs'],['bedrockBehaviorPacks','behavior-packs']]){const target=$(element);target.replaceChildren();const packs=c.packs[kind]||[];if(!packs.length)bedrockEmpty(target,'這個版本尚未安裝此類資源。');for(const pack of packs){const card=document.createElement('article');card.className='card bedrock-card br-pack-card';const main=document.createElement('div');main.className='bedrock-card-main';const title=document.createElement('b');title.textContent=pack.name;const version=document.createElement('small');version.textContent=pack.version||'已安裝';main.append(title,version);card.append(main,bedrockButton('開啟資料夾',()=>brOpen(id,'pack',pack.id,kind)));target.append(card);}}
 brCollapsePathGroup('brResourcePaths','資源與行為包儲存位置');
 document.querySelectorAll('[data-bedrock-control]').forEach(button=>button.disabled=bedrockBusy||bedrockState?.job?.status==='running'||button.dataset.unavailable==='true');localize();}
function initBrPages(){
 document.querySelectorAll('[data-br-go]').forEach(button=>button.onclick=()=>brNavigate(button.dataset.brGo));
 $('brPlayVersion').onchange=()=>brSelectVersion($('brPlayVersion').value);
 for(const id of ['brWorldVersion','brResourceVersion'])$(id).onchange=async()=>{const retarget=id==='brResourceVersion'&&!!brContent?.autoImport?.enabled;brDataVersion=$(id).value;brContent=null;brContentRequest++;brCatalogSignature='';renderBrPages(bedrockState);if(retarget)await brSetAutoImport(brDataVersion!=='external');brLoadContent();};
 for(const id of ['brWorldRefresh','brResourceRefresh'])$(id).onclick=()=>{brContent=null;brLoadContent();};
 $('brLaunchError').onclick=()=>{brNavigate('help');$('bedrockReadLog').click();};
 $('brPrepareCompat').onclick=()=>bedrockJob('bedrock-compat',{id:brVersion});
 $('brPlay').onclick=()=>bedrockJob('bedrock-play',{id:brVersion});
 $('brResourceDownload').onclick=()=>{const url=$('brResourceUrl').value.trim();try{const parsed=new URL(url);if(parsed.protocol!=='https:'||parsed.username||parsed.password||parsed.hash)throw Error();}catch{notice('請貼上有效的 HTTPS 資源檔案直連。');return;}bedrockJob('bedrock-resource-install',{id:brDataVersion,url});};
 $('brResourceImport').onclick=()=>bedrockJob('bedrock-resource-install',{id:brDataVersion,choose:true});
 try{const savedSource=localStorage.getItem('mamba-br-resource-source');if(brResourceSources[savedSource])$('brResourceSource').value=savedSource;}catch{}
 $('brResourceSource').onchange=()=>{try{localStorage.setItem('mamba-br-resource-source',$('brResourceSource').value);}catch{}brUpdateResourceSource();};
 $('brResourceSearchButton').onclick=brSearchResourceSource;
 $('brResourceSearch').onkeydown=e=>{if(e.key==='Enter')brSearchResourceSource();};
 brUpdateResourceSource();
 $('brAutoImport').onchange=()=>brSetAutoImport($('brAutoImport').checked);
 brCollapsePathGroup('brResourcePaths','資源與行為包儲存位置');
 $('brExportLog').onclick=async()=>{try{const result=await api('bedrock-log'),blob=new Blob([result.text],{type:'text/plain;charset=utf-8'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='MambaCraft-Bedrock.log.txt';document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);}catch(e){notice(e.message);}};
}

function renderBrAutoImport(state){
 const toggle=$('brAutoImport'),status=$('brAutoImportStatus');if(!toggle||!status)return;
 toggle.checked=!!state.enabled;
 status.textContent=state.message|| (state.enabled?'監看 Downloads 的新 .mcpack／.mcaddon 檔案。':'自動匯入目前關閉。');
 status.dataset.state=state.status||'off';
}
async function brSetAutoImport(enabled){
 const id=brDataVersion;if(enabled&&(!id||id==='external')){notice('請先選擇已安裝的 MambaCraft 版本。');$('brAutoImport').checked=false;return;}
 $('brAutoImport').disabled=true;
 try{const state=await api('bedrock-resource-watch',{enabled,id});if(brContent?.id===id){brContent.autoImport=state;renderBrAutoImport(state);}else renderBrAutoImport(state);}
 catch(e){$('brAutoImport').checked=!enabled;notice(e.message);}
 finally{$('brAutoImport').disabled=!!bedrockBusy||bedrockState?.job?.status==='running';}
}
const brResourceSources={
 mcpedl:{browse:'https://mcpedl.com/addons/',search:'https://mcpedl.com/'},
 klpbbs:{browse:'https://klpbbs.com/forum.php?gid=37',search:'https://klpbbs.com/search.php?mod=forum'}
};
function brUpdateResourceSource(){
 const source=brResourceSources[$('brResourceSource').value]||brResourceSources.mcpedl;
 $('brResourceBrowse').href=source.browse;
}
function brSearchResourceSource(){
 const provider=$('brResourceSource').value,source=brResourceSources[provider]||brResourceSources.mcpedl,query=$('brResourceSearch').value.trim();
 const url=new URL(query?source.search:source.browse);
 if(query)url.searchParams.set(provider==='klpbbs'?'srchtxt':'s',query);
 const tab=window.open(url.toString(),'_blank');if(tab)tab.opener=null;else notice('瀏覽器封鎖了新分頁，請使用上方「瀏覽來源網站」連結。');
}
