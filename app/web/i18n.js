'use strict';
(()=>{
 const rows=[
  ['語言保存失敗','语言保存失败','Language preference could not be saved'],
  ['你的空間','你的空间','Workspace'],['◈　開始遊戲','◈　开始游戏','◈　Play'],['＋　安裝版本','＋　安装版本','＋　Install'],['⬇　Mods 與整合包','⬇　Mods 与整合包','⬇　Mods & Modpacks'],['▤　遊戲管理','▤　游戏管理','▤　Game Library'],['◎　玩家與設定','◎　玩家与设置','◎　Players & Settings'],['☷　日誌與支援','☷　日志与支持','☷　Logs & Support'],
  ['正在連接…','正在连接…','Connecting…'],['結束啟動器','结束启动器','Quit Launcher'],['你的空間 / 開始遊戲','你的空间 / 开始游戏','Workspace / Play'],['白天模式','白天模式','Light mode'],['夜間模式','夜间模式','Dark mode'],['切換至淺色主題','切换至浅色主题','Switch to light theme'],['切換至深色主題','切换至深色主题','Switch to dark theme'],['介面語言','界面语言','Interface language'],['繁體中文','繁体中文','Traditional Chinese'],['简体中文','简体中文','Simplified Chinese'],['本地玩家 ·','本地玩家 ·','Local player ·'],
  ['世界，由你開始。','世界，由你开始。','Your world starts here.'],['選好版本，帶上想像力。','选好版本，带上想象力。','Choose a version and bring your imagination.'],['熟悉的方塊，屬於你的玩法。','熟悉的方块，属于你的玩法。','Familiar blocks, your way to play.'],['探索並安裝版本 ↗','探索并安装版本 ↗','Explore and install versions ↗'],['我的遊戲','我的游戏','My Games'],['0 個實例','0 个实例','0 instances'],['重新掃描 ↻','重新扫描 ↻','Rescan ↻'],['新增遊戲資料夾…','添加游戏文件夹…','Add Game Folder…'],['目前遊戲版本','当前游戏版本','Selected Game Version'],['點此切換版本','点此切换版本','Click to switch versions'],['選擇要啟動的已安裝版本','选择要启动的已安装版本','Choose an installed version to launch'],['尚未安裝遊戲','尚未安装游戏','No games installed'],['每個實例使用獨立的世界與 Mods。','每个实例使用独立的世界与 Mods。','Each instance has its own worlds and mods.'],['開始遊戲','开始游戏','Play Game'],['檢查及修復','检查并修复','Check & Repair'],['遊戲資料夾 ↗','游戏文件夹 ↗','Game Folder ↗'],['Mods 資料夾 ↗','Mods 文件夹 ↗','Mods Folder ↗'],['備份世界與設定','备份世界与设置','Back Up Worlds & Settings'],['會自動掃描官方、Prism、MultiMC、PolyMC、ATLauncher、CurseForge 等常見位置；也可新增任何包含 Minecraft `versions` 資料夾的位置。外部世界沿用原資料夾，請先備份。','会自动扫描官方、Prism、MultiMC、PolyMC、ATLauncher、CurseForge 等常见位置；也可添加任何包含 Minecraft `versions` 文件夹的位置。外部世界沿用原文件夹，请先备份。','Common locations are scanned automatically, including the official launcher, Prism, MultiMC, PolyMC, ATLauncher and CurseForge. You can also add any folder containing Minecraft `versions`. External worlds stay in their original folders; back them up first.'],
  ['下一個世界，哪個版本？','下一个世界，哪个版本？','Which version will your next world be?'],['可安裝官方清單中的全部版本：正式版、快照／愚人節版本、Beta、Alpha 與早期版本。','可安装官方列表中的所有版本：正式版、快照／愚人节版本、Beta、Alpha 和早期版本。','Install any version in the official catalog: releases, snapshots and April Fools versions, Beta, Alpha, and earlier versions.'],['安裝新版本','安装新版本','Install a Version'],['更新官方清單 ↻','更新官方列表 ↻','Refresh Official Catalog ↻'],['搜尋版本','搜索版本','Search Versions'],['例如：1.8.9、20w14infinite、b1.7.3','例如：1.8.9、20w14infinite、b1.7.3','e.g. 1.8.9, 20w14infinite, b1.7.3'],['版本系列','版本系列','Version Series'],['全部官方版本','全部官方版本','All Official Versions'],['正式版','正式版','Release'],['快照／愚人節','快照／愚人节','Snapshots / April Fools'],['Beta 經典','Beta 经典','Beta Classics'],['Alpha 經典','Alpha 经典','Alpha Classics'],['Minecraft 版本','Minecraft 版本','Minecraft Version'],['先按「更新官方清單」','请先点“更新官方列表”','Click “Refresh Official Catalog” first'],['遊戲類型','游戏类型','Game Type'],['原版 Vanilla','原版 Vanilla','Vanilla'],['Fabric · 穩定 Loader','Fabric · 稳定 Loader','Fabric · Stable Loader'],['啟動器會先搜尋並驗證本機 Java（含版本與 CPU 架構）；Apple Silicon 上使用 LWJGL 2 的舊版會優先採用 ARM64 Java 8、ARM64 原生元件、固定雜湊的 JNA 5.7.0 和 universal Objective-C bridge；其他需 Intel 原生函式庫的舊版仍需 Rosetta 2。Fabric 只適用於官方支援的版本。','启动器会先搜索并验证本机 Java（含版本与 CPU 架构）；Apple Silicon 上使用 LWJGL 2 的旧版会优先采用 ARM64 Java 8、ARM64 原生组件、固定哈希的 JNA 5.7.0 和 universal Objective-C bridge；其他需要 Intel 原生库的旧版仍需 Rosetta 2。Fabric 仅适用于官方支持的版本。','The launcher checks local Java versions and CPU architectures first. On Apple Silicon, legacy LWJGL 2 versions prefer ARM64 Java 8 and verified ARM64 components. Some older Intel-native libraries still require Rosetta 2. Fabric is available only for officially supported versions.'],['安裝這個版本 ↓','安装此版本 ↓','Install This Version ↓'],['下載會校驗完整性；大型檔案遇到連線失敗或持續低速時，會自動切換備援來源，再回到官方來源重試。','下载会校验完整性；大文件遇到连接失败或持续低速时，会自动切换备用来源，再回到官方来源重试。','Downloads are verified. If a large file fails or stays slow, the launcher switches to a mirror and retries the official source.'],
  ['探索 Mods 與整合包','探索 Mods 与整合包','Discover Mods & Modpacks'],['搜尋 Modrinth 專案、查看相容的 Minecraft 版本與載入器，可從已安裝版本建議中選擇或手動輸入版本；Mods 預設匯入目前選定遊戲。空白搜尋會顯示熱門推薦。','搜索 Modrinth 项目、查看兼容的 Minecraft 版本与加载器，可从已安装版本建议中选择或手动输入版本；Mods 默认导入当前选定游戏。空白搜索会显示热门推荐。','Search Modrinth projects and check Minecraft and loader compatibility. Pick an installed version or enter one manually. Mods import to the selected game by default; an empty search shows popular picks.'],['整合包','整合包','Modpacks'],['搜尋關鍵字','搜索关键词','Search Keywords'],['例如：地圖、小地圖、Create、RLCraft','例如：地图、小地图、Create、RLCraft','e.g. map, minimap, Create, RLCraft'],['搜尋／熱門推薦','搜索／热门推荐','Search / Popular'],['Minecraft 版本（選填）','Minecraft 版本（选填）','Minecraft Version (Optional)'],['選已安裝版本，或手動輸入，例如 1.20.1','选择已安装版本，或手动输入，例如 1.20.1','Choose an installed version or enter one, e.g. 1.20.1'],['載入器（Mods）','加载器（Mods）','Loader (Mods)'],['不限','不限','Any'],['下載／安裝方式','下载／安装方式','Download / Install To'],['一鍵匯入已安裝遊戲的 Mods 資料夾','一键导入已安装游戏的 Mods 文件夹','Import to an installed game’s Mods folder'],['下載到系統 Downloads 資料夾','下载到系统 Downloads 文件夹','Download to system Downloads folder'],['目標遊戲','目标游戏','Target Game'],['先安裝或掃描遊戲','请先安装或扫描游戏','Install or scan for a game first'],['Mods 會校驗 SHA-1／SHA-512 後才寫入目標；外部遊戲會沿用原 Mods 資料夾，請先備份；載入器無法辨識時，需手動選擇實際使用的 loader。','Mods 会校验 SHA-1／SHA-512 后才写入目标；外部游戏会沿用原 Mods 文件夹，请先备份；加载器无法识别时，需手动选择实际使用的 loader。','Mods are verified with SHA-1 / SHA-512 before import. External games use their existing Mods folder; back it up first. If the loader cannot be identified, choose it manually.'],['搜尋來源：Modrinth 官方；官方來源失敗時嘗試 MCIM 備援。來源均無法使用時會提供專案頁面供手動下載。','搜索来源：Modrinth 官方；官方来源失败时尝试 MCIM 备用。来源均无法使用时会提供项目页供手动下载。','Search source: Modrinth. MCIM is tried if the official source fails. If both are unavailable, use the project page to download manually.'],['按「搜尋／熱門推薦」開始探索。','点击“搜索／热门推荐”开始探索。','Select “Search / Popular” to get started.'],['Modrinth 為主要內容來源。MCIM 是中國大陸的非官方快取鏡像，僅作連線備援；不同網絡、專案授權與快取狀態會影響可用性。整合包一鍵匯入會建立獨立實例，不會覆蓋現有世界；目前支援原版與 Fabric 的 .mrpack。其他載入器整合包可下載到 Downloads 後交由原平台匯入。','Modrinth 为主要内容来源。MCIM 是中国大陆的非官方缓存镜像，仅作连接备用；不同网络、项目授权与缓存状态会影响可用性。整合包一键导入会创建独立实例，不会覆盖现有世界；目前支持原版与 Fabric 的 .mrpack。其他加载器整合包可下载到 Downloads 后交由原平台导入。','Modrinth is the primary source. MCIM is an unofficial China-based cache used only as a connection fallback; availability varies by network, project permissions, and cache status. Importing a .mrpack creates an isolated instance and never overwrites worlds. One-click import currently supports Vanilla and Fabric; download other loaders to Downloads and import them with their original platform.'],
  ['遊戲管理','游戏管理','Game Library'],['查看每個版本的安裝路徑，開啟遊戲檔案、Mods 與存檔資料夾，或備份及刪除 MambaCraft 管理的實例。外部版本可檢視、開啟資料夾及備份，但不能從這裡刪除。','查看每个版本的安装路径，打开游戏文件、Mods 与存档文件夹，或备份及删除 MambaCraft 管理的实例。外部版本可查看、打开文件夹及备份，但不能从这里删除。','View install paths, open game files, Mods and saves, or back up and delete MambaCraft-managed instances. External games can be viewed, opened and backed up, but cannot be deleted here.'],['已安裝的遊戲','已安装的游戏','Installed Games'],['0 個版本','0 个版本','0 versions'],['尚未找到已安裝的遊戲。先安裝版本，或到「開始遊戲」新增外部資料夾。','尚未找到已安装的游戏。请先安装版本，或到“开始游戏”添加外部文件夹。','No installed games found. Install a version or add an external folder from Play.'],['玩家與設定','玩家与设置','Players & Settings'],['本地玩家','本地玩家','Local Player'],['已儲存的玩家','已保存的玩家','Saved Players'],['使用這個玩家','使用此玩家','Use This Player'],['建立另一個玩家','创建另一个玩家','Create Another Player'],['3–16 個英文字母、數字或底線。相同名稱保留相同 UUID；改名會改變世界內的玩家身份。','3–16 个英文字母、数字或下划线。相同名称保留相同 UUID；改名会改变世界内的玩家身份。','Use 3–16 English letters, numbers, or underscores. The same name keeps the same UUID; changing it changes your in-game identity.'],['建立並使用','创建并使用','Create & Use'],['記憶體','内存','Memory'],['遊戲可使用的記憶體','游戏可用内存','Memory Available to Game'],['自動（建議）','自动（建议）','Automatic (Recommended)'],['儲存設定','保存设置','Save Settings'],['Java 安裝與搜尋位置','Java 安装与搜索位置','Java Install & Search Location'],['建議位置：','建议位置：','Recommended location:'],['會先搜尋此資料夾及本機常見位置中的相容 Java；只有找不到時才下載所需版本到此處。此資料夾需要可寫入。已安裝實例會沿用原記錄的 Java；若要改用新位置的 Java，選取版本後按「檢查及修復」，世界與 Mods 會保留。','会先搜索此文件夹及本机常见位置中的兼容 Java；只有找不到时才下载所需版本到此处。此文件夹需要可写入。已安装实例会沿用原记录的 Java；若要改用新位置的 Java，选中版本后点“检查并修复”，世界与 Mods 会保留。','Compatible Java is searched for here and in common system locations. A required version is downloaded here only if none is found. This folder must be writable. Installed games keep their recorded Java; to switch, select a version and choose Check & Repair. Worlds and Mods are preserved.'],['選擇 Java 資料夾…','选择 Java 文件夹…','Choose Java Folder…'],['使用建議位置','使用建议位置','Use Recommended Location'],['資料位置','数据位置','Data Location'],['你的官方 Minecraft 舊存檔仍在原本資料夾；本版會建立自己的獨立實例。','你的官方 Minecraft 旧存档仍在原文件夹；本版会创建独立实例。','Your official Minecraft saves remain in their original folder. This launcher creates separate instances.'],['讓問題有答案。','让问题有答案。','Find answers to problems.'],['先查看錯誤，再決定修復。世界不會被修復程序刪除。','先查看错误，再决定修复。世界不会被修复程序删除。','Review the error before repairing. Repair does not delete worlds.'],['重新讀取日誌','重新读取日志','Reload Log'],['日誌資料夾 ↗','日志文件夹 ↗','Logs Folder ↗'],['匯出診斷包','导出诊断包','Export Diagnostics'],['開啟診斷包 ↗','打开诊断包 ↗','Open Diagnostics ↗'],['開啟備份 ↗','打开备份 ↗','Open Backups ↗'],['暫時沒有載入日誌。','暂时没有加载日志。','No log loaded yet.'],['遇到問題時','遇到问题时','Troubleshooting'],['Mods／整合包：','Mods／整合包：','Mods / Modpacks:'],['到「Mods 與整合包」搜尋或看熱門推薦，按 Minecraft 版本和載入器選相容版本。Minecraft 版本欄會建議已安裝版本並允許手動輸入；Mod 預設匯入目前選定遊戲，也可改存 Downloads；Modrinth .mrpack 可下載，或一鍵建立獨立 Vanilla／Fabric 實例。下載先校驗 SHA-1／SHA-512；官方來源失敗時嘗試 MCIM 鏡像，兩者失敗會提供專案頁面供手動下載。','到“Mods 与整合包”搜索或查看热门推荐，按 Minecraft 版本和加载器选择兼容版本。Minecraft 版本栏会建议已安装版本并允许手动输入；Mod 默认导入当前选定游戏，也可改存 Downloads；Modrinth .mrpack 可下载，或一键创建独立 Vanilla／Fabric 实例。下载先校验 SHA-1／SHA-512；官方来源失败时尝试 MCIM 镜像，两者失败会提供项目页供手动下载。','Search or browse popular picks in Mods & Modpacks, then choose a compatible Minecraft version and loader. Installed versions are suggested, and manual entry is supported. Mods import to the selected game by default or can be saved to Downloads. Modrinth .mrpack files can be downloaded or imported as an isolated Vanilla / Fabric instance. Downloads are checksum-verified; if both sources fail, use the project page.'],['下載失敗：','下载失败：','Download failed:'],['確認網絡及磁碟空間後重試。已校驗的檔案會保留。','确认网络和磁盘空间后重试。已校验的文件会保留。','Check your network and disk space, then retry. Verified files are kept.'],['遊戲閃退：','游戏闪退：','Game crash:'],['先按「檢查及修復」。使用 Fabric 時，暫時移走新增的模組，再看日誌。','先点“检查并修复”。使用 Fabric 时，暂时移走新加的模组，再查看日志。','Choose Check & Repair first. If you use Fabric, temporarily remove recently added mods and review the log.'],['Java 版本：','Java 版本：','Java version:'],['在「玩家與設定」選擇 Java 搜尋／安裝資料夾並查看建議位置；啟動器依遊戲 metadata 精確比對 Java 主版本和 CPU 架構，例如需要 Java 17 時不會誤用 Java 25；外部遊戲缺少相應 Java 時會先詢問，確認後才安裝。Apple Silicon 上使用 LWJGL 2 的版本會採用 ARM64 Java 8、固定校驗的 ARM64 原生庫、JNA 5.7.0 與 universal Objective-C bridge；GitHub 下載失敗時會嘗試固定雜湊驗證的 HTTPS 備援來源；其他需 Intel 原生函式庫的版本仍需 Rosetta 2。','在“玩家与设置”选择 Java 搜索／安装文件夹并查看建议位置；启动器按游戏 metadata 精确匹配 Java 主版本和 CPU 架构，例如需要 Java 17 时不会误用 Java 25；外部游戏缺少相应 Java 时会先询问，确认后才安装。Apple Silicon 上使用 LWJGL 2 的版本会采用 ARM64 Java 8、固定校验的 ARM64 原生库、JNA 5.7.0 与 universal Objective-C bridge；GitHub 下载失败时会尝试固定哈希校验的 HTTPS 备用源；其他需要 Intel 原生库的版本仍需 Rosetta 2。','Choose a Java search / install folder in Players & Settings. The launcher matches the required Java major version and CPU architecture, so Java 25 is not used when Java 17 is required. It asks before installing Java for external games. Apple Silicon legacy LWJGL 2 versions use verified ARM64 components; some Intel-only versions still require Rosetta 2.'],['想完全離線：','想完全离线：','For offline play:'],['先在線完成安裝並成功進入世界一次，正常退出，再關 Wi-Fi 測試。','先在线完成安装并成功进入世界一次，正常退出，再关闭 Wi-Fi 测试。','Install and enter a world once while online, quit normally, then test with Wi-Fi off.'],['遊戲管理：','游戏管理：','Game library:'],['在「遊戲管理」查看安裝、存檔、Mods 與 Java 路徑；可開啟相應資料夾、備份或刪除 MambaCraft 管理的實例。刪除會移除該實例的世界、Mods 與設定；外部實例由原啟動器管理。','在“游戏管理”查看安装、存档、Mods 与 Java 路径；可打开相应文件夹、备份或删除 MambaCraft 管理的实例。删除会移除此实例的世界、Mods 与设置；外部实例由原启动器管理。','Game Library shows install, saves, Mods and Java paths. You can open folders, back up, or delete MambaCraft-managed instances. Deleting removes that instance’s worlds, Mods and settings; external instances remain managed by their original launcher.'],['Microsoft 登入：','Microsoft 登录：','Microsoft sign-in:'],['這個交付版提供本地身份，未提供 Microsoft 登入、Realms 或正版驗證伺服器連線。','此版本提供本地身份，不提供 Microsoft 登录、Realms 或正版验证服务器连接。','This build uses local profiles. Microsoft sign-in, Realms, and authenticated server access are not included.'],['關閉介面：','关闭界面：','Closing the launcher:'],['關閉最後一個啟動器分頁後 Helper 會自動退出；若下載工作還在進行會等工作完成；若 Minecraft 還在運行會等遊戲結束。','关闭最后一个启动器标签页后 Helper 会自动退出；下载进行中时会等任务完成；Minecraft 运行时会等游戏退出。','The helper exits after the last launcher tab closes. It waits for downloads and Minecraft to finish first.'],['1.12.x 沒有視窗：','1.12.x 没有窗口：','No window on 1.12.x:'],['RC8 會把 universal','RC8 会把 universal','RC8 places universal'],['libjcocoa.dylib','libjcocoa.dylib','libjcocoa.dylib'],['放入這次遊戲的原生函式庫路徑，並記錄在遊戲日誌。若仍沒有視窗，保持遊戲運行、匯出診斷包並附上該次遊戲日誌；音樂或 Java PID 不代表啟動成功。','放入本次游戏的原生库路径，并记录在游戏日志。若仍没有窗口，保持游戏运行、导出诊断包并附上该次游戏日志；音乐或 Java PID 不代表启动成功。','is placed in the native library path and recorded in the game log. If no window appears, keep the game running, export diagnostics and include that game log. Music or a Java process alone does not mean launch succeeded.'],['版本狀態：','版本状态：','Release notes:'],['1.3 RC22 新增本地玩家清理與皮膚站登入憑證移除說明，保留世界資料。基岩版仍屬相容性預覽；macOS 實機進入世界驗證尚未完成。','1.3 RC22 新增本地玩家清理与皮肤站登录凭证移除说明，保留世界数据。基岩版仍属兼容性预览；macOS 实机进入世界验证尚未完成。','Version 1.3 RC22 adds local player cleanup and clarifies removal of saved skin site credentials while keeping world data. Bedrock remains a compatibility preview; entering a world on macOS still needs verification.'],['1.2.4 RC10 加入語言選擇，並保留白天／夜間主題與版本選擇提示。Mod 和整合包圖示、圖片備援、已安裝版本建議及 Mods 預設匯入均保留。RC8 的 Apple Silicon 舊版視窗修正及 RC7 的搜尋／匯入功能均保留。','1.2.4 RC10 增加语言选择，并保留白天／夜间主题与版本选择提示。Mod 和整合包图标、图片备用、已安装版本建议及 Mods 默认导入均保留。','Version 1.2.4 RC10 adds language selection and keeps the light / dark theme and clearer version picker. Mod and modpack icons, installed-version suggestions and default Mods import are also retained.'],['準備就緒','准备就绪','Ready'],['打開啟動器後，選擇或安裝遊戲。','打开启动器后，选择或安装游戏。','Open the launcher, then choose or install a game.'],['取消下載','取消下载','Cancel Download'],['開源 · 本機運作 · 無追蹤','开源 · 本地运行 · 无追踪','Open source · Local · No tracking'],
  ['連線失敗','连接失败','Connection failed'],['你的空間 / ','你的空间 / ','Workspace / '],['此系列沒有相符版本','此系列没有匹配版本','No matching versions in this series'],['先按「更新官方清單」','先点“更新官方列表”','Click “Refresh Official Catalog” first'],['正在檢查並更新完整官方版本清單…','正在检查并更新完整官方版本列表…','Checking and refreshing the full official catalog…'],['已有工作正在進行','已有任务正在进行','Another task is already running'],['更新官方版本清單失敗：','更新官方版本列表失败：','Could not refresh the official catalog: '],['；目前已快取的版本仍可使用，按「更新官方清單」重試。','；当前缓存版本仍可使用，点击“更新官方列表”重试。','; cached versions are still available. Select “Refresh Official Catalog” to retry.'],[' 個版本',' 个版本',' versions'],['尚未找到已安裝的遊戲。先安裝版本，或到「開始遊戲」新增外部資料夾。','尚未找到已安装的游戏。请先安装版本，或到“开始游戏”添加外部文件夹。','No installed games found. Install a version or add an external folder from Play.'],['外部安裝','外部安装','External installation'],['原版 Vanilla','原版 Vanilla','Vanilla'],['外部管理','外部管理','Externally managed'],['MambaCraft 管理','MambaCraft 管理','Managed by MambaCraft'],['安裝位置','安装位置','Install Location'],['遊戲版本檔案','游戏版本文件','Game Version Files'],['存檔資料夾','存档文件夹','Saves Folder'],['Mods 資料夾','Mods 文件夹','Mods Folder'],['Java 執行檔','Java 可执行文件','Java Executable'],['開啟遊戲資料夾','打开游戏文件夹','Open Game Folder'],['管理 Mods','管理 Mods','Manage Mods'],['管理存檔','管理存档','Manage Saves'],['備份世界','备份世界','Back Up Worlds'],['刪除版本','删除版本','Delete Version'],['確定永久刪除 ','确定永久删除 ','Permanently delete '],['？這會刪除此版本的世界、Mods 和設定。其他版本仍在使用的共用檔案會保留。','？这会删除此版本的世界、Mods 和设置。其他版本仍在使用的共享文件会保留。','? This deletes this version’s worlds, Mods and settings. Shared files used by other versions are kept.'],['由原啟動器管理，無法從這裡刪除','由原启动器管理，无法从这里删除','Managed by the original launcher; cannot be deleted here'],['一鍵匯入已安裝遊戲的 Mods 資料夾','一键导入已安装游戏的 Mods 文件夹','Import to an installed game’s Mods folder'],['下載到系統 Downloads 資料夾','下载到系统 Downloads 文件夹','Download to system Downloads folder'],['下載 .mrpack 到系統 Downloads 資料夾','下载 .mrpack 到系统 Downloads 文件夹','Download .mrpack to Downloads'],['一鍵匯入為獨立遊戲實例','一键导入为独立游戏实例','Import as an isolated game instance'],['請先選擇要匯入的遊戲版本。','请先选择要导入的游戏版本。','Choose a target game before importing.'],['外部遊戲的載入器尚未辨識；請在「載入器」選擇該遊戲實際使用的 Fabric、Forge、NeoForge 或 Quilt。','外部游戏的加载器尚未识别；请在“加载器”中选择该游戏实际使用的 Fabric、Forge、NeoForge 或 Quilt。','The external game’s loader is unknown. Choose the actual Fabric, Forge, NeoForge, or Quilt loader.'],['整合包會依自己的遊戲版本與載入器建立獨立實例；只有 Vanilla／Fabric .mrpack 支援一鍵匯入。','整合包会按其游戏版本和加载器创建独立实例；只有 Vanilla／Fabric .mrpack 支持一键导入。','Modpacks create isolated instances using their game version and loader. One-click import supports Vanilla / Fabric .mrpack only.'],['沒有找到結果。試試其他關鍵字、Minecraft 版本或載入器。','没有找到结果。试试其他关键词、Minecraft 版本或加载器。','No results found. Try another keyword, Minecraft version, or loader.'],['沒有提供簡介。','没有提供简介。','No description provided.'],['查看支援版本','查看支持版本','View Supported Versions'],['沒有符合所選篩選的版本；修改版本或載入器後再查看。','没有符合所选筛选的版本；修改版本或加载器后再查看。','No versions match these filters. Change the game version or loader and try again.'],['未命名版本','未命名版本','Unnamed version'],['未標示遊戲版本','未标注游戏版本','Game version not specified'],['未標示載入器','未标注加载器','Loader not specified'],['選擇此整合包版本','选择此整合包版本','Select this modpack version'],['下載此 Mod 版本','下载此 Mod 版本','Download this Mod version'],['取消工作','取消任务','Cancel Task'],['遊戲執行中','游戏运行中','Game Running'],['開始遊戲 ▶','开始游戏 ▶','Play ▶'],['本機已連接','本地已连接','Connected locally'],['遊戲資料夾','游戏文件夹','Game Folder'],['原版','原版','Vanilla'],[' 個實例',' 个实例',' instances'],['外部資料夾','外部文件夹','External folder'],['每個 MambaCraft 實例使用獨立的世界與 Mods。','每个 MambaCraft 实例使用独立的世界与 Mods。','Each MambaCraft instance has its own worlds and Mods.'],['Minecraft Java 程序仍在執行。若只有音效、沒有遊戲視窗，等 20 秒後到「日誌與支援」匯出診斷包；若 JVM 原生崩潰，診斷包會包含 hs_err 報告。','Minecraft Java 程序仍在运行。如果只有音效、没有游戏窗口，等待 20 秒后到“日志与支持”导出诊断包；如果 JVM 原生崩溃，诊断包会包含 hs_err 报告。','Minecraft Java is still running. If you hear audio but see no window, wait 20 seconds, then export diagnostics from Logs & Support. JVM native crash reports are included.'],['每個版本使用獨立存檔。','每个版本使用独立存档。','Each version has separate saves.'],['遊戲已正常結束','游戏已正常结束','Game exited normally'],['可以再次啟動，或備份這個實例。','可以再次启动，或备份此实例。','You can launch again or back up this instance.'],['Minecraft 已結束（代碼 ','Minecraft 已结束（代码 ','Minecraft exited (code '],['）。請到「日誌與支援」查看原因。','）。请到“日志与支持”查看原因。','). Check Logs & Support for details.'],['連線中斷','连接中断','Connection lost'],['；如果已結束啟動器，重新開啟 MambaCraft.app。','；如果已退出启动器，请重新打开 MambaCraft.app。','; if you quit the launcher, reopen MambaCraft.app.'],['無法儲存外觀設定：','无法保存外观设置：','Could not save appearance setting: '],['已結束','已退出','Closed'],['啟動器已結束，可以關閉這個分頁。','启动器已退出，可以关闭此标签页。','The launcher has quit. You can close this tab.'],['請從 MambaCraft.app 或 Start.command 打開這個介面。','请从 MambaCraft.app 或 Start.command 打开此界面。','Open this page from MambaCraft.app or Start.command.'],['外部資料夾：','外部文件夹：','External folder: '],['來源：','来源：','Source: '],['；世界使用原資料夾。修復請使用原啟動器。','；世界使用原文件夹。请使用原启动器修复。','; worlds remain in the original folder. Use the original launcher to repair.'],['沒有相符的官方版本','没有匹配的官方版本','No matching official versions'],['更新版本清單失敗：','更新版本列表失败：','Version catalog update failed: '],['目前已快取的版本仍可使用。','当前缓存版本仍可使用。','Cached versions remain available.'],['無法儲存語言設定：','无法保存语言设置：','Could not save language setting: '],['找不到相容的 Minecraft 版本。','找不到兼容的 Minecraft 版本。','No compatible Minecraft version found.']
 ];
 rows.push(...[["▤　遊戲版本", "▤　游戏版本", "▤　Game Versions"], ["▧　世界存檔", "▧　世界存档", "▧　World Saves"], ["⬇　資源", "⬇　资源", "⬇　Resources"], ["世界存檔", "世界存档", "World Saves"], ["遊戲版本", "游戏版本", "Game Versions"], ["資源", "资源", "Resources"], ["日誌與支援", "日志与支持", "Logs & Support"], ["核心已就緒", "核心已就绪", "Runtime ready"], ["首次啟動會準備核心", "首次启动会准备核心", "Runtime is prepared on first launch"], ["選擇已安裝版本", "选择已安装版本", "Choose an installed version"], ["新增遊戲版本", "新增游戏版本", "Add a game version"], ["啟動環境與資料位置", "启动环境与数据位置", "Runtime and file locations"], ["複製路徑", "复制路径", "Copy path"], ["已複製路徑。", "已复制路径。", "Path copied."], ["尚未建立", "尚未创建", "Not created yet"], ["遊戲檔案", "游戏文件", "Game files"], ["世界與資源位置", "世界与资源位置", "Worlds and content location"], ["安裝位置", "安装位置", "Installation location"], ["移除版本", "移除版本", "Remove version"], ["世界存檔位置", "世界存档位置", "World saves location"], ["備份儲存位置", "备份保存位置", "Backup location"], ["資源包位置", "资源包位置", "Resource pack location"], ["行為包位置", "行为包位置", "Behavior pack location"], ["外部／共用資料位置", "外部／共用数据位置", "External / shared data folder"], ["世界備份", "世界备份", "World backups"], ["遊戲日誌", "游戏日志", "Game log"], ["啟動器日誌", "启动器日志", "Launcher logs"], ["遊戲版本安裝位置", "游戏版本安装位置", "Game version installation folder"], ["基岩版核心", "基岩版核心", "Bedrock runtime"], ["資源檔案 HTTPS 直連", "资源文件 HTTPS 直连", "Direct HTTPS resource link"], ["下載並安裝資源", "下载并安装资源", "Download and install content"], ["選擇資源檔案…", "选择资源文件…", "Choose content file…"], ["探索 Minecraft 附加包 ↗", "探索 Minecraft 附加包 ↗", "Explore Minecraft Add-Ons ↗"], ["下載日誌 .txt", "下载日志 .txt", "Download log .txt"], ["材質、音效與外觀。", "材质、音效与外观。", "Textures, sounds and appearance."], ["生物、配方與遊戲行為。", "生物、配方与游戏行为。", "Entities, recipes and game behavior."], ["選好已安裝的版本，即可啟動。所需核心會自動準備，每個版本各有獨立世界。", "选好已安装的版本，即可启动。所需核心会自动准备，每个版本各有独立世界。", "Choose an installed version and launch. The runtime is prepared automatically; each version has separate worlds."], ["首次啟動會自動下載及校驗核心；亦可先按下方按鈕準備。", "首次启动会自动下载并校验核心；也可先按下方按钮准备。", "First launch downloads and verifies the runtime automatically. You can also prepare it below."], ["選擇版本，查看它的世界與完整存檔路徑。備份前請先儲存並退出遊戲。", "选择版本，查看它的世界与完整存档路径。备份前请先保存并退出游戏。", "Choose a version to view its worlds and full save paths. Save and quit the game before backing up."], ["新增不同版本，並在「開始遊戲」隨時切換。版本檔案與世界存檔各自保存。", "添加不同版本，并在“开始游戏”随时切换。版本文件和世界存档分别保存。", "Install multiple versions and switch on the Play page. Game files and world saves are stored separately."], ["下載或匯入基岩版附加包、資源包與行為包。Java Mods 不適用於此頁。", "下载或导入基岩版附加包、资源包和行为包。Java Mods 不适用于此页。", "Download or import Bedrock add-ons, resource packs and behavior packs. Java Mods are not supported here."], ["支援 .mcpack、.mcaddon 及含 manifest 的 ZIP。安裝後，請在遊戲內的世界設定啟用所需資源包與行為包。", "支持 .mcpack、.mcaddon 及含 manifest 的 ZIP。安装后，请在游戏内的世界设置启用所需资源包与行为包。", "Supports .mcpack, .mcaddon and ZIP packages with manifests. After installation, activate the resource and behavior packs in your world settings in-game."], ["下載入口由你提供；沒有內建可直接下載的資源目錄。", "下载链接由你提供；没有内置可直接下载的资源目录。", "Provide your own download link. There is no built-in catalog with direct downloads."], ["啟動失敗時，先讀取遊戲日誌。下方列出實際檔案位置，方便尋找和提供錯誤資料。", "启动失败时，先读取游戏日志。下方列出实际文件位置，方便查找和提供错误信息。", "If launch fails, read the game log. The actual file locations below help you find and share error details."], ["核心相容範圍只代表可嘗試啟動，實際遊玩仍需在你的 Mac 驗證。較新版本可安裝管理，尚未開放啟動。", "核心兼容范围只代表可尝试启动，实际游玩仍需在你的 Mac 验证。较新版本可安装管理，尚未开放启动。", "A supported version range permits a launch attempt; playability still needs validation on your Mac. Newer versions can be installed and managed but cannot be launched yet."], ["尚未安裝遊戲。請先新增遊戲版本。", "尚未安装游戏。请先添加游戏版本。", "No game installed. Add a game version first."], ["此版本可管理，但目前核心尚未開放啟動。", "此版本可管理，但当前核心尚未开放启动。", "This version can be managed, but the runtime does not support launching it yet."], ["這個版本尚未建立世界。進入遊戲建立世界後，按「重新掃描」。", "这个版本尚未创建世界。进入游戏创建世界后，点击“重新扫描”。", "No worlds for this version yet. Create a world in-game, then rescan."], ["這個版本尚未安裝此類資源。", "这个版本尚未安装此类资源。", "No content of this type installed for this version."], ["請貼上有效的 HTTPS 資源檔案直連。", "请粘贴有效的 HTTPS 资源文件直连。", "Paste a valid direct HTTPS content link."], ["只移除遊戲程式，保留世界與資源。繼續？", "仅移除游戏程序，保留世界和资源。继续？", "Remove the game files and keep worlds and content. Continue?"], ["無法自動複製，請選取畫面上的完整路徑後複製。", "无法自动复制，请选中屏幕上的完整路径后复制。", "Could not copy automatically. Select and copy the full path shown on screen."], ["無法讀取內容，請重新掃描。", "无法读取内容，请重新扫描。", "Could not read content. Rescan to try again."]]);
 rows.push(...[["檢視外部遊戲資料夾…", "查看外部游戏文件夹…", "View external game folder…"], ["檔案格式與進階說明", "文件格式与进阶说明", "File formats and advanced help"], ["選擇已下載的遊戲安裝檔，版本會自動辨識；不用手動改檔名。", "选择已下载的游戏安装文件，版本会自动识别；无需手动更改文件名。", "Choose a downloaded game package. The version is detected automatically; no renaming is needed."], ["貼上連結下載並安裝", "粘贴链接下载并安装", "Paste a link to download and install"], ["完整性驗證（選填）", "完整性验证（选填）", "Integrity verification (optional)"]]);
 rows.push(...[["查看啟動錯誤", "查看启动错误", "View launch error"], ["此版本相容性尚未驗證，可以按「開始遊戲」嘗試啟動。", "此版本兼容性尚未验证，可以点击“开始游戏”尝试启动。", "Compatibility is unverified. Click Play to attempt launching this version."], ["此版本缺少適合這台 Mac 的遊戲檔案。", "此版本缺少适合这台 Mac 的游戏文件。", "This version is missing game files for this Mac."], ["此版本相容性尚未驗證。安裝後，架構與檔案完整即可嘗試啟動。", "此版本兼容性尚未验证。安装后，架构匹配且文件完整即可尝试启动。", "Compatibility is unverified. After installation, you can attempt launch if the architecture and files match."], ["架構與遊戲檔案符合即可啟動；相容性未驗證的版本會標示提醒。若啟動失敗，日誌會記錄實際錯誤。", "架构和游戏文件匹配即可启动；兼容性未验证的版本会标注提醒。如果启动失败，日志会记录实际错误。", "Versions with matching architecture and game files can launch. Unverified compatibility is labeled; launch failures are recorded in the log."], ["此索引僅供參考，不代表有對應下載來源。安裝包會決定版本；架構與檔案符合即可嘗試啟動。", "此索引仅供参考，不代表有相应下载来源。安装包决定版本；架构和文件匹配即可尝试启动。", "This index is a reference, not a download source. The package determines the version; matching architecture and files allow a launch attempt."]]);
 rows.push(...[["準備相容補丁", "准备兼容补丁", "Prepare compatibility patch"], ["相容補丁位置", "兼容补丁位置", "Compatibility patch folder"], ["相容補丁已準備；啟動時會驗證並載入。", "兼容补丁已准备；启动时会验证并加载。", "Compatibility patch prepared; verified and loaded at launch."], ["首次啟動會自動下載並準備相容補丁。", "首次启动会自动下载并准备兼容补丁。", "The compatibility patch is downloaded and prepared on first launch."]]);
 rows.push(...[
  ['使用直接連結或本機檔案安裝','使用直接链接或本地文件安装','Install from a direct link or local file'],
  ['BEDROCK ADD-ONS','BEDROCK ADD-ONS','BEDROCK ADD-ONS'],['探索基岩版資源','探索基岩版资源','Discover Bedrock Content'],['瀏覽 MCPEDL ↗','浏览 MCPEDL ↗','Browse MCPEDL ↗'],
  ['搜尋附加包、資源包或行為包','搜索附加包、资源包或行为包','Search add-ons, resource packs or behavior packs'],
  ['例如：better on bedrock、shader、動物','例如：better on bedrock、shader、动物','e.g. Better on Bedrock, shader, animals'],['搜尋 MCPEDL ↗','搜索 MCPEDL ↗','Search MCPEDL ↗'],
  ['搜尋結果會在瀏覽器開啟 MCPEDL 官方頁面，下載時保留作者提供的連結與流程。','搜索结果会在浏览器打开 MCPEDL 官方页面，下载时保留作者提供的链接与流程。','Search results open on MCPEDL. Downloads follow the links and steps provided by each creator.'],
  ['下載完成後自動匯入 .mcpack／.mcaddon','下载完成后自动导入 .mcpack／.mcaddon','Automatically import completed .mcpack / .mcaddon downloads'],
  ['啟用後，MambaCraft 會監看 Downloads 內的新附加包。','启用后，MambaCraft 会监视 Downloads 中的新附加包。','When enabled, MambaCraft watches Downloads for new add-ons.'],
  ['自動匯入至目前選取的 MambaCraft 版本；原始下載檔會保留。匯入後仍需在世界設定中啟用資源包或行為包。','自动导入到当前选择的 MambaCraft 版本；原始下载文件会保留。导入后仍需在世界设置中启用资源包或行为包。','Imports to the selected MambaCraft version and keeps the original download. Activate the packs in your world settings afterward.'],
  ['資源與行為包儲存位置','资源与行为包保存位置','Resource and behavior pack locations'],['版本位置與管理','版本位置与管理','Version locations and management'],
  ['可啟動','可启动','Ready to launch'],['暫不支援啟動','暂不支持启动','Launch unavailable'],['開始遊戲 ▶','开始游戏 ▶','Play ▶'],['存檔與資源','存档与资源','Worlds & Content'],['開啟遊戲資料夾','打开游戏文件夹','Open game folder'],
  ['監看 Downloads 的新 .mcpack／.mcaddon 檔案。','监视 Downloads 中的新 .mcpack／.mcaddon 文件。','Watching Downloads for new .mcpack / .mcaddon files.'],['自動匯入目前關閉。','自动导入当前已关闭。','Automatic import is off.'],
  ['基岩版仍在執行；退出遊戲後會自動匯入。','基岩版仍在运行；退出游戏后会自动导入。','Bedrock is running. The add-on will import after you exit the game.'],
  ['請先選擇已安裝的 MambaCraft 版本。','请先选择已安装的 MambaCraft 版本。','Choose an installed MambaCraft version first.'],
  ['瀏覽器封鎖了新分頁，請按「瀏覽 MCPEDL」後再搜尋。','浏览器阻止了新标签页，请点击“浏览 MCPEDL”后再搜索。','The browser blocked a new tab. Open MCPEDL and search there.']
 ]);
 const messages=new Map(rows.map(([source,simplified,english])=>[source,{'zh-Hans':simplified,en:english}]));
 for(const [source,simplified,english] of [
  ['Java 帳號中心','Java 账号中心','Java Account Center'],
  ['選擇遊戲身份；不同帳號的世界玩家資料可能不同。','选择游戏身份；不同账号的世界玩家数据可能不同。','Choose a game identity. World player data may differ between accounts.'],
  ['尚未加入皮膚站帳號。','尚未添加皮肤站账号。','No skin site accounts have been added.'],
  ['目前使用','当前使用','In use'],['使用此帳號','使用此账号','Use Account'],['移除帳號','移除账号','Remove Account'],['移除此皮膚站帳號？','移除此皮肤站账号？','Remove this skin site account?'],['移除此皮膚站帳號？登入憑證會從這部 Mac 的鑰匙圈移除；皮膚站帳號及世界存檔不會被刪除。','移除此皮肤站账号？登录凭证会从这台 Mac 的钥匙串中移除；皮肤站账号及世界存档不会被删除。','Remove this skin site account? Its saved sign-in will be removed from this Mac’s Keychain. The skin site account and world saves will remain.'],['刪除此玩家','删除此玩家','Delete Player'],['至少保留一個本地玩家。','至少保留一个本地玩家。','Keep at least one local player.'],['找不到已儲存的本地玩家。','找不到已保存的本地玩家。','Could not find the saved local player.'],['至少要保留一個本地玩家。','至少要保留一个本地玩家。','At least one local player must remain.'],['刪除只會移除啟動器儲存的玩家名稱，不會刪除世界或世界內的玩家資料。至少保留一個本地玩家。','删除只会移除启动器保存的玩家名称，不会删除世界或世界内的玩家数据。至少保留一个本地玩家。','Deleting only removes the saved launcher player name. Worlds and in-world player data stay intact. Keep at least one local player.'],['刪除本地玩家「{name}」？這只會移除啟動器儲存的玩家名稱，不會刪除世界或世界內的玩家資料。','删除本地玩家“{name}”？这只会移除启动器保存的玩家名称，不会删除世界或世界内的玩家数据。','Delete local player “{name}”? This only removes its saved launcher name; worlds and in-world player data will remain.'],
  ['Microsoft 正版帳號','Microsoft 正版账号','Microsoft Account'],['正版登入與官方皮膚上傳即將提供。','正版登录与官方皮肤上传即将提供。','Microsoft sign-in and official skin uploads are planned.'],['等待接入','等待接入','Coming later'],
  ['皮膚站帳號','皮肤站账号','Skin Site Account'],['支援 LittleSkin 與相容的自訂驗證站。','支持 LittleSkin 与兼容的自定义验证站。','Supports LittleSkin and compatible custom authentication servers.'],['新增皮膚站帳號','添加皮肤站账号','Add Skin Site Account'],
  ['皮膚站來源','皮肤站来源','Skin Site'],['自訂皮膚站','自定义皮肤站','Custom Skin Site'],['皮膚站 HTTPS 網址','皮肤站 HTTPS 地址','Skin Site HTTPS Address'],['確認皮膚站','确认皮肤站','Check Skin Site'],
  ['確認網址後，帳號和密碼只會傳送至此皮膚站。','确认地址后，账号和密码只会发送给此皮肤站。','After you confirm the address, your account and password are sent only to this skin site.'],['皮膚站密碼','皮肤站密码','Skin Site Password'],['登入皮膚站','登录皮肤站','Sign In'],['選擇遊戲角色','选择游戏角色','Choose a Game Profile'],['使用此角色','使用此角色','Use This Profile'],
  ['皮膚站登入使用獨立遊戲身份；多人伺服器須支援該驗證站。','皮肤站登录使用独立游戏身份；多人服务器须支持该验证站。','Skin site accounts use a separate game identity. Multiplayer servers must support that authentication server.'],
  ['前往 LittleSkin 註冊或管理皮膚 ↗','前往 LittleSkin 注册或管理皮肤 ↗','Open LittleSkin to register or manage skins ↗'],['已更新帳號。','已更新账号。','Account updated.'],['皮膚站帳號已加入。','皮肤站账号已添加。','Skin site account added.'],
  ['請輸入有效的公開 HTTPS 皮膚站網址。','请输入有效的公开 HTTPS 皮肤站地址。','Enter a valid public HTTPS skin site address.'],['無法讀取鑰匙圈中的登入資料，請重新登入。','无法读取钥匙串中的登录数据，请重新登录。','Could not read credentials from Keychain. Sign in again.'],
  ['無法儲存登入資料到 macOS 鑰匙圈。','无法将登录数据保存到 macOS 钥匙串。','Could not save credentials to macOS Keychain.'],['無法從鑰匙圈移除登入資料。','无法从钥匙串中移除登录数据。','Could not remove credentials from Keychain.'],
  ['皮膚站要求重新導向登入，為保護登入資料已停止。','皮肤站要求重定向登录；为保护登录数据，操作已停止。','The skin site requested a login redirect. The request was stopped to protect your credentials.'],
  ['皮膚站登入資料無效或已過期，請重新登入。','皮肤站登录数据无效或已过期，请重新登录。','The skin site credentials are invalid or expired. Sign in again.'],['皮膚站暫時無法處理要求，請稍後重試。','皮肤站暂时无法处理请求，请稍后重试。','The skin site could not process the request. Try again later.'],
  ['皮膚站回應格式不正確。','皮肤站响应格式不正确。','The skin site returned an invalid response.'],['皮膚站回應過大。','皮肤站响应过大。','The skin site response is too large.'],['無法連線皮膚站，請檢查網址與網絡。','无法连接皮肤站，请检查地址和网络。','Could not connect to the skin site. Check the address and network.'],
  ['皮膚站重新導向不完整。','皮肤站重定向信息不完整。','The skin site redirect is incomplete.'],['找不到相容的 Yggdrasil 驗證服務。','找不到兼容的 Yggdrasil 验证服务。','No compatible Yggdrasil authentication service was found.'],['皮膚站重新導向過多。','皮肤站重定向次数过多。','The skin site redirected too many times.'],
  ['皮膚站沒有可用的遊戲角色。','皮肤站没有可用的游戏角色。','This skin site account has no game profiles.'],['皮膚站回傳的角色資料不正確。','皮肤站返回的角色数据不正确。','The skin site returned invalid profile data.'],['皮膚站確認已過期，請重新確認網址。','皮肤站确认已过期，请重新确认地址。','The skin site confirmation expired. Check the address again.'],['請輸入皮膚站帳號和密碼。','请输入皮肤站账号和密码。','Enter the skin site account and password.'],
  ['角色選擇已過期，請重新登入。','角色选择已过期，请重新登录。','Profile selection expired. Sign in again.'],['請選擇有效的皮膚站角色。','请选择有效的皮肤站角色。','Choose a valid skin site profile.'],['請重新登入以選擇其他角色。','请重新登录以选择其他角色。','Sign in again to choose another profile.'],['找不到皮膚站帳號，請重新登入。','找不到皮肤站账号，请重新登录。','Skin site account not found. Sign in again.'],['正在下載並校驗皮膚站登入元件…','正在下载并校验皮肤站登录组件…','Downloading and verifying the skin site authentication component…'],
  ['目前支援本機與皮膚站帳號；Microsoft 正版登入、Realms 與正版驗證伺服器連線尚未提供。','目前支持本地和皮肤站账号；Microsoft 正版登录、Realms 和正版验证服务器连接尚未提供。','Local and skin site accounts are supported. Microsoft sign-in, Realms and authenticated official servers are not available yet.']
 ])messages.set(source,{'zh-Hans':simplified,en:english});
 for(const [source,simplified,english] of [['文','文','文'],['安裝版本','安装版本','Install Version'],['Mods 與整合包','Mods 与整合包','Mods & Modpacks'],['已安裝','已安装','Installed'],['Modrinth 作者','Modrinth 作者','Modrinth author'],['（載入器待選）','（加载器待选）','(choose loader)'],['Alpha／更早期','Alpha／更早期','Alpha / Earlier']])messages.set(source,{'zh-Hans':simplified,en:english});
 const extraRows=[
  ["BEDROCK EDITION MANAGER","BEDROCK EDITION MANAGER","BEDROCK EDITION MANAGER"],
  ["YOUR INSTALLED GAMES","已安装的游戏","YOUR INSTALLED GAMES"],
  ["BEDROCK EDITION · LOCAL MANAGEMENT","基岩版 · 本地管理","BEDROCK EDITION · LOCAL MANAGEMENT"],
  ["基岩版管理","基岩版管理","Bedrock Management"],
  ["1.2.5 RC18 修正基岩版版本卡片自動收合，改善 MCPEDL／苦力怕論壇資源搜尋與附加包匯入，並補齊繁體中文、簡體中文和英文的錯誤及狀態翻譯。","1.2.5 RC18 修复基岩版版本卡片自动收起，改进 MCPEDL／苦力怕论坛资源搜索与附加包导入，并补齐繁体中文、简体中文和英文的错误及状态翻译。","Version 1.2.5 RC18 fixes Bedrock version cards collapsing, improves MCPEDL / KLPBBS content discovery and add-on import, and completes error and status translations in Traditional Chinese, Simplified Chinese and English."],
  ["你的空間 / 基岩版管理","你的空间 / 基岩版管理","Your space / Bedrock Management"],
  ["管理這台 Mac 上已安裝的 mcpelauncher 版本、世界與資源包。此頁只讀取本機檔案；遊戲版本取得與啟動由上游啟動器處理。","管理这台 Mac 上已安装的 mcpelauncher 版本、世界与资源包。此页面只读取本地文件；游戏版本获取与启动由上游启动器处理。","Manage mcpelauncher versions, worlds, and packs already on this Mac. This page only reads local files; the upstream launcher handles game acquisition and launch."],
  ["資料根目錄","数据根目录","Data root"],["正在檢查…","正在检查…","Checking…"],["正在掃描…","正在扫描…","Scanning…"],
  ["開啟上游啟動器","打开上游启动器","Open upstream launcher"],["開啟資料根目錄","打开数据根目录","Open data root"],
  ["選擇資料位置…","选择数据位置…","Choose data folder…"],["使用預設位置","使用默认位置","Use default location"],["重新掃描 ↻","重新扫描 ↻","Rescan ↻"],
  ["本機未找到 Minecraft Bedrock Launcher.app 時，請先自行安裝上游 mcpelauncher，再設定其資料根目錄。","本地未找到 Minecraft Bedrock Launcher.app 时，请先自行安装上游 mcpelauncher，再设置其数据根目录。","If Minecraft Bedrock Launcher.app is not found, install the upstream mcpelauncher yourself and set its data root."],
  ["已安裝版本","已安装版本","Installed versions"],["世界","世界","Worlds"],["資源包","资源包","Resource packs"],["行為包","行为包","Behavior packs"],
  ["開啟資料夾","打开文件夹","Open folder"],["備份 .mcworld","备份 .mcworld","Back up .mcworld"],
  ["本機未找到 Minecraft Bedrock Launcher.app 時，請先自行安裝上游 mcpelauncher，再設定其資料根目錄。","本地未找到 Minecraft Bedrock Launcher.app 时，请先自行安装上游 mcpelauncher，再设置其数据根目录。","If Minecraft Bedrock Launcher.app is not found, install the upstream mcpelauncher yourself and set its data root."],
  ["mcpelauncher 不隨 MambaCraft 打包。請使用自己有權取得的遊戲版本；本管理頁不提供 APK 搜尋、下載或匯入。","mcpelauncher 不随 MambaCraft 打包。请使用自己有权获取的游戏版本；本管理页不提供 APK 搜索、下载或导入。","mcpelauncher is not bundled. Use game versions you are authorized to obtain; this manager does not search for, download, or import APKs."],
  ["自訂資料位置已不存在，請重新選擇資料夾。","自定义数据位置已不存在，请重新选择文件夹。","The custom data folder no longer exists. Choose it again."],
  ["已找到本機 mcpelauncher 資料。","已找到本地 mcpelauncher 数据。","Local mcpelauncher data was found."],
  ["預設資料夾尚未建立；可安裝上游啟動器或自行選擇資料位置。","默认文件夹尚未创建；可安装上游启动器或自行选择数据位置。","The default folder does not exist yet. Install the upstream launcher or choose a data folder."],
  ["沒有找到已安裝版本。","没有找到已安装版本。","No installed versions found."],["目前沒有可列出的版本。","目前没有可列出的版本。","There are no versions to show."],
  ["沒有找到世界。","没有找到世界。","No worlds found."],["目前沒有可列出的世界。","目前没有可列出的世界。","There are no worlds to show."],
  ["目前沒有資源包。","目前没有资源包。","No resource packs installed."],["目前沒有行為包。","目前没有行为包。","No behavior packs installed."],
  ["架構資訊未能判定","架构信息无法判断","Architecture not detected"],
  ["請先退出 Bedrock。MambaCraft 會在本機建立一份 .mcworld 備份。繼續？","请先退出 Bedrock。MambaCraft 会在本地创建一份 .mcworld 备份。继续？","Quit Bedrock first. MambaCraft will create a local .mcworld backup. Continue?"],
  ["讀取失敗，請確認 Helper 已更新後重試。","读取失败，请确认 Helper 已更新后重试。","Could not read data. Confirm the helper is up to date and try again."],
  ["mcpelauncher 的資料根目錄，也可以選 versions 或 games/com.mojang 子資料夾。","mcpelauncher 的数据根目录，也可以选择 versions 或 games/com.mojang 子文件夹。","mcpelauncher data root; you may also choose its versions or games/com.mojang folder."],
  ["已恢復 mcpelauncher 預設資料位置。","已恢复 mcpelauncher 默认数据位置。","Restored the default mcpelauncher data folder."],
  ["Bedrock 資料夾路徑不合法。","Bedrock 文件夹路径无效。","The Bedrock folder path is invalid."],
  ["所選位置不是資料夾。","所选位置不是文件夹。","The selected path is not a folder."],
  ["未知的 Bedrock 資料夾。","未知的 Bedrock 文件夹。","Unknown Bedrock folder."],
  ["資料夾識別資料不合法。","文件夹标识无效。","The folder identifier is invalid."],
  ["找不到這個資料夾，請重新掃描。","找不到此文件夹，请重新扫描。","Folder not found. Rescan and try again."],
  ["找不到這個資料夾，請確認 mcpelauncher 已安裝並重新掃描。","找不到此文件夹，请确认已安装 mcpelauncher 并重新扫描。","Folder not found. Confirm mcpelauncher is installed and rescan."],
  ["開啟 Finder 資料夾只適用於 macOS。","打开 Finder 文件夹仅适用于 macOS。","Opening folders in Finder is only available on macOS."],
  ["開啟 macOS Bedrock Launcher 只適用於 macOS。","打开 macOS Bedrock Launcher 仅适用于 macOS。","Opening the macOS Bedrock Launcher is only available on macOS."],
  ["找不到 Minecraft Bedrock Launcher.app。請先安裝上游啟動器，或確認它位於 /Applications 或 ~/Applications。","找不到 Minecraft Bedrock Launcher.app。请先安装上游启动器，或确认它位于 /Applications 或 ~/Applications。","Minecraft Bedrock Launcher.app was not found. Install it or check /Applications and ~/Applications."],
  ["請先完全退出 Minecraft Bedrock，再備份世界。","请先完全退出 Minecraft Bedrock，再备份世界。","Quit Minecraft Bedrock completely before backing up a world."],
  ["找不到這個世界，請重新掃描。","找不到此世界，请重新扫描。","World not found. Rescan and try again."],
  ["世界資料夾已移動或無法安全讀取。","世界文件夹已移动或无法安全读取。","The world folder moved or cannot be read safely."],
  ["世界備份已建立：","世界备份已创建：","World backup created: "],
  ["已在 Finder 開啟：","已在 Finder 打开：","Opened in Finder: "],
  ["已設定 Bedrock 資料位置：","已设置 Bedrock 数据位置：","Bedrock data folder set to: "],
  ["已交由 Minecraft Bedrock Launcher 開啟。遊戲版本仍由上游啟動器管理。","已交由 Minecraft Bedrock Launcher 打开。游戏版本仍由上游启动器管理。","Opened Minecraft Bedrock Launcher. The upstream launcher manages game versions."],
  ["請先退出 Bedrock。MambaCraft 會在本機建立一份 .mcworld 備份。繼續？","请先退出 Bedrock。MambaCraft 会在本地创建一份 .mcworld 备份。继续？","Quit Bedrock first. MambaCraft will create a local .mcworld backup. Continue?"],
  ["無法讀取 Bedrock 資料：","无法读取 Bedrock 数据：","Could not read Bedrock data: "]
 ];
 for(const [source,simplified,english] of extraRows)messages.set(source,{'zh-Hans':simplified,en:english});
 for(const [source,simplified,english] of [
  ['瀏覽來源網站 ↗','浏览来源网站 ↗','Browse source ↗'],
  ['選擇下載來源','选择下载来源','Choose a source'],
  ['國際來源 · MCPEDL','国际来源 · MCPEDL','International · MCPEDL'],
  ['中國大陸 · 苦力怕論壇','中国大陆 · 苦力怕论坛','Mainland China · KLPBBS'],
  ['搜尋所選來源 ↗','搜索所选来源 ↗','Search selected source ↗'],
  ['基岩版','基岩版','Bedrock'],
  ['https://你的來源/addon.mcaddon','https://你的来源/addon.mcaddon','https://your-source/addon.mcaddon'],
  ['例如 BlackMamba','例如 BlackMamba','e.g. BlackMamba'],
  ['此版本缺少對應架構的遊戲檔案。','此版本缺少对应架构的游戏文件。','This version is missing game files for this architecture.'],
  ['專案頁 ↗','项目页 ↗','Project page ↗'],
  ['Modrinth 官方','Modrinth 官方','Modrinth official'],
  ['MCIM 鏡像','MCIM 镜像','MCIM mirror'],
  ['瀏覽器封鎖了新分頁，請使用上方「瀏覽來源網站」連結。','浏览器阻止了新标签页，请使用上方“浏览来源网站”链接。','Your browser blocked the new tab. Use “Browse source” above.'],
  ['直接下載需要可存取的 HTTPS 檔案連結；也可從上方來源搜尋，下載後自動匯入。','直接下载需要可访问的 HTTPS 文件链接；也可从上方来源搜索，下载后自动导入。','Direct downloads need an accessible HTTPS file link. You can also search the sources above and import the downloaded pack automatically.'],
  ['MCPEDL 提供國際資源搜尋；苦力怕論壇提供中國大陸入口。搜尋結果與下載由來源網站處理，下載完成後可由 MambaCraft 自動匯入。','MCPEDL 提供国际资源搜索；苦力怕论坛提供中国大陆入口。搜索结果和下载由来源网站处理，下载完成后可由 MambaCraft 自动导入。','MCPEDL provides an international catalog; KLPBBS adds a mainland China entry point. Search and downloads stay on the source sites, and MambaCraft can import completed downloads automatically.']
 ])messages.set(source,{'zh-Hans':simplified,en:english});
 for(const [source,simplified,english] of [["準備基岩版核心", "準備基岩版核心", "Set up Bedrock runtime"], ["使用 MambaCraft 資料位置", "使用 MambaCraft 資料位置", "Use MambaCraft data folder"], ["核心尚未準備；按「準備基岩版核心」，由 MambaCraft 自動下載及校驗。", "核心尚未準備；按「準備基岩版核心」，由 MambaCraft 自動下載及校驗。", "The runtime is not ready. Click “Set up Bedrock runtime” to download and verify it automatically."], ["尋找基岩版版本", "尋找基岩版版本", "Find a Bedrock version"], ["更新版本清單", "更新版本清單", "Refresh version catalog"], ["全部版本", "全部版本", "All versions"], ["Minecraft 基岩版版本", "Minecraft 基岩版版本", "Minecraft Bedrock version"], ["讀取基岩版日誌", "讀取基岩版日誌", "Read Bedrock log"], ["下方世界與資源包是所選外部資料根目錄中的內容。由 MambaCraft 啟動的版本各有獨立存檔，請使用版本卡片的「此版本存檔／資源包」與「備份此版本世界」。", "下方世界與資源包是所選外部資料根目錄中的內容。由 MambaCraft 啟動的版本各有獨立存檔，請使用版本卡片的「此版本存檔／資源包」與「備份此版本世界」。", "Worlds and packs below belong to the selected data root. Versions launched by MambaCraft have independent worlds. Use “Version worlds / packs” and “Back up version worlds” on each version card."], ["目前沒有可列出的版本。", "目前沒有可列出的版本。", "No installed versions to show."], ["此版本存檔／資源包", "此版本存檔／資源包", "Version worlds / packs"], ["備份此版本世界", "備份此版本世界", "Back up version worlds"], ["MambaCraft 管理的基岩版資料。", "MambaCraft 管理的基岩版資料。", "Bedrock data managed by MambaCraft."], ["正在檢視外部資料；新安裝請使用 MambaCraft 資料位置。", "正在檢視外部資料；新安裝請使用 MambaCraft 資料位置。", "Viewing external data; use the MambaCraft data folder to install new versions."], ["基岩版核心已就緒", "基岩版核心已就緒", "Bedrock runtime ready"], ["沒有符合條件的版本", "沒有符合條件的版本", "No matching versions"], ["此版本在上游公布的相容範圍內；仍需在你的 Mac 實測。", "此版本在上游公布的相容範圍內；仍需在你的 Mac 實測。", "This version is in the upstream compatibility range; it still needs gameplay testing on your Mac."], ["此版本尚未完成相容性整合；可安裝，但目前未開放啟動。", "此版本尚未完成相容性整合；可安裝，但目前未開放啟動。", "Compatibility integration is not complete for this version. Installation is available; launching is not yet enabled."], ["沒有符合條件的版本。", "沒有符合條件的版本。", "No matching versions."], ["例如 1.20.80 或 1.21", "例如 1.20.80 或 1.21", "e.g. 1.20.80 or 1.21"]])messages.set(source,{'zh-Hans':simplified,en:english});
 const backendRows=[
  ['無效的版本／實例名稱。','无效的版本／实例名称。','Invalid version or instance name.'],
  ['玩家名稱需為 3–16 個英文字母、數字或底線。','玩家名称需为 3–16 个英文字母、数字或下划线。','Player names must use 3–16 English letters, numbers, or underscores.'],
  ['檔案路徑不合法。','文件路径无效。','The file path is invalid.'],
  ['拒絕越界的檔案路徑。','已拒绝超出范围的文件路径。','The file path escapes its allowed location.'],
  ['整合包內含不安全的檔案路徑。','整合包包含不安全的文件路径。','The modpack contains an unsafe file path.'],
  ['無法讀取官方資料。','无法读取官方数据。','Could not read official data.'],
  ['不支援的函式庫名稱。','不支持的库名称。','Unsupported library name.'],
  ['Apple Silicon Objective-C 原生庫目錄為符號連結；已停止啟動。','Apple Silicon Objective-C 原生库目录是符号链接；已停止启动。','The Apple Silicon Objective-C native library folder is a symlink. Launch stopped.'],
  ['這個版本沒有可替換的 LWJGL 2 Java 函式庫。','此版本没有可替换的 LWJGL 2 Java 库。','This version has no LWJGL 2 Java library to replace.'],
  ['這個舊版的 LWJGL 2 元件不完整，為避免混用架構已停止啟動。','此旧版本的 LWJGL 2 组件不完整，为避免混用架构已停止启动。','Legacy LWJGL 2 components are incomplete. Launch stopped to prevent mixing architectures.'],
  ['找不到舊版 LWJGL 2 的 classpath 位置。','找不到旧版 LWJGL 2 的 classpath 位置。','Could not find the legacy LWJGL 2 classpath location.'],
  ['找不到舊版 JNA 的 classpath 位置。','找不到旧版 JNA 的 classpath 位置。','Could not find the legacy JNA classpath location.'],
  ['無法取得 Modrinth 資料。','无法获取 Modrinth 数据。','Could not retrieve Modrinth data.'],
  ['正在下載並校驗整合包…','正在下载并校验整合包…','Downloading and verifying modpack…'],
  ['已取消。已下載且通過校驗的檔案會保留，重試可繼續使用。','已取消。已下载且通过校验的文件会保留，重试时可继续使用。','Cancelled. Verified downloads are kept and can be reused on retry.'],
  ['下載來源不在啟動器固定的相容性來源清單內。','下载来源不在启动器固定的兼容来源列表中。','The download source is not on the launcher’s approved compatibility list.'],
  ['下載來源不在允許的 HTTPS 網域內。','下载来源不在允许的 HTTPS 域名内。','The download source is outside the allowed HTTPS domains.'],
  ['拒絕不安全的下載轉址。','已拒绝不安全的下载重定向。','An unsafe download redirect was blocked.'],
  ['下載重試設定不合法。','下载重试设置无效。','The download retry settings are invalid.'],
  ['下載備援來源不在啟動器固定的 HTTPS 網域清單內。','下载备用来源不在启动器固定的 HTTPS 域名列表中。','The fallback source is not on the launcher’s approved HTTPS domain list.'],
  ['Java 安裝檔無法安全解壓，請按「檢查及修復」重試。','Java 安装文件无法安全解压，请点击“检查并修复”重试。','The Java package could not be extracted safely. Choose Check & Repair to retry.'],
  ['Apple Silicon LWJGL 套件無法讀取；原版遊戲檔未變更。','Apple Silicon LWJGL 包无法读取；原版游戏文件未更改。','Could not read the Apple Silicon LWJGL package. Original game files were not changed.'],
  ['Apple Silicon 舊版相容套件缺少 JNA；請重新解壓縮啟動器。','Apple Silicon 旧版兼容包缺少 JNA；请重新解压启动器。','The legacy Apple Silicon compatibility package is missing JNA. Re-extract the launcher.'],
  ['Apple Silicon 舊版 JNA 套件大小不符；請重新解壓縮啟動器。','Apple Silicon 旧版 JNA 包大小不符；请重新解压启动器。','The legacy Apple Silicon JNA package has an unexpected size. Re-extract the launcher.'],
  ['Apple Silicon 舊版 JNA 套件校驗失敗；請重新解壓縮啟動器。','Apple Silicon 旧版 JNA 包校验失败；请重新解压启动器。','The legacy Apple Silicon JNA package failed verification. Re-extract the launcher.'],
  ['Apple Silicon 舊版 JNA 套件無法讀取；請重新解壓縮啟動器。','Apple Silicon 旧版 JNA 包无法读取；请重新解压启动器。','Could not read the legacy Apple Silicon JNA package. Re-extract the launcher.'],
  ['Apple Silicon 舊版相容套件缺少 Objective-C bridge；請重新解壓縮啟動器。','Apple Silicon 旧版兼容包缺少 Objective-C bridge；请重新解压启动器。','The legacy Apple Silicon compatibility package is missing the Objective-C bridge. Re-extract the launcher.'],
  ['Apple Silicon Objective-C bridge 套件大小不符；請重新解壓縮啟動器。','Apple Silicon Objective-C bridge 包大小不符；请重新解压启动器。','The Apple Silicon Objective-C bridge package has an unexpected size. Re-extract the launcher.'],
  ['Apple Silicon Objective-C bridge 套件校驗失敗；請重新解壓縮啟動器。','Apple Silicon Objective-C bridge 包校验失败；请重新解压启动器。','The Apple Silicon Objective-C bridge package failed verification. Re-extract the launcher.'],
  ['Apple Silicon Objective-C bridge 套件無法讀取；請重新解壓縮啟動器。','Apple Silicon Objective-C bridge 包无法读取；请重新解压启动器。','Could not read the Apple Silicon Objective-C bridge package. Re-extract the launcher.'],
  ['Apple Silicon Objective-C 原生庫是符號連結；已停止啟動。','Apple Silicon Objective-C 原生库是符号链接；已停止启动。','The Apple Silicon Objective-C native library is a symlink. Launch stopped.'],
  ['Apple Silicon Objective-C 原生庫無法安全安裝到遊戲執行目錄；已停止啟動。','Apple Silicon Objective-C 原生库无法安全安装到游戏运行目录；已停止启动。','Could not safely install the Apple Silicon Objective-C library into the game runtime. Launch stopped.'],
  ['這個版本使用尚未支援的啟動參數，已停止啟動。','此版本使用了尚未支持的启动参数，已停止启动。','This version uses unsupported launch arguments. Launch stopped.'],
  ['選取的路徑不是資料夾。','所选路径不是文件夹。','The selected path is not a folder.'],
  ['最多新增 40 個遊戲資料夾。請刪除不再使用的資料夾後重試。','最多添加 40 个游戏文件夹。请删除不再使用的文件夹后重试。','You can add up to 40 game folders. Remove unused folders and try again.'],
  ['記憶體設定不合法。','内存设置无效。','The memory setting is invalid.'],
  ['外觀主題設定不合法。','外观主题设置无效。','The appearance theme setting is invalid.'],
  ['語言設定不合法。','语言设置无效。','The language setting is invalid.'],
  ['遊戲版本管理偏好不合法。','游戏版本管理偏好设置无效。','The game edition preference is invalid.'],
  ['拒絕不安全的 Modrinth API 要求。','已拒绝不安全的 Modrinth API 请求。','An unsafe Modrinth API request was blocked.'],
  ['Modrinth 官方來源與 MCIM 備援均無法連線。請稍後重試，或開啟 Modrinth 專案頁手動下載。','Modrinth 官方来源和 MCIM 备用源均无法连接。请稍后重试，或打开 Modrinth 项目页手动下载。','Neither Modrinth nor the MCIM fallback is reachable. Retry later or download from the Modrinth project page.'],
  ['搜尋類型不合法。','搜索类型无效。','The search type is invalid.'],
  ['搜尋關鍵字最多 120 個字元。','搜索关键词最多 120 个字符。','Search queries may contain up to 120 characters.'],
  ['模組載入器篩選不合法。','模组加载器筛选条件无效。','The mod loader filter is invalid.'],
  ['Modrinth 搜尋回傳格式不完整。','Modrinth 搜索响应格式不完整。','The Modrinth search response is incomplete.'],
  ['搜尋結果已過期；請重新搜尋後再選版本。','搜索结果已过期；请重新搜索后再选择版本。','Search results expired. Search again before choosing a version.'],
  ['Minecraft 版本篩選不合法。','Minecraft 版本筛选条件无效。','The Minecraft version filter is invalid.'],
  ['Modrinth 版本資料格式不完整。','Modrinth 版本数据格式不完整。','The Modrinth version data is incomplete.'],
  ['這個檔案不在啟動器允許的 Modrinth CDN；請從專案頁面手動下載。','此文件不在启动器允许的 Modrinth CDN 上；请从项目页手动下载。','This file is not on an approved Modrinth CDN. Download it from the project page.'],
  ['來源未提供有效 SHA-1／SHA-512，為保護遊戲檔案已停止下載。','来源未提供有效 SHA-1／SHA-512；为保护游戏文件，已停止下载。','The source did not provide a valid SHA-1 / SHA-512 checksum. Download stopped to protect game files.'],
  ['來源檔案大小不合法或超過安全上限。','来源文件大小无效或超过安全上限。','The source file size is invalid or exceeds the safety limit.'],
  ['系統 Downloads 路徑不是資料夾。','系统 Downloads 路径不是文件夹。','The system Downloads path is not a folder.'],
  ['同名檔案過多，請清理下載資料夾後重試。','同名文件过多，请清理下载文件夹后重试。','Too many files share this name. Clean up Downloads and try again.'],
  ['搜尋結果已過期；請重新搜尋並選擇版本。','搜索结果已过期；请重新搜索并选择版本。','Search results expired. Search again and choose a version.'],
  ['所選項目不是 Mod。','所选项目不是 Mod。','The selected project is not a Mod.'],
  ['下載目的地不合法。','下载目标无效。','The download destination is invalid.'],
  ['所選版本不是 JAR Mod；請在專案頁面確認下載檔案。','所选版本不是 JAR Mod；请在项目页确认下载文件。','The selected version is not a JAR Mod. Check the file on its project page.'],
  ['搜尋結果已過期；請重新搜尋並選擇整合包版本。','搜索结果已过期；请重新搜索并选择整合包版本。','Search results expired. Search again and choose a modpack version.'],
  ['所選項目不是整合包。','所选项目不是整合包。','The selected project is not a modpack.'],
  ['所選檔案不是 .mrpack 整合包；請開啟專案頁面手動下載。','所选文件不是 .mrpack 整合包；请打开项目页手动下载。','The selected file is not a .mrpack modpack. Download it from the project page.'],
  ['目前一鍵匯入只支援 Modrinth .mrpack；請改存到 Downloads 再用原平台匯入。','目前一键导入仅支持 Modrinth .mrpack；请保存到 Downloads，再用原平台导入。','One-click import currently supports Modrinth .mrpack only. Save it to Downloads and import with its original launcher.'],
  ['暫存目錄路徑不安全。','临时目录路径不安全。','The temporary directory path is unsafe.'],
  ['版本伺服器回傳資料不完整。','版本服务器返回的数据不完整。','The version server returned incomplete data.'],
  ['請先更新版本清單，再選擇正式版、快照或舊版本。','请先更新版本列表，再选择正式版、快照或旧版本。','Refresh the version list before choosing a release, snapshot, or legacy version.'],
  ['版本啟動資料不受支援。','版本启动数据不受支持。','The version launch data is unsupported.'],
  ['Apple Silicon Java 8 相容 runtime 只適用於 macOS ARM64。','Apple Silicon Java 8 兼容 runtime 仅适用于 macOS ARM64。','The Apple Silicon Java 8 compatibility runtime is only for macOS ARM64.'],
  ['Java 安裝路徑為符號連結；為保護資料已停止安裝。','Java 安装路径是符号链接；为保护数据已停止安装。','The Java installation path is a symlink. Installation stopped to protect your data.'],
  ['Apple Silicon LWJGL 2 相容層不適用於這個版本或電腦。','Apple Silicon LWJGL 2 兼容层不适用于此版本或电脑。','The Apple Silicon LWJGL 2 compatibility layer does not support this version or computer.'],
  ['Apple Silicon LWJGL Java 函式庫損壞，請按「檢查及修復」重試。','Apple Silicon LWJGL Java 库已损坏，请点击“检查并修复”重试。','The Apple Silicon LWJGL Java library is damaged. Choose Check & Repair to retry.'],
  ['找不到這個外部 Minecraft 安裝。請重新掃描資料夾。','找不到此外部 Minecraft 安装。请重新扫描文件夹。','Could not find this external Minecraft installation. Rescan the folder.'],
  ['不支援的遊戲類型。','不支持的游戏类型。','Unsupported game type.'],
  ['可用空間少於 2 GB，請先清理磁碟。','可用空间不足 2 GB，请先清理磁盘。','Less than 2 GB of free space is available. Free up disk space first.'],
  ['整合包暫存實例名稱衝突，請重試。','整合包临时实例名称冲突，请重试。','The temporary modpack instance name conflicts. Try again.'],
  ['正在準備 Apple Silicon 舊版視窗相容元件…','正在准备 Apple Silicon 旧版窗口兼容组件…','Preparing the legacy Apple Silicon window compatibility component…'],
  ['原啟動器的版本資料已移動。請重新掃描資料夾。','原启动器的版本数据已移动。请重新扫描文件夹。','The original launcher’s version data has moved. Rescan the folder.'],
  ['這是另一個啟動器管理的版本。為保護原有檔案，請用該啟動器修復；也可在 MambaCraft 安裝相同版本。','此版本由其他启动器管理。为保护原有文件，请用该启动器修复；也可在 MambaCraft 安装相同版本。','Another launcher manages this version. Repair it there, or install the same version in MambaCraft.'],
  ['外部版本由原啟動器管理，MambaCraft 不會刪除外部遊戲資料。','外部版本由原启动器管理，MambaCraft 不会删除外部游戏数据。','External versions remain managed by their original launcher; MambaCraft will not delete their data.'],
  ['正在準備並校驗 Apple Silicon 舊版視窗相容元件…','正在准备并校验 Apple Silicon 旧版窗口兼容组件…','Preparing and verifying the legacy Apple Silicon window compatibility component…'],
  ['原生函式庫路徑為符號連結；為保護資料已停止啟動。','原生库路径是符号链接；为保护数据已停止启动。','The native library path is a symlink. Launch stopped to protect your data.'],
  ['開啟 Finder 功能只適用於 macOS。','打开 Finder 的功能仅适用于 macOS。','Opening folders in Finder is only available on macOS.'],
  ['拒絕原生函式庫中的符號連結。','已拒绝原生库中的符号链接。','A symlink in the native library was blocked.'],
  ['Java 安裝檔超出安全解壓限制。','Java 安装文件超过安全解压限制。','The Java package exceeds the safe extraction limit.'],
  ['Apple Silicon 舊版 JNA 原生庫格式無效；請重新解壓縮啟動器。','Apple Silicon 旧版 JNA 原生库格式无效；请重新解压启动器。','The legacy Apple Silicon JNA native library is invalid. Re-extract the launcher.'],
  ['Apple Silicon 舊版 JNA 套件沒有 ARM64 原生庫；已停止啟動。','Apple Silicon 旧版 JNA 包没有 ARM64 原生库；已停止启动。','The legacy Apple Silicon JNA package has no ARM64 native library. Launch stopped.'],
  ['Apple Silicon 舊版 JNA 不相容於 Java 8；已停止啟動。','Apple Silicon 旧版 JNA 与 Java 8 不兼容；已停止启动。','The legacy Apple Silicon JNA is incompatible with Java 8. Launch stopped.'],
  ['Apple Silicon Objective-C bridge 原生庫格式無效；已停止啟動。','Apple Silicon Objective-C bridge 原生库格式无效；已停止启动。','The Apple Silicon Objective-C bridge native library is invalid. Launch stopped.'],
  ['Apple Silicon Objective-C bridge 沒有 ARM64 原生庫；已停止啟動。','Apple Silicon Objective-C bridge 没有 ARM64 原生库；已停止启动。','The Apple Silicon Objective-C bridge has no ARM64 native library. Launch stopped.'],
  ['Apple Silicon Objective-C bridge 缺少必要 Java 類別；已停止啟動。','Apple Silicon Objective-C bridge 缺少必要 Java 类；已停止启动。','The Apple Silicon Objective-C bridge is missing required Java classes. Launch stopped.'],
  ['Apple Silicon Objective-C 原生庫大小或格式無效；已停止啟動。','Apple Silicon Objective-C 原生库大小或格式无效；已停止启动。','The Apple Silicon Objective-C native library has an invalid size or format. Launch stopped.'],
  ['Apple Silicon Objective-C 原生庫不完整或沒有 ARM64 架構；已停止啟動。','Apple Silicon Objective-C 原生库不完整或没有 ARM64 架构；已停止启动。','The Apple Silicon Objective-C native library is incomplete or lacks ARM64. Launch stopped.'],
  ['找不到選取的資料夾。','找不到所选文件夹。','The selected folder could not be found.'],
  ['請等候目前工作或遊戲結束後，再更改 Java 位置。','请等待当前任务或游戏结束后，再更改 Java 位置。','Wait for the current task or game to finish before changing the Java location.'],
  ['請先等候工作／遊戲結束，再更改玩家。','请等待任务／游戏结束后，再更改玩家。','Wait for the task or game to finish before changing the player.'],
  ['請等候目前工作完成。','请等待当前任务完成。','Wait for the current task to finish.'],
  ['已取消搜尋。','已取消搜索。','Search cancelled.'],
  ['Modrinth 官方 API 連線失敗，正在切換中國大陸 MCIM 鏡像…','Modrinth 官方 API 连接失败，正在切换中国大陆 MCIM 镜像…','Could not reach the Modrinth API. Switching to the MCIM mirror…'],
  ['無法建立系統 Downloads 資料夾；請在設定中確認家目錄可寫入。','无法创建系统 Downloads 文件夹；请在设置中确认主目录可写入。','Could not create the system Downloads folder. Check that your home folder is writable.'],
  ['這個 Mod 版本與所選 Minecraft 版本不相容。','此 Mod 版本与所选 Minecraft 版本不兼容。','This Mod version is incompatible with the selected Minecraft version.'],
  ['這個 Mod 版本不支援所選 Fabric 遊戲。','此 Mod 版本不支持所选 Fabric 游戏。','This Mod version does not support the selected Fabric game.'],
  ['原版遊戲沒有 Mods 載入器；請先安裝相容的 Fabric，或選擇已安裝的 Forge／Fabric 遊戲。','原版游戏没有 Mods 加载器；请先安装兼容的 Fabric，或选择已安装的 Forge／Fabric 游戏。','Vanilla has no Mods loader. Install a compatible Fabric version or select an installed Forge / Fabric game.'],
  ['這個 Mod 版本與遊戲載入器不相容。','此 Mod 版本与游戏加载器不兼容。','This Mod version is incompatible with the game loader.'],
  ['目標 Mods 路徑不安全；為保護資料已停止安裝。','目标 Mods 路径不安全；为保护数据已停止安装。','The target Mods path is unsafe. Installation stopped to protect your data.'],
  ['整合包無法安全讀取或寫入；未建立可見的半成品實例。','无法安全读取或写入整合包；未创建可见的半成品实例。','The modpack could not be read or written safely. No partial instance was created.'],
  ['啟動器正在結束，請重新開啟 App。','启动器正在退出，请重新打开 App。','The launcher is shutting down. Reopen the app.'],
  ['已有工作正在進行，請等候或取消。','已有任务正在进行，请等待或取消。','A task is already running. Wait for it or cancel it.'],
  ['遊戲仍在執行；請先儲存世界並正常離開遊戲。','游戏仍在运行；请先保存世界并正常退出游戏。','The game is still running. Save your world and quit normally first.'],
  ['未知操作。','未知操作。','Unknown action.'],
  ['Java 安裝目錄包含符號連結；為保護資料已停止安裝。','Java 安装目录包含符号链接；为保护数据已停止安装。','The Java installation folder contains a symlink. Installation stopped to protect your data.'],
  ['下載的 Java 8 無法在 Apple Silicon 執行，已停止安裝。','下载的 Java 8 无法在 Apple Silicon 上运行，已停止安装。','The downloaded Java 8 cannot run on Apple Silicon. Installation stopped.'],
  ['Java 連結路徑超出安裝範圍。','Java 链接路径超出安装范围。','The Java symlink points outside the installation location.'],
  ['此經典版本不支援 Fabric 安裝；請選 Vanilla。','此经典版本不支持安装 Fabric；请选择 Vanilla。','This legacy version does not support Fabric. Choose Vanilla.'],
  ['Fabric 版本資料不相符。','Fabric 版本数据不匹配。','The Fabric version metadata does not match.'],
  ['函式庫檔案損壞，請重試修復。','库文件已损坏，请重试修复。','A library file is damaged. Try repairing again.'],
  ['素材雜湊格式錯誤。','素材哈希格式错误。','The asset checksum format is invalid.'],
  ['找不到完整安裝的實例，請先安裝。','找不到完整安装的实例，请先安装。','No complete instance was found. Install the game first.'],
  ['遊戲仍在執行；請正常退出後再刪除。','游戏仍在运行；请正常退出后再删除。','The game is still running. Quit normally before deleting it.'],
  ['拒絕刪除包含符號連結的實例路徑。','已拒绝删除包含符号链接的实例路径。','Deletion of an instance path containing a symlink was blocked.'],
  ['實例路徑不在 MambaCraft 管理範圍內。','实例路径不在 MambaCraft 管理范围内。','The instance path is outside MambaCraft’s managed location.'],
  ['實例資料與資料夾不符，為保護資料已停止刪除。','实例数据与文件夹不匹配；为保护数据已停止删除。','Instance metadata does not match the folder. Deletion stopped to protect your data.'],
  ['實例版本資料不完整，無法安全清理。','实例版本数据不完整，无法安全清理。','Instance version data is incomplete and cannot be safely cleaned up.'],
  ['找不到完整的 MambaCraft 實例，未刪除任何資料。','找不到完整的 MambaCraft 实例，未删除任何数据。','No complete MambaCraft instance was found. No data was deleted.'],
  ['原生函式庫路徑不是資料夾；請按「檢查及修復」。','原生库路径不是文件夹；请点击“检查并修复”。','The native library path is not a folder. Choose Check & Repair.'],
  ['Apple Silicon Objective-C bridge 沒有加入啟動 classpath；已停止啟動。','Apple Silicon Objective-C bridge 未加入启动 classpath；已停止启动。','The Apple Silicon Objective-C bridge is missing from the launch classpath. Launch stopped.'],
  ['未知資料夾。','未知文件夹。','Unknown folder.'],
  ['拒絕 Java 安裝檔中的符號連結。','已拒绝 Java 安装包中的符号链接。','A symlink in the Java package was blocked.'],
  ['Java 安裝檔包含不合法的根路徑。','Java 安装包包含无效的根路径。','The Java package contains an invalid root path.'],
  ['Java 安裝檔包含越界路徑。','Java 安装包包含超出范围的路径。','The Java package contains a path outside its root.'],
  ['Java 安裝檔包含不支援的特殊檔案。','Java 安装包包含不支持的特殊文件。','The Java package contains an unsupported special file.'],
  ['Java 安裝檔包含重複路徑。','Java 安装包包含重复路径。','The Java package contains duplicate paths.'],
  ['Java 安裝檔目錄結構衝突。','Java 安装包目录结构冲突。','The Java package contains conflicting directory structures.'],
  ['Java 安裝檔包含目的地衝突。','Java 安装包包含目标路径冲突。','The Java package contains conflicting destination paths.'],
  ['Java 安裝檔內容不完整。','Java 安装包内容不完整。','The Java package is incomplete.'],
  ['Java 安裝檔硬連結無法安全建立。','无法安全创建 Java 安装包中的硬链接。','Could not safely create a hard link from the Java package.'],
  ['Java 安裝檔符號連結目的地衝突。','Java 安装包的符号链接目标冲突。','The Java package contains a conflicting symlink destination.'],
  ['Apple Silicon LWJGL 套件缺少必要原生檔。','Apple Silicon LWJGL 包缺少必要的原生文件。','The Apple Silicon LWJGL package is missing a required native file.'],
  ['Apple Silicon LWJGL 原生檔不是 ARM64 架構。','Apple Silicon LWJGL 原生文件不是 ARM64 架构。','The Apple Silicon LWJGL native file is not ARM64.'],
  ['Apple Silicon Objective-C bridge 類別格式無效；已停止啟動。','Apple Silicon Objective-C bridge 类格式无效；已停止启动。','The Apple Silicon Objective-C bridge class file is invalid. Launch stopped.'],
  ['Apple Silicon Objective-C bridge 不相容於 Java 8；已停止啟動。','Apple Silicon Objective-C bridge 与 Java 8 不兼容；已停止启动。','The Apple Silicon Objective-C bridge is incompatible with Java 8. Launch stopped.'],
  ['Java 資料夾路徑不合法。','Java 文件夹路径无效。','The Java folder path is invalid.'],
  ['選取的 Java 位置不是資料夾。','所选 Java 位置不是文件夹。','The selected Java location is not a folder.'],
  ['最多保留 30 個本地玩家。','最多保留 30 个本地玩家。','You can keep up to 30 local players.'],
  ['外部遊戲的 Mod 載入器無法辨識；請先在搜尋條件選擇該遊戲實際使用的 Fabric、Forge、NeoForge 或 Quilt。','无法识别外部游戏的 Mod 加载器；请先在搜索条件中选择该游戏实际使用的 Fabric、Forge、NeoForge 或 Quilt。','The external game’s Mod loader could not be identified. Choose its actual Fabric, Forge, NeoForge, or Quilt loader in the search filters.'],
  ['這個 Mod 版本與所選外部遊戲載入器不相容。','此 Mod 版本与所选外部游戏加载器不兼容。','This Mod version is incompatible with the selected external game loader.'],
  ['無法建立目標遊戲的 Mods 資料夾。','无法创建目标游戏的 Mods 文件夹。','Could not create the target game’s Mods folder.'],
  ['整合包超過安全檔案數或解壓大小上限。','整合包超过安全文件数或解压大小上限。','The modpack exceeds the safe file-count or extraction-size limit.'],
  ['整合包缺少可讀的 modrinth.index.json。','整合包缺少可读取的 modrinth.index.json。','The modpack is missing a readable modrinth.index.json.'],
  ['不支援這個 Modrinth 整合包格式。','不支持此 Modrinth 整合包格式。','This Modrinth modpack format is not supported.'],
  ['整合包缺少版本需求。','整合包缺少版本要求。','The modpack is missing version requirements.'],
  ['整合包 Minecraft 版本不合法。','整合包的 Minecraft 版本无效。','The modpack’s Minecraft version is invalid.'],
  ['這個整合包使用 Forge、NeoForge 或 Quilt；目前一鍵匯入只支援原版與 Fabric。請選「下載到 Downloads」並使用相應啟動器匯入。','此整合包使用 Forge、NeoForge 或 Quilt；目前一键导入仅支持原版与 Fabric。请选择“下载到 Downloads”，再用相应启动器导入。','This modpack uses Forge, NeoForge, or Quilt. One-click import supports Vanilla and Fabric only. Download it to Downloads and import it with its matching launcher.'],
  ['整合包檔案清單不合法或超過安全上限。','整合包文件列表无效或超过安全上限。','The modpack file list is invalid or exceeds the safety limit.'],
  ['已取消整合包匯入；暫存實例已清理。','已取消整合包导入；临时实例已清理。','Modpack import cancelled. The temporary instance was removed.'],
  ['建立整合包實例時發生名稱衝突，請重試。','创建整合包实例时名称冲突，请重试。','A name conflict occurred while creating the modpack instance. Try again.'],
  ['Java 安裝路徑衝突。','Java 安装路径冲突。','The Java installation path conflicts with an existing path.'],
  ['Fabric 暫未提供此版本的穩定 Loader。','Fabric 暂未提供此版本的稳定 Loader。','Fabric has not published a stable loader for this version yet.'],
  ['記憶體分配太多，請改用自動。','分配的内存过多，请改用自动。','Too much memory is allocated. Switch to Automatic.'],
  ['下載校驗失敗，原有檔案未被覆蓋。','下载校验失败，原有文件未被覆盖。','Download verification failed. Existing files were not overwritten.'],
  ['下載 SHA-256 校驗失敗，原有檔案未被覆蓋。','下载 SHA-256 校验失败，原有文件未被覆盖。','The SHA-256 check failed. Existing files were not overwritten.'],
  ['下載 SHA-512 校驗失敗，原有檔案未被覆蓋。','下载 SHA-512 校验失败，原有文件未被覆盖。','The SHA-512 check failed. Existing files were not overwritten.'],
  ['Java 安裝檔在符號連結下包含檔案。','Java 安装包在符号链接目录下包含文件。','The Java package contains a file inside a symlink.'],
  ['Java 安裝檔包含不安全的符號連結。','Java 安装包包含不安全的符号链接。','The Java package contains an unsafe symlink.'],
  ['Java 安裝檔符號連結超出解壓範圍。','Java 安装包的符号链接超出解压范围。','A Java package symlink points outside the extraction root.'],
  ['Apple Silicon Objective-C 原生庫長度不符；已停止啟動。','Apple Silicon Objective-C 原生库长度不符；已停止启动。','The Apple Silicon Objective-C native library has an unexpected length. Launch stopped.'],
  ['找不到選取的 Java 資料夾。','找不到所选的 Java 文件夹。','The selected Java folder could not be found.'],
  ['這個資料夾無法寫入。請選擇可寫入的 Java 安裝位置。','此文件夹不可写入。请选择可写入的 Java 安装位置。','This folder is not writable. Choose a writable Java installation location.'],
  ['Modrinth API 回應超過安全大小上限。','Modrinth API 响应超过安全大小上限。','The Modrinth API response exceeds the safe size limit.'],
  ['整合包嘗試覆蓋啟動器管理檔案，為保護遊戲已停止匯入。','整合包试图覆盖启动器管理的文件；为保护游戏，已停止导入。','The modpack tried to overwrite launcher-managed files. Import stopped to protect the game.'],
  ['整合包覆蓋檔包含符號連結。','整合包覆盖文件包含符号链接。','A modpack override contains a symlink.'],
  ['整合包覆蓋檔解壓後超過 1 GB 安全上限。','整合包覆盖文件解压后超过 1 GB 安全上限。','The extracted modpack overrides exceed the 1 GB safety limit.'],
  ['整合包檔案資料不完整。','整合包文件数据不完整。','The modpack file metadata is incomplete.'],
  ['整合包含重複安裝路徑，為避免覆蓋已停止。','整合包包含重复安装路径；为避免覆盖文件，已停止导入。','The modpack has duplicate install paths. Import stopped to prevent overwrites.'],
  ['整合包中有檔案缺少下載位址、雜湊或大小。','整合包中的文件缺少下载地址、哈希或大小。','A modpack file is missing its download URL, checksum, or size.'],
  ['整合包必要檔案總大小超過 1 GB 安全上限。','整合包所需文件总大小超过 1 GB 安全上限。','The required modpack files exceed the 1 GB safety limit.'],
  ['整合包檔案下載位址不合法。','整合包文件下载地址无效。','A modpack file has an invalid download URL.'],
  ['整合包包含非 Modrinth CDN 的第三方檔案，為保護安全未自動下載。請先選「下載到 Downloads」並使用原平台匯入。','整合包包含来自非 Modrinth CDN 的第三方文件；为保护安全，未自动下载。请选择“下载到 Downloads”并使用原平台导入。','The modpack includes third-party files outside the Modrinth CDN, so they were not downloaded automatically. Save it to Downloads and import with its original launcher.'],
  ['整合包覆蓋路徑包含符號連結。','整合包覆盖路径包含符号链接。','A modpack override path contains a symlink.'],
  ['Java 安裝檔內容大小與 ZIP 索引不符。','Java 安装包内容大小与 ZIP 索引不符。','The Java package contents do not match the ZIP index sizes.'],
  ['Java 安裝檔包含不安全的硬連結。','Java 安装包包含不安全的硬链接。','The Java package contains an unsafe hard link.'],
  ['Java 安裝檔硬連結目標不合法。','Java 安装包的硬链接目标无效。','The Java package contains an invalid hard-link target.'],
  ['Java 安裝檔內容超出安全限制。','Java 安装包内容超过安全限制。','The Java package contents exceed the safety limit.'],
  ['Apple Silicon Java 8 相容 runtime 只適用於 macOS ARM64。','Apple Silicon Java 8 兼容运行环境仅适用于 macOS ARM64。','The Apple Silicon Java 8 compatibility runtime requires macOS ARM64.'],
  ['Apple Silicon LWJGL 2 相容層不適用於這個版本或電腦。','Apple Silicon LWJGL 2 兼容层不适用于此版本或电脑。','The Apple Silicon LWJGL 2 compatibility layer is not available for this game version or Mac.'],
  ['Apple Silicon LWJGL Java 函式庫損壞，請按「檢查及修復」重試。','Apple Silicon LWJGL Java 库已损坏，请点“检查并修复”重试。','The Apple Silicon LWJGL Java library is damaged. Choose Check & Repair and try again.'],
  ['Apple Silicon LWJGL 原生檔不是 ARM64 架構。','Apple Silicon LWJGL 原生文件不是 ARM64 架构。','The Apple Silicon LWJGL native file is not built for ARM64.'],
  ['Apple Silicon LWJGL 套件無法讀取；原版遊戲檔未變更。','无法读取 Apple Silicon LWJGL 套件；原版游戏文件未更改。','Could not read the Apple Silicon LWJGL package. Original game files were not changed.'],
  ['Apple Silicon LWJGL 套件缺少必要原生檔。','Apple Silicon LWJGL 套件缺少必需的原生文件。','The Apple Silicon LWJGL package is missing a required native file.'],
  ['Apple Silicon Objective-C bridge 不相容於 Java 8；已停止啟動。','Apple Silicon Objective-C bridge 与 Java 8 不兼容；已停止启动。','The Apple Silicon Objective-C bridge is incompatible with Java 8. Launch stopped.'],
  ['Apple Silicon Objective-C bridge 原生庫格式無效；已停止啟動。','Apple Silicon Objective-C bridge 原生库格式无效；已停止启动。','The Apple Silicon Objective-C bridge native library has an invalid format. Launch stopped.'],
  ['Apple Silicon Objective-C bridge 套件大小不符；請重新解壓縮啟動器。','Apple Silicon Objective-C bridge 套件大小不符；请重新解压启动器。','The Apple Silicon Objective-C bridge package has an unexpected size. Re-extract the launcher.'],
  ['Apple Silicon Objective-C bridge 套件校驗失敗；請重新解壓縮啟動器。','Apple Silicon Objective-C bridge 套件校验失败；请重新解压启动器。','The Apple Silicon Objective-C bridge package failed verification. Re-extract the launcher.'],
  ['Apple Silicon Objective-C bridge 套件無法讀取；請重新解壓縮啟動器。','无法读取 Apple Silicon Objective-C bridge 套件；请重新解压启动器。','Could not read the Apple Silicon Objective-C bridge package. Re-extract the launcher.'],
  ['Apple Silicon Objective-C bridge 沒有 ARM64 原生庫；已停止啟動。','Apple Silicon Objective-C bridge 没有 ARM64 原生库；已停止启动。','The Apple Silicon Objective-C bridge has no ARM64 native library. Launch stopped.'],
  ['Apple Silicon Objective-C bridge 沒有加入啟動 classpath；已停止啟動。','Apple Silicon Objective-C bridge 未加入启动 classpath；已停止启动。','The Apple Silicon Objective-C bridge is missing from the launch classpath. Launch stopped.'],
  ['Apple Silicon Objective-C bridge 缺少必要 Java 類別；已停止啟動。','Apple Silicon Objective-C bridge 缺少必需的 Java 类；已停止启动。','The Apple Silicon Objective-C bridge is missing a required Java class. Launch stopped.'],
  ['Apple Silicon Objective-C bridge 類別格式無效；已停止啟動。','Apple Silicon Objective-C bridge 类格式无效；已停止启动。','The Apple Silicon Objective-C bridge class has an invalid format. Launch stopped.'],
  ['Apple Silicon Objective-C 原生庫不完整或沒有 ARM64 架構；已停止啟動。','Apple Silicon Objective-C 原生库不完整或没有 ARM64 架构；已停止启动。','The Apple Silicon Objective-C native library is incomplete or lacks ARM64 support. Launch stopped.'],
  ['Apple Silicon Objective-C 原生庫大小或格式無效；已停止啟動。','Apple Silicon Objective-C 原生库大小或格式无效；已停止启动。','The Apple Silicon Objective-C native library has an invalid size or format. Launch stopped.'],
  ['Apple Silicon Objective-C 原生庫無法安全安裝到遊戲執行目錄；已停止啟動。','Apple Silicon Objective-C 原生库无法安全安装到游戏运行目录；已停止启动。','The Apple Silicon Objective-C native library cannot be safely installed in the game runtime folder. Launch stopped.'],
  ['Apple Silicon 舊版 JNA 不相容於 Java 8；已停止啟動。','Apple Silicon 旧版 JNA 与 Java 8 不兼容；已停止启动。','The legacy Apple Silicon JNA library is incompatible with Java 8. Launch stopped.'],
  ['Apple Silicon 舊版 JNA 原生庫格式無效；請重新解壓縮啟動器。','Apple Silicon 旧版 JNA 原生库格式无效；请重新解压启动器。','The legacy Apple Silicon JNA native library has an invalid format. Re-extract the launcher.'],
  ['Apple Silicon 舊版 JNA 套件大小不符；請重新解壓縮啟動器。','Apple Silicon 旧版 JNA 套件大小不符；请重新解压启动器。','The legacy Apple Silicon JNA package has an unexpected size. Re-extract the launcher.'],
  ['Apple Silicon 舊版 JNA 套件校驗失敗；請重新解壓縮啟動器。','Apple Silicon 旧版 JNA 套件校验失败；请重新解压启动器。','The legacy Apple Silicon JNA package failed verification. Re-extract the launcher.'],
  ['Apple Silicon 舊版 JNA 套件沒有 ARM64 原生庫；已停止啟動。','Apple Silicon 旧版 JNA 套件没有 ARM64 原生库；已停止启动。','The legacy Apple Silicon JNA package has no ARM64 native library. Launch stopped.'],
  ['Apple Silicon 舊版 JNA 套件無法讀取；請重新解壓縮啟動器。','无法读取 Apple Silicon 旧版 JNA 套件；请重新解压启动器。','Could not read the legacy Apple Silicon JNA package. Re-extract the launcher.'],
  ['Apple Silicon 舊版相容套件缺少 JNA；請重新解壓縮啟動器。','Apple Silicon 旧版兼容套件缺少 JNA；请重新解压启动器。','The legacy Apple Silicon compatibility package is missing JNA. Re-extract the launcher.'],
  ['Apple Silicon 舊版相容套件缺少 Objective-C bridge；請重新解壓縮啟動器。','Apple Silicon 旧版兼容套件缺少 Objective-C bridge；请重新解压启动器。','The legacy Apple Silicon compatibility package is missing the Objective-C bridge. Re-extract the launcher.'],
  ['APK manifest 過大。','APK manifest 过大。','The APK manifest is too large.'],
  ['APK 含不安全的路徑。','APK 包含不安全的路径。','The APK contains an unsafe path.'],
  ['APK 含重複路徑。','APK 包含重复路径。','The APK contains duplicate paths.'],
  ['APK 含重複遊戲檔案，無法安全合併。','APK 包含重复游戏文件，无法安全合并。','The APKs contain duplicate game files and cannot be safely merged.'],
  ['APK 超過安裝大小限制。','APK 超过安装大小限制。','The APK exceeds the installation size limit.'],
  ['Android manifest 大小不正確。','Android manifest 大小不正确。','The Android manifest has an invalid size.'],
  ['Bedrock 資料夾路徑不合法。','Bedrock 文件夹路径无效。','The Bedrock folder path is invalid.'],
  ['Bedrock 資料夾路徑欄位缺失。','缺少 Bedrock 文件夹路径字段。','The Bedrock folder path field is missing.'],
  ['Fabric 暫未提供此版本的穩定 Loader。','Fabric 暂未提供此版本的稳定 Loader。','Fabric does not provide a stable loader for this game version yet.'],
  ['Fabric 版本資料不相符。','Fabric 版本数据不匹配。','The Fabric version metadata does not match.'],
  ['Java 安裝檔內容不完整。','Java 安装包内容不完整。','The Java installation archive is incomplete.'],
  ['Java 安裝檔內容大小與 ZIP 索引不符。','Java 安装包内容大小与 ZIP 索引不符。','The Java installation archive contents do not match the ZIP index sizes.'],
  ['Java 安裝檔內容超出安全限制。','Java 安装包内容超出安全限制。','The Java installation archive contents exceed the safety limit.'],
  ['Java 安裝檔包含不合法的根路徑。','Java 安装包包含无效的根路径。','The Java installation archive contains an invalid root path.'],
  ['Java 安裝檔包含不安全的硬連結。','Java 安装包包含不安全的硬链接。','The Java installation archive contains an unsafe hard link.'],
  ['Java 安裝檔包含不安全的符號連結。','Java 安装包包含不安全的符号链接。','The Java installation archive contains an unsafe symbolic link.'],
  ['Java 安裝檔包含不支援的特殊檔案。','Java 安装包包含不支持的特殊文件。','The Java installation archive contains an unsupported special file.'],
  ['Java 安裝檔包含目的地衝突。','Java 安装包存在目标路径冲突。','The Java installation archive contains a destination conflict.'],
  ['Java 安裝檔包含越界路徑。','Java 安装包包含越界路径。','The Java installation archive contains a path outside its allowed location.'],
  ['Java 安裝檔包含重複路徑。','Java 安装包包含重复路径。','The Java installation archive contains duplicate paths.'],
  ['Java 安裝檔在符號連結下包含檔案。','Java 安装包在符号链接下包含文件。','The Java installation archive contains a file beneath a symbolic link.'],
  ['Java 安裝檔無法安全解壓，請按「檢查及修復」重試。','Java 安装包无法安全解压，请点“检查并修复”重试。','The Java installation archive cannot be safely extracted. Choose Check & Repair and try again.'],
  ['Java 安裝檔目錄結構衝突。','Java 安装包目录结构冲突。','The Java installation archive has conflicting directory entries.'],
  ['Java 安裝檔硬連結無法安全建立。','无法安全创建 Java 安装包中的硬链接。','A hard link in the Java installation archive cannot be created safely.'],
  ['Java 安裝檔硬連結目標不合法。','Java 安装包硬链接目标无效。','A hard-link target in the Java installation archive is invalid.'],
  ['Java 安裝檔符號連結目的地衝突。','Java 安装包符号链接目标冲突。','A symbolic-link destination in the Java installation archive conflicts with another entry.'],
  ['Java 安裝檔符號連結超出解壓範圍。','Java 安装包符号链接指向解压范围之外。','A symbolic link in the Java installation archive points outside the extraction folder.'],
  ['Java 安裝檔超出安全解壓限制。','Java 安装包超出安全解压限制。','The Java installation archive exceeds the safe extraction limit.'],
  ['Java 安裝目錄包含符號連結；為保護資料已停止安裝。','Java 安装目录包含符号链接；为保护数据已停止安装。','The Java installation folder contains a symbolic link. Installation stopped to protect your data.'],
  ['Java 安裝路徑為符號連結；為保護資料已停止安裝。','Java 安装路径是符号链接；为保护数据已停止安装。','The Java installation path is a symbolic link. Installation stopped to protect your data.'],
  ['Java 安裝路徑衝突。','Java 安装路径冲突。','The Java installation path conflicts with an existing path.'],
  ['Java 已啟動，等候遊戲視窗…','Java 已启动，正在等待游戏窗口…','Java is running. Waiting for the game window…'],
  ['Java 資料夾路徑不合法。','Java 文件夹路径无效。','The Java folder path is invalid.'],
  ['Java 資料夾路徑欄位缺失。','缺少 Java 文件夹路径字段。','The Java folder path field is missing.'],
  ['Java 連結路徑超出安裝範圍。','Java 链接路径超出安装范围。','A Java link points outside the installation folder.'],
  ['Minecraft 版本篩選不合法。','Minecraft 版本筛选条件无效。','The Minecraft version filter is invalid.'],
  ['Mod 已下載並通過 SHA 校驗。','Mod 已下载并通过 SHA 校验。','The Mod was downloaded and passed the SHA checksum check.'],
  ['Modrinth API 回應超過安全大小上限。','Modrinth API 响应超过安全大小上限。','The Modrinth API response exceeds the safe size limit.'],
  ['Modrinth 官方 API 連線失敗，正在切換中國大陸 MCIM 鏡像…','Modrinth 官方 API 连接失败，正在切换到中国大陆 MCIM 镜像…','Could not reach the official Modrinth API. Switching to the MCIM mirror in mainland China…'],
  ['Modrinth 官方來源與 MCIM 備援均無法連線。請稍後重試，或開啟 Modrinth 專案頁手動下載。','Modrinth 官方源和 MCIM 备用源均无法连接。请稍后重试，或打开 Modrinth 项目页手动下载。','Neither the official Modrinth source nor the MCIM mirror is reachable. Try again later or open the Modrinth project page to download manually.'],
  ['Modrinth 搜尋回傳格式不完整。','Modrinth 搜索结果格式不完整。','The Modrinth search response is incomplete.'],
  ['Modrinth 版本資料格式不完整。','Modrinth 版本数据格式不完整。','The Modrinth version data is incomplete.'],
  ['PlayFab ARM64 程式庫校驗失敗，未安裝。','PlayFab ARM64 库校验失败，未安装。','The PlayFab ARM64 library failed verification and was not installed.'],
  ['SDK 未包含預期的 ARM64 相容程式庫。','SDK 不包含预期的 ARM64 兼容库。','The SDK does not contain the expected ARM64 compatibility library.'],
  ['XAPK／APKS／APKM／ZIP 請一次選一個。','XAPK／APKS／APKM／ZIP 请一次选择一个。','Choose only one XAPK, APKS, APKM or ZIP file at a time.'],
  ['下載 SHA-256 校驗失敗，原有檔案未被覆蓋。','下载文件的 SHA-256 校验失败，未覆盖原有文件。','The download failed its SHA-256 check. The existing file was not overwritten.'],
  ['下載 SHA-512 校驗失敗，原有檔案未被覆蓋。','下载文件的 SHA-512 校验失败，未覆盖原有文件。','The download failed its SHA-512 check. The existing file was not overwritten.'],
  ['下載來源不在允許的 HTTPS 網域內。','下载源不在允许的 HTTPS 域名内。','The download source is not on an allowed HTTPS domain.'],
  ['下載來源不在啟動器固定的相容性來源清單內。','下载源不在启动器固定的兼容源列表内。','The download source is not in the launcher’s trusted compatibility source list.'],
  ['下載來源的轉址不完整。','下载源的重定向信息不完整。','The download source returned an incomplete redirect.'],
  ['下載來源轉址過多。','下载源重定向次数过多。','The download source redirected too many times.'],
  ['下載備援來源不在啟動器固定的 HTTPS 網域清單內。','下载备用源不在启动器固定的 HTTPS 域名列表内。','The fallback download source is not in the launcher’s trusted HTTPS domain list.'],
  ['下載校驗失敗，原有檔案未被覆蓋。','下载校验失败，未覆盖原有文件。','The download failed verification. The existing file was not overwritten.'],
  ['下載的 Java 8 無法在 Apple Silicon 執行，已停止安裝。','下载的 Java 8 无法在 Apple Silicon 上运行，已停止安装。','The downloaded Java 8 runtime cannot run on Apple Silicon. Installation stopped.'],
  ['下載目的地不合法。','下载目标路径无效。','The download destination is invalid.'],
  ['下載重試設定不合法。','下载重试设置无效。','The download retry setting is invalid.'],
  ['不支援的函式庫名稱。','不支持的库名称。','The library name is not supported.'],
  ['不支援的遊戲類型。','不支持的游戏类型。','The game type is not supported.'],
  ['不支援這個 Modrinth 整合包格式。','不支持此 Modrinth 整合包格式。','This Modrinth modpack format is not supported.'],
  ['世界內含無法安全讀取的路徑，已取消備份。','世界包含无法安全读取的路径，已取消备份。','The world contains a path that cannot be read safely. Backup was cancelled.'],
  ['世界缺少 level.dat，未建立不完整備份。','世界缺少 level.dat，未创建不完整备份。','The world is missing level.dat. An incomplete backup was not created.'],
  ['世界資料夾已移動或無法安全讀取。','世界文件夹已移动或无法安全读取。','The world folder has moved or cannot be read safely.'],
  ['來源未提供有效 SHA-1／SHA-512，為保護遊戲檔案已停止下載。','源未提供有效的 SHA-1／SHA-512；为保护游戏文件，已停止下载。','The source did not provide a valid SHA-1 / SHA-512 checksum. Download stopped to protect game files.'],
  ['來源檔案大小不合法或超過安全上限。','源文件大小无效或超过安全上限。','The source file size is invalid or exceeds the safety limit.'],
  ['備份位置是符號連結，已停止以保護資料。','备份位置是符号链接；为保护数据已停止操作。','The backup location is a symbolic link. Operation stopped to protect your data.'],
  ['備份檔完整性檢查失敗，未保留不完整檔案。','备份文件完整性检查失败，未保留不完整文件。','The backup failed its integrity check. The incomplete file was discarded.'],
  ['函式庫檔案損壞，請重試修復。','库文件已损坏，请重新尝试修复。','A library file is damaged. Try repairing again.'],
  ['匯入基岩版至少需要 12 GB 暫存及安裝空間。','导入基岩版至少需要 12 GB 临时空间和安装空间。','Importing Bedrock requires at least 12 GB of temporary and installation space.'],
  ['另一個基岩版遊戲仍在執行。請先儲存並退出，再啟動版本。','另一个基岩版游戏仍在运行。请先保存并退出，再启动此版本。','Another Bedrock game is still running. Save and quit it before launching this version.'],
  ['只接受 JSON。','仅接受 JSON。','Only JSON is accepted.'],
  ['只接受公開 HTTPS 直連，不接受帳號密碼、片段或本機位址。','仅接受公开 HTTPS 直链，不接受用户名、密码、片段标识或本地地址。','Only public HTTPS direct links are accepted. Usernames, passwords, URL fragments and local addresses are not allowed.'],
  ['基岩版程式已啟動，等待遊戲視窗；可玩性需以實際進入世界確認。','基岩版程序已启动，正在等待游戏窗口；是否可玩需以实际进入世界确认。','The Bedrock process started and is waiting for the game window. Confirm playability by entering a world.'],
  ['外部遊戲版本請使用原啟動器管理。','请使用原启动器管理外部游戏版本。','Manage external game versions with their original launcher.'],
  ['多選時請只選 base／split APK。','多选时请只选择 base／split APK。','When selecting multiple files, choose only the base and split APKs.'],
  ['安裝包 SHA-256 不符，未安裝。','安装包 SHA-256 不匹配，未安装。','The package SHA-256 checksum does not match. Nothing was installed.'],
  ['安裝包下載不完整。','安装包下载不完整。','The package download is incomplete.'],
  ['安裝包下載失敗或逾時；請確認直連可以下載檔案後重試。','安装包下载失败或超时；请确认直链可以下载文件后重试。','The package download failed or timed out. Confirm the direct link downloads a file, then try again.'],
  ['安裝包下載逾時，請重試。','安装包下载超时，请重试。','The package download timed out. Try again.'],
  ['安裝包不完整或無法讀取，未安裝。','安装包不完整或无法读取，未安装。','The package is incomplete or unreadable. Nothing was installed.'],
  ['安裝包內的版本識別碼與相容補丁不符，未套用。','安装包中的版本标识与兼容补丁不匹配，未应用补丁。','The version identifier in the package does not match the compatibility patch. The patch was not applied.'],
  ['安裝包包含過多 APK。','安装包包含过多 APK。','The package contains too many APK files.'],
  ['安裝包含不安全或重複的路徑。','安装包包含不安全或重复的路径。','The package contains an unsafe or duplicate path.'],
  ['安裝包大小超過限制或與來源不符。','安装包大小超出限制或与来源提供的信息不符。','The package exceeds the size limit or its size does not match the source.'],
  ['安裝包檔案數量過多。','安装包文件数量过多。','The package contains too many files.'],
  ['安裝包檔案校驗失敗。','安装包文件校验失败。','The package file failed verification.'],
  ['安裝包版本名稱不一致，未安裝。','安装包版本名称不一致，未安装。','The version names in the package do not match. Nothing was installed.'],
  ['安裝包的遊戲或版本不一致，未安裝。','安装包中的游戏或版本不一致，未安装。','The game or version in the package does not match. Nothing was installed.'],
  ['安裝包的遊戲程式架構不正確。','安装包中的游戏程序架构不正确。','The game executable in the package has the wrong architecture.'],
  ['安裝包總大小超過 6 GB。','安装包总大小超过 6 GB。','The total package size exceeds 6 GB.'],
  ['安裝包缺少對應此 Mac 的遊戲程式或資源。請檢查是否選齊 base 與 split APK。','安装包缺少适用于此 Mac 的游戏程序或资源。请确认已选齐 base 和 split APK。','The package is missing game files or resources for this Mac. Check that you selected the base and all required split APKs.'],
  ['安裝包解壓後超過 6 GB。','安装包解压后超过 6 GB。','The extracted package exceeds 6 GB.'],
  ['安裝包超過 3 GB 限制。','安装包超过 3 GB 限制。','The package exceeds the 3 GB limit.'],
  ['安裝包路徑不合法。','安装包路径无效。','The package path is invalid.'],
  ['安裝新版本請先按「使用 MambaCraft 資料位置」，外部資料只供讀取及啟動。','安装新版本前，请先点“使用 MambaCraft 数据位置”；外部数据仅供读取和启动。','To install a new version, first choose “Use MambaCraft data folder.” External data is read-only and can only be used to launch.'],
  ['已有不完整的核心目錄；請先保留診斷資料並移走該目錄，再重試。','已存在不完整的核心目录；请先保留诊断资料并移走该目录，然后重试。','An incomplete runtime folder already exists. Save its diagnostic data and move the folder aside before trying again.'],
  ['找不到安裝包，或檔案超過 3 GB。','找不到安装包，或文件超过 3 GB。','The package could not be found or exceeds 3 GB.'],
  ['找不到所選資料夾。','找不到所选文件夹。','The selected folder could not be found.'],
  ['找不到附加包 manifest；請選擇 .mcpack 或 .mcaddon。','找不到附加包 manifest；请选择 .mcpack 或 .mcaddon 文件。','Could not find an add-on manifest. Choose an .mcpack or .mcaddon file.'],
  ['整合包已下載並通過 SHA 校驗。','整合包已下载并通过 SHA 校验。','The modpack was downloaded and passed the SHA checksum check.'],
  ['整合包已匯入並完成檔案校驗。','整合包已导入并完成文件校验。','The modpack was imported and all files passed verification.'],
  ['未知的 Bedrock 資源包類型。','未知的 Bedrock 资源包类型。','Unknown Bedrock pack type.'],
  ['未知的支援資料位置。','未知的受支持数据位置。','Unknown supported data location.'],
  ['本機檔案自動匯入要求無效。','本地文件自动导入请求无效。','The local-file auto-import request is invalid.'],
  ['核心套件結構不正確。','核心包结构不正确。','The runtime package has an invalid structure.'],
  ['核心套件缺少遊戲執行檔。','核心包缺少游戏可执行文件。','The runtime package is missing the game executable.'],
  ['核心套件與這台 Mac 的架構不符。','核心包与这台 Mac 的架构不匹配。','The runtime package does not match this Mac’s architecture.'],
  ['核心校驗失敗，未安裝；請重新下載。','核心校验失败，未安装；请重新下载。','The runtime failed verification and was not installed. Download it again.'],
  ['核心檔案大小不符。','核心文件大小不匹配。','The runtime file size does not match.'],
  ['核心資料夾不安全，請檢查符號連結。','核心文件夹不安全，请检查符号链接。','The runtime folder is unsafe. Check it for symbolic links.'],
  ['檔案中沒有 Android APK。請使用安裝包直連，不能使用網頁連結。','文件中没有 Android APK。请使用安装包直链，不能使用网页链接。','No Android APK was found in the file. Use a direct package link, not a webpage link.'],
  ['正在下載基岩版執行核心…','正在下载基岩版运行核心…','Downloading the Bedrock runtime…'],
  ['正在下載相容補丁 PlayFab SDK…','正在下载兼容补丁 PlayFab SDK…','Downloading the PlayFab SDK compatibility patch…'],
  ['正在下載自訂來源安裝包…','正在从自定义来源下载安装包…','Downloading the package from the custom source…'],
  ['正在備份世界、模組及遊戲設定…','正在备份世界、模组和游戏设置…','Backing up worlds, mods and game settings…'],
  ['正在備份這個版本的所有世界…','正在备份此版本的所有世界…','Backing up all worlds for this version…'],
  ['正在取得官方版本清單…','正在获取官方版本列表…','Fetching the official version catalog…'],
  ['正在更新基岩版版本清單…','正在更新基岩版版本列表…','Updating the Bedrock version catalog…'],
  ['正在檢查安裝包版本及 CPU 架構…','正在检查安装包版本和 CPU 架构…','Checking the package version and CPU architecture…'],
  ['正在準備基岩版相容補丁：下載並校驗 PlayFab SDK…','正在准备基岩版兼容补丁：下载并校验 PlayFab SDK…','Preparing the Bedrock compatibility patch: downloading and verifying the PlayFab SDK…'],
  ['正在準備獨立整合包實例…','正在准备独立整合包实例…','Preparing an isolated modpack instance…'],
  ['正在讀取本機安裝包…','正在读取本地安装包…','Reading the local package…'],
  ['正在驗證及安裝基岩版核心…','正在验证并安装基岩版核心…','Verifying and installing the Bedrock runtime…'],
  ['正在驗證及安裝遊戲…','正在验证并安装游戏…','Verifying and installing the game…'],
  ['此基岩版整合目前只支援 Apple Silicon 與 Intel Mac。','此 Bedrock 集成目前仅支持 Apple Silicon 和 Intel Mac。','This Bedrock integration currently supports Apple Silicon and Intel Macs only.'],
  ['此安裝包依賴 OBB，這個版本暫不支援。請使用完整 APK 或 base／split APK。','此安装包依赖 OBB，此版本暂不支持。请使用完整 APK 或 base／split APK。','This package requires OBB files, which are not supported yet. Use a complete APK or base / split APKs.'],
  ['此版本尚未建立獨立存檔。','此版本尚未创建独立存档。','No separate save data has been created for this version yet.'],
  ['此版本已改為直接啟動遊戲。請選擇已安裝的基岩版版本。','此版本现已直接启动游戏。请选择已安装的基岩版版本。','This version now launches the game directly. Select an installed Bedrock version.'],
  ['此版本缺少適合這台 Mac 的遊戲程式。','此版本缺少适用于这台 Mac 的游戏程序。','This version is missing the game executable for this Mac.'],
  ['準備基岩版核心至少需要 3 GB 可用空間。','准备基岩版核心至少需要 3 GB 可用空间。','At least 3 GB of free space is required to set up the Bedrock runtime.'],
  ['無法確認 Bedrock 是否正在執行，因此取消備份以保護存檔。','无法确认 Bedrock 是否正在运行，因此已取消备份以保护存档。','Could not determine whether Bedrock is running. Backup was cancelled to protect your saves.'],
  ['無法讀取安裝包；請提供完整、未加密的 APK／XAPK／APKS／APKM／ZIP。','无法读取安装包；请提供完整、未加密的 APK／XAPK／APKS／APKM／ZIP。','Could not read the package. Provide a complete, unencrypted APK / XAPK / APKS / APKM / ZIP.'],
  ['無法辨識資源包或行為包的 manifest。','无法识别资源包或行为包的 manifest。','Could not recognize the resource or behavior pack manifest.'],
  ['無法驗證安裝包的 Android manifest。','无法验证安装包的 Android manifest。','Could not verify the Android manifest in the package.'],
  ['版本來源回傳空清單，已保留快取。','版本源返回空列表，已保留缓存。','The version source returned an empty list. The cached list was kept.'],
  ['版本日誌路徑含符號連結。','版本日志路径包含符号链接。','The version log path contains a symbolic link.'],
  ['版本清單過大。','版本列表过大。','The version catalog is too large.'],
  ['版本索引包含不正確的項目。','版本索引包含无效项目。','The version index contains an invalid entry.'],
  ['版本索引格式不正確。','版本索引格式不正确。','The version index has an invalid format.'],
  ['版本識別資料不合法。','版本标识信息无效。','The version identifier is invalid.'],
  ['版本資料夾不安全，請檢查符號連結。','版本文件夹不安全，请检查符号链接。','The version folder is unsafe. Check it for symbolic links.'],
  ['相容程式庫大小不符。','兼容库大小不匹配。','The compatibility library has an unexpected size.'],
  ['相容補丁下載大小不符。','兼容补丁下载大小不匹配。','The compatibility patch download has an unexpected size.'],
  ['相容補丁壓縮檔損壞，未安裝。','兼容补丁压缩包已损坏，未安装。','The compatibility patch archive is damaged and was not installed.'],
  ['相容補丁已準備，正在交給基岩版核心載入…','兼容补丁已准备，正在交由基岩版核心加载…','The compatibility patch is ready. Passing it to the Bedrock runtime…'],
  ['相容補丁目錄不安全。','兼容补丁目录不安全。','The compatibility patch folder is unsafe.'],
  ['自動匯入只接受 Downloads 內已完成的 .mcpack 或 .mcaddon。','自动导入仅接受 Downloads 中已下载完成的 .mcpack 或 .mcaddon 文件。','Auto-import accepts only completed .mcpack or .mcaddon files in Downloads.'],
  ['自動匯入只能安裝到 MambaCraft 管理的遊戲版本。','自动导入只能安装到由 MambaCraft 管理的游戏版本。','Auto-import can only install into game versions managed by MambaCraft.'],
  ['自動匯入檔案已變更或不在 Downloads 根目錄。','自动导入文件已更改，或不在 Downloads 根目录中。','The auto-import file changed or is not in the Downloads root folder.'],
  ['自動匯入設定不正確。','自动导入设置无效。','The auto-import settings are invalid.'],
  ['要求大小不合法。','请求大小无效。','The requested size is invalid.'],
  ['請先儲存並退出基岩版，再備份世界。','请先保存并退出基岩版，再备份世界。','Save and quit Bedrock before backing up worlds.'],
  ['請先儲存並退出基岩版，再匯入安裝包。','请先保存并退出基岩版，再导入安装包。','Save and quit Bedrock before importing a package.'],
  ['請先完成工作及退出遊戲，再更改資料位置。','请先完成当前任务并退出游戏，再更改数据位置。','Finish current tasks and quit the game before changing the data location.'],
  ['請先完成目前工作或退出遊戲。','请先完成当前任务或退出游戏。','Finish the current task or quit the game first.'],
  ['請先等候工作完成並正常退出遊戲。','请先等待任务完成并正常退出游戏。','Wait for the task to finish and quit the game normally first.'],
  ['請先退出基岩版，再安裝附加內容。','请先退出基岩版，再安装附加内容。','Quit Bedrock before installing add-ons.'],
  ['請先退出基岩版，再準備相容補丁。','请先退出基岩版，再准备兼容补丁。','Quit Bedrock before preparing the compatibility patch.'],
  ['請先退出基岩版，再移除遊戲版本。','请先退出基岩版，再移除游戏版本。','Quit Bedrock before removing a game version.'],
  ['請先選擇已安裝的基岩版版本。','请先选择已安装的基岩版版本。','Select an installed Bedrock version first.'],
  ['請在基岩版遊戲中儲存並正常退出。','请在基岩版游戏中保存并正常退出。','Save your game and quit Bedrock normally.'],
  ['請貼上 HTTPS 直連，或選擇資源檔案。','请粘贴 HTTPS 直链，或选择资源文件。','Paste a direct HTTPS link or choose a resource file.'],
  ['請選擇一個安裝包，或最多 64 個 base／split APK。','请选择一个安装包，或最多 64 个 base／split APK。','Choose one package file, or up to 64 base / split APK files.'],
  ['請選擇有效的基岩版版本。','请选择有效的基岩版版本。','Choose a valid Bedrock version.'],
  ['請選擇本機安裝包或填寫 HTTPS 直連。','请选择本地安装包或输入 HTTPS 直链。','Choose a local package or enter a direct HTTPS link.'],
  ['請選擇由 MambaCraft 啟動的遊戲版本。','请选择由 MambaCraft 启动的游戏版本。','Choose a game version launched by MambaCraft.'],
  ['請選齊安裝包；必須包含唯一的 base APK。','请选齐安装包；必须包含且仅包含一个 base APK。','Select all package files. There must be exactly one base APK.'],
  ['讀取版本資料…','正在读取版本数据…','Reading version data…'],
  ['資料格式錯誤。','数据格式错误。','The data format is invalid.'],
  ['資料路徑含符號連結，請選擇實際資料夾。','数据路径包含符号链接，请选择实际文件夹。','The data path contains a symbolic link. Choose the actual folder.'],
  ['資料路徑超出管理範圍。','数据路径超出管理范围。','The data path is outside the managed area.'],
  ['資源包 manifest 過大。','资源包 manifest 过大。','The resource pack manifest is too large.'],
  ['資源包含不安全路徑、重複檔案或超出解壓限制。','资源包包含不安全路径、重复文件或超出解压限制。','The resource pack contains an unsafe path, duplicate file, or exceeds the extraction limit.'],
  ['資源包損壞或無法解壓，未安裝。','资源包已损坏或无法解压，未安装。','The resource pack is damaged or cannot be extracted. Nothing was installed.'],
  ['資源包目錄重疊，未安裝。','资源包目录重叠，未安装。','The resource pack folders overlap. Nothing was installed.'],
  ['資源檔案不存在或超過 512 MB。','资源文件不存在或超过 512 MB。','The resource file is missing or exceeds 512 MB.'],
  ['這不是可辨識的 Minecraft Android 正式版安裝包。','这不是可识别的 Minecraft Android 正式版安装包。','This is not a recognized Minecraft Android release package.'],
  ['這個世界沒有可備份的檔案。','此世界没有可备份的文件。','This world has no files to back up.'],
  ['這個版本已存在，已保留原本的遊戲檔案。','此版本已存在，原有游戏文件已保留。','This version already exists. The existing game files were kept.'],
  ['這個附加包已安裝或套件內有重複項目；原有內容保留。','此附加包已安装，或包内存在重复项目；原有内容已保留。','This add-on is already installed or contains duplicate items. Existing content was kept.'],
  ['遊戲正在啟動，請在遊戲內正常退出。','游戏正在启动，请在游戏中正常退出。','The game is starting. Quit normally from within the game.'],
  ['遊戲版本資料不安全，請重新匯入。','游戏版本数据不安全，请重新导入。','The game version data is unsafe. Import it again.'],
  ['遊戲版本路徑不安全。','游戏版本路径不安全。','The game version path is unsafe.'],
  ['遊戲資料夾不安全，請檢查符號連結。','游戏文件夹不安全，请检查符号链接。','The game folder is unsafe. Check it for symbolic links.'],
  ['隨附相容橋接程式校驗失敗，請重新解壓啟動器。','随附的兼容桥接程序校验失败，请重新解压启动器。','The bundled compatibility bridge failed verification. Re-extract the launcher.'],
 ];
 for(const [source,simplified,english] of backendRows)messages.set(source,{'zh-Hans':simplified,en:english});
 const attrs=new WeakMap(),texts=new WeakMap();
 const supported=['zh-Hant','zh-Hans','en'];
 function detect(languages){for(const raw of (languages||[])){const tag=String(raw||'').toLowerCase().replace('_','-');if(tag.startsWith('zh')){if(tag.includes('hant')||/(^|-)tw($|-)|(^|-)hk($|-)|(^|-)mo($|-)/.test(tag))return 'zh-Hant';if(tag.includes('hans')||/(^|-)cn($|-)|(^|-)sg($|-)/.test(tag))return 'zh-Hans';return 'zh-Hans';}if(tag.startsWith('en'))return 'en';}return 'en';}
 const seriesNames={'全部官方版本':['全部官方版本','All Official Versions'],'正式版':['正式版','Release'],'快照／愚人節':['快照／愚人节','Snapshots / April Fools'],'Beta 經典':['Beta 经典','Beta Classics'],'Alpha／更早期':['Alpha／更早期','Alpha / Earlier']};
 for(const [source,simplified,english] of [["在 MambaCraft 內匯入、管理及啟動基岩版。執行核心自動準備，每個版本使用獨立存檔。Apple Silicon／Intel Mac · 相容性預覽版。", "在 MambaCraft 内导入、管理及启动基岩版。运行核心自动准备，每个版本使用独立存档。Apple Silicon／Intel Mac · 兼容性预览版。", "Import, manage and launch Bedrock in MambaCraft. The runtime is set up automatically, with separate worlds for each version. Apple Silicon / Intel Mac · Compatibility preview."], ["加入基岩版遊戲", "添加基岩版游戏", "Add a Bedrock game"], ["選擇你有權使用的 Minecraft Android 安裝包，MambaCraft 會自動辨識版本與架構。支援完整 APK，或含 base／split APK 的 XAPK、APKS、APKM、ZIP。", "选择你有权使用的 Minecraft Android 安装包，MambaCraft 会自动识别版本与架构。支持完整 APK，或含 base／split APK 的 XAPK、APKS、APKM、ZIP。", "Choose a Minecraft Android package you are authorized to use. MambaCraft detects its version and CPU architecture. Supports a complete APK or XAPK, APKS, APKM and ZIP containing base / split APKs."], ["選擇本機安裝包…", "选择本地安装包…", "Choose local package…"], ["分割 APK 請同時選齊 base 與此 Mac 對應的 split。Apple Silicon 需要 arm64-v8a；Intel 需要 x86_64。OBB 暫不支援。", "分割 APK 请同时选齐 base 与此 Mac 对应的 split。Apple Silicon 需要 arm64-v8a；Intel 需要 x86_64。暂不支持 OBB。", "Select the base APK and matching splits together. Apple Silicon requires arm64-v8a; Intel requires x86_64. OBB is not supported yet."], ["從自訂 HTTPS 來源下載", "从自定义 HTTPS 来源下载", "Download from a custom HTTPS source"], ["安裝包直連", "安装包直链", "Direct package URL"], ["https://你的來源/game.apk", "https://你的来源/game.apk", "https://your-source/game.apk"], ["SHA-256（選填）", "SHA-256（选填）", "SHA-256 (optional)"], ["來源提供的 64 位 SHA-256", "来源提供的 64 位 SHA-256", "64-character SHA-256 supplied by the source"], ["下載並匯入", "下载并导入", "Download and import"], ["請使用你有權存取的安裝包直連，不是下載網頁。未內建完整遊戲鏡像；雜湊只核對檔案完整性，不能證明發行者身份。", "请使用你有权访问的安装包直链，不是下载网页。未内置完整游戏镜像；哈希只核对文件完整性，不能证明发行者身份。", "Use a direct package URL you are authorized to access, rather than a download webpage. No full-game mirrors are included. Hashes check file integrity, not publisher identity."], ["官方下載頁面 ↗", "官方下载页面 ↗", "Official download page ↗"], ["官方試玩選項 ↗", "官方试玩选项 ↗", "Official trial options ↗"], ["官方頁面供查看平台選項；Windows、iOS 安裝包與獨立伺服器不適用於此 Android 執行核心。移除啟動器登入不代表取得遊戲授權；遊戲自身的授權及 Xbox 功能由遊戲處理。", "官方页面供查看平台选项；Windows、iOS 安装包与独立服务器不适用于此 Android 运行核心。移除启动器登录不代表取得游戏授权；游戏自身的授权及 Xbox 功能由游戏处理。", "Official pages list platform options. Windows and iOS packages and dedicated servers cannot run with this Android runtime. Removing launcher sign-in does not grant a game license; game licensing and Xbox features remain handled by the game."], ["版本與相容性參考", "版本与兼容性参考", "Version and compatibility reference"], ["此索引僅供參考，不代表有對應下載來源。安裝時會以安裝包內容辨識版本，不需要手動選版本。相容範圍未經你的 Mac 實機驗證；較新版本可匯入管理，暫不開放啟動。", "此索引仅供参考，不代表有对应下载来源。安装时会以安装包内容识别版本，不需要手动选版本。兼容范围未经你的 Mac 实机验证；较新版本可导入管理，暂不开放启动。", "This index is a reference, not a list of available downloads. The package determines the installed version automatically. Compatibility still needs testing on your Mac; newer versions can be imported and managed, but launching is disabled."], ["1.3 RC22 新增本地玩家清理與皮膚站登入憑證移除說明，保留世界資料。基岩版仍屬相容性預覽；macOS 實機進入世界驗證尚未完成。", "1.3 RC22 新增本地玩家清理与皮肤站登录凭证移除说明，保留世界数据。基岩版仍属兼容性预览；macOS 实机进入世界验证尚未完成。", "Version 1.3 RC22 adds local player cleanup and clearer skin site credential removal. World data is kept. Bedrock remains a compatibility preview; entering a world on macOS still needs verification."], ["請輸入有效的 HTTPS 安裝包直連。", "请输入有效的 HTTPS 安装包直链。", "Enter a valid direct HTTPS package URL."], ["SHA-256 必須是 64 位十六進制字串，或留空。", "SHA-256 必须是 64 位十六进制字符串，或留空。", "Enter a 64-character hexadecimal SHA-256 or leave it blank."]])messages.set(source,{'zh-Hans':simplified,en:english});
 function translate(value,language){
  const table=messages.get(value);
  if(table&&table[language])return table[language];
  if(language==='zh-Hant')return value;
  const hans=language==='zh-Hans';
  let match;
  match=value.match(/^你的空間 \/ (.+)$/);
  if(match)return (hans?'你的空间 / ':'Workspace / ')+translate(match[1],language);
  match=value.match(/^(.+) · ([\d,]+) 次下載$/);
  if(match)return translate(match[1],language)+' · '+match[2]+' '+(hans?'次下载':'downloads');
  match=value.match(/^(.+) · 外部（載入器待選）$/);
  if(match)return match[1]+' · '+(hans?'外部（加载器待选）':'External (choose loader)');
  const bedrockSuffix=value.match(/^(.*) · (相容範圍|未驗證|無法啟動|相容性未驗證|已保留的世界|已安裝)$/);
  if(bedrockSuffix){const labels={'相容範圍':['兼容范围','Compatibility range'],'未驗證':['未验证','Unverified'],'無法啟動':['无法启动','Cannot launch'],'相容性未驗證':['兼容性未验证','Compatibility unverified'],'已保留的世界':['已保留的存档','Saved worlds'],'已安裝':['已安装','Installed']};return bedrockSuffix[1]+' · '+labels[bedrockSuffix[2]][hans?0:1];}
  match=value.match(/^(.*) · MambaCraft 獨立存檔$/);
  if(match)return match[1]+' · '+(hans?'MambaCraft 独立存档':'MambaCraft isolated saves');
  match=value.match(/^搜尋來源：(.*?)。官方來源失敗時會嘗試另一來源。$/);
  if(match)return (hans?'搜索来源：':'Search source: ')+translate(match[1],language)+(hans?'。官方来源失败时会尝试其他来源。':'. Another source will be tried if this one fails.');
  match=value.match(/^正在載入 (Mods|整合包) 搜尋結果…$/);
  if(match)return (hans?'正在加载 ':'Loading ')+(match[1]==='整合包'?(hans?'整合包':'modpacks'):'Mods')+(hans?' 搜索结果…':' search results…');

  match=value.match(/^無法儲存語言設定：(.*)$/);
  if(match)return (hans?'无法保存语言设置：':'Could not save language setting: ')+translate(match[1],language);
  match=value.match(/^無法儲存外觀設定：(.*)$/);
  if(match)return (hans?'无法保存外观设置：':'Could not save appearance setting: ')+translate(match[1],language);
  match=value.match(/^無法儲存遊戲版本管理偏好：(.*)$/);
  if(match)return (hans?'无法保存游戏版本管理偏好：':'Could not save edition preference: ')+translate(match[1],language);
  match=value.match(/^(全部官方版本|正式版|快照／愚人節|Beta 經典|Alpha／更早期) \((\d+)\)$/);
  if(match){const pair=seriesNames[match[1]];return pair[hans?0:1]+' ('+match[2]+')';}
  match=value.match(/^(.+) · (正式版|快照／愚人節|Beta 經典|Alpha／更早期)$/);
  if(match){const pair=seriesNames[match[2]];return match[1]+' · '+pair[hans?0:1];}
  match=value.match(/^(.+) · 外部安裝$/);
  if(match)return match[1]+' · '+(hans?'外部安装':'External');
  match=value.match(/^(.+) · 外部 · (.+)$/);
  if(match)return match[1]+' · '+(hans?'外部':'External')+' · '+match[2];
  match=value.match(/^(Darwin|Windows|Linux) (.+) · 可用 (.+) GB$/);
  if(match)return match[1]+' '+match[2]+' · '+(hans?'可用':'Available')+' '+match[3]+' GB';
  match=value.match(/^正在搜尋 Modrinth (Mods|整合包)…$/);
  if(match)return (hans?'正在搜索 Modrinth ':'Searching Modrinth ')+(match[1]==='整合包'?(hans?'整合包':'modpacks'):'Mods')+'…';
  match=value.match(/^正在讀取 (.+) 的相容版本…$/);
  if(match)return hans?'正在读取 '+match[1]+' 的兼容版本…':'Loading compatible versions for '+match[1]+'…';
  match=value.match(/^正在下載並校驗 (.+)…$/);
  if(match)return hans?'正在下载并校验 '+match[1]+'…':'Downloading and verifying '+match[1]+'…';
  match=value.match(/^正在下載／校驗整合包檔案 (\d+)\/(\d+)…$/);
  if(match)return hans?'正在下载／校验整合包文件 '+match[1]+'/'+match[2]+'…':'Downloading / verifying modpack files '+match[1]+'/'+match[2]+'…';
  match=value.match(/^正在下載／校驗遊戲與函式庫…(?:（沿用本機 Java (.+)）)?$/);
  if(match)return hans?'正在下载／校验游戏与库…'+(match[1]?'（使用本机 Java '+match[1]+'）':''):'Downloading / verifying game and libraries…'+(match[1]?' (using local Java '+match[1]+')':'');
  match=value.match(/^正在下載／校驗聲音與素材…$/);
  if(match)return hans?'正在下载／校验声音与资源…':'Downloading / verifying sounds and assets…';
  match=value.match(/^主要下載來源無回應或速度過慢，正在切換至 (.+)…$/);
  if(match)return hans?'主要下载源无响应或速度过慢，正在切换至 '+match[1]+'…':'Primary download source is unavailable or too slow; switching to '+match[1]+'…';
  match=value.match(/^正在尋找可用的本機 Java (\d+)…$/);
  if(match)return hans?'正在搜索可用的本机 Java '+match[1]+'…':'Searching for compatible local Java '+match[1]+'…';
  match=value.match(/^找到本機 Java (.+)，直接使用：(.+)$/);
  if(match)return hans?'找到本机 Java '+match[1]+'，直接使用：'+match[2]:'Found local Java '+match[1]+', using it: '+match[2];
  match=value.match(/^找到 (\d+) 個相容版本。來源：(.+)。$/);
  if(match)return hans?'已找到 '+match[1]+' 个兼容版本。来源：'+match[2]+'。':'Found '+match[1]+' compatible versions. Source: '+match[2]+'.';
  match=value.match(/^找到 (\d+) 個(整合包|Mod)。來源：(.+)。$/);
  if(match)return hans?'找到 '+match[1]+' 个'+(match[2]==='整合包'?'整合包':'Mod')+'。来源：'+match[3]+'。':'Found '+match[1]+' '+(match[2]==='整合包'?'modpacks':'Mods')+'. Source: '+match[3]+'.';
  match=value.match(/^(.+) 已下載至：(.+)$/);
  if(match)return hans?match[1]+' 已下载至：'+match[2]:match[1]+' downloaded to: '+match[2];
  match=value.match(/^(.+) 安裝完成，可以開始遊戲。(.+)。$/);
  if(match){const method=match[2].replace('沿用本機 Java ','using local Java ').replace('使用 MambaCraft 管理的 Java ','using MambaCraft-managed Java ');const methodHans=match[2].replace('沿用本機 Java ','沿用本机 Java ');return hans?match[1]+' 安装完成，可以开始游戏。'+methodHans+'。':match[1]+' installed and ready to play. '+method+'.';}
  match=value.match(/^重新掃描完成：找到 (\d+) 個本機版本。$/);
  if(match)return hans?'重新扫描完成：找到 '+match[1]+' 个本机版本。':'Scan complete: found '+match[1]+' local game versions.';
  match=value.match(/^(.+) 已安裝為獨立實例「(.+)」，使用 Minecraft (.+)。$/);
  if(match)return hans?match[1]+' 已安装为独立实例「'+match[2]+'」，使用 Minecraft '+match[3]+'。':match[1]+' installed as an isolated instance “'+match[2]+'” for Minecraft '+match[3]+'.';
  match=value.match(/^備份已建立：(.+)（「開啟備份」可找到）$/);
  if(match)return hans?'备份已创建：'+match[1]+'（可在“打开备份”中找到）':'Backup created: '+match[1]+' (open it from Backups).';
  match=value.match(/^診斷包已建立：(.+)。遊戲仍在執行時會嘗試擷取 Mac 執行緒；分享前請檢查玩家名稱與伺服器地址。$/);
  if(match)return hans?'诊断包已创建：'+match[1]+'。游戏仍在运行时会尝试采集 Mac 线程；分享前请检查玩家名称和服务器地址。':'Diagnostics created: '+match[1]+'. If the game is running, MambaCraft will try to capture Mac threads. Review player names and server addresses before sharing.';
  match=value.match(/^已刪除實例「(.+)」及其世界、Mods、設定。仍被其他版本使用的共用檔案會保留。$/);
  if(match)return hans?'已删除实例「'+match[1]+'」及其世界、Mods、设置。其他版本仍在使用的共享文件会保留。':'Deleted instance “'+match[1]+'” and its worlds, Mods and settings. Shared files used by other versions were kept.';
  match=value.match(/^已加入／檢查 (\d+) 個 Minecraft 資料夾：找到 (\d+) 個可辨識版本。$/);
  if(match)return hans?'已添加／检查 '+match[1]+' 个 Minecraft 文件夹：找到 '+match[2]+' 个可识别版本。':'Added / checked '+match[1]+' Minecraft folders; found '+match[2]+' recognized versions.';
  match=value.match(/^Java 安裝／搜尋位置：(.+)$/);
  if(match)return hans?'Java 安装／搜索位置：'+match[1]:'Java install / search location: '+match[1];
  match=value.match(/^正在取得官方版本清單…$/);
  if(match)return hans?'正在获取官方版本列表…':'Fetching the official version catalog…';
  match=value.match(/^讀取版本資料…$/);
  if(match)return hans?'正在读取版本数据…':'Reading version metadata…';
  match=value.match(/^正在準備 (Apple Silicon .+)…$/);
  if(match)return hans?'正在准备 '+match[1]+'…':'Preparing '+match[1]+'…';
  match=value.match(/^正在準備並校驗 (Apple Silicon .+)…$/);
  if(match)return hans?'正在准备并校验 '+match[1]+'…':'Preparing and verifying '+match[1]+'…';
  match=value.match(/^Java 已啟動，等候遊戲視窗…$/);
  if(match)return hans?'Java 已启动，正在等待游戏窗口…':'Java started; waiting for the game window…';
  match=value.match(/^正在備份世界、模組及遊戲設定…$/);
  if(match)return hans?'正在备份世界、模组和游戏设置…':'Backing up worlds, mods and game settings…';
  if(value==='Mod 已下載並通過 SHA 校驗。')return hans?'Mod 已下载并通过 SHA 校验。':'Mod downloaded and passed SHA verification.';
  if(value==='整合包已下載並通過 SHA 校驗。')return hans?'整合包已下载并通过 SHA 校验。':'Modpack downloaded and passed SHA verification.';
  if(value==='整合包已匯入並完成檔案校驗。')return hans?'整合包已导入并完成文件校验。':'Modpack imported and all files verified.';
  if(value==='正在準備獨立整合包實例…')return hans?'正在准备独立整合包实例…':'Preparing an isolated modpack instance…';
  if(value==='遊戲程序已啟動；請確認已進入 Minecraft 主畫面。')return hans?'游戏程序已启动；请确认已进入 Minecraft 主界面。':'Game process started. Confirm the Minecraft main menu appears.';
  if(value==='已完成')return hans?'已完成':'Complete';
  match=value.match(/^已切換至(淺色|深色)主題。$/);
  if(match)return hans?'已切换至'+(match[1]==='淺色'?'浅色':'深色')+'主题。':(match[1]==='淺色'?'Switched to light theme.':'Switched to dark theme.');
  match=value.match(/^版本清單已更新：正式版 (\d+)、快照／愚人節 (\d+)、Beta (\d+)、Alpha (\d+)；另找到 (\d+) 個本機版本。$/);
  if(match)return hans?'版本列表已更新：正式版 '+match[1]+'、快照／愚人节 '+match[2]+'、Beta '+match[3]+'、Alpha '+match[4]+'；另找到 '+match[5]+' 个本机版本。':'Catalog updated: '+match[1]+' releases, '+match[2]+' snapshots / April Fools, '+match[3]+' Beta, '+match[4]+' Alpha; '+match[5]+' local versions found.';
  match=value.match(/^Minecraft 基岩版 (.+)$/);
  if(match)return hans?'Minecraft 基岩版 '+match[1]:'Minecraft Bedrock '+match[1];
  match=value.match(/^正在等候下載完成：(.*)$/);
  if(match)return (hans?'正在等待下载完成：':'Waiting for download to finish: ')+match[1];
  match=value.match(/^下載完成，正在驗證並匯入：(.*)$/);
  if(match)return (hans?'下载完成，正在验证并导入：':'Download finished; verifying and importing: ')+match[1];
  match=value.match(/^已自動匯入 (.*)；請在世界設定中啟用資源包／行為包。$/);
  if(match)return (hans?'已自动导入 '+match[1]+'；请在世界设置中启用资源包／行为包。':'Imported '+match[1]+' automatically. Activate its packs in your world settings.');
  match=value.match(/^無法自動匯入 (.*)：(.*)$/);
  if(match)return (hans?'无法自动导入 '+match[1]+'：'+match[2]:'Could not import '+match[1]+': '+match[2]);
  match=value.match(/^(\d+) 個版本$/);
  if(match)return hans?match[1]+' 个版本':match[1]+' versions';
  match=value.match(/^(\d+) 個世界$/);
  if(match)return hans?match[1]+' 个世界':match[1]+' worlds';
  match=value.match(/^世界備份已建立：(.*)$/);
  if(match)return (hans?'世界备份已创建：':'World backup created: ')+match[1];
  match=value.match(/^已在 Finder 開啟：(.*)$/);
  if(match)return (hans?'已在 Finder 打开：':'Opened in Finder: ')+match[1];
  match=value.match(/^已設定 Bedrock 資料位置：(.*)$/);
  if(match)return (hans?'已设置 Bedrock 数据位置：':'Bedrock data folder set to: ')+match[1];
  match=value.match(/^無法讀取 Bedrock 資料：(.*)$/);
  if(match)return (hans?'无法读取 Bedrock 数据：':'Could not read Bedrock data: ')+match[1];
  match=value.match(/^存檔磁碟可用空間：(.+) GiB（(\d+) bytes）。啟動前會檢查寫入權限。$/);
  if(match)return hans?'存档磁盘可用空间：'+match[1]+' GiB（'+match[2]+' bytes）。启动前会检查写入权限。':'World volume available: '+match[1]+' GiB ('+match[2]+' bytes). Write access is checked before launch.';
  if(value==='無法讀取存檔磁碟空間；啟動前會重新檢查。')return hans?'无法读取存档磁盘空间；启动前会重新检查。':'World volume space is unavailable; it will be checked before launch.';
  return value;
 }
 function apply(language,root=document){const lang=supported.includes(language)?language:'zh-Hant';document.documentElement.lang=lang;const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);let node;while((node=walker.nextNode())){if(!texts.has(node))texts.set(node,node.nodeValue);const original=texts.get(node);const trimmed=original.trim();if(!trimmed)continue;const translated=translate(trimmed,lang);const leading=original.match(/^\s*/)[0],trailing=original.match(/\s*$/)[0];node.nodeValue=leading+translated+trailing;}
  for(const el of root.querySelectorAll('[aria-label],[placeholder],[title]'))for(const name of ['aria-label','placeholder','title']){if(!el.hasAttribute(name))continue;let record=attrs.get(el);if(!record){record={};attrs.set(el,record);}if(!(name in record))record[name]=el.getAttribute(name);el.setAttribute(name,translate(record[name],lang));}
 }
 window.MambaI18n={supported,detect,apply,translate};
})();
