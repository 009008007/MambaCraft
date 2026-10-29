# MambaCraft macOS 1.3 RC22

MambaCraft 是 macOS 上的 Minecraft 啟動器，提供 Java 版本管理、Fabric、Mods、整合包和第三方皮膚站帳號。基岩版功能屬於相容性預覽。

## 下載與安裝

請從此專案的 GitHub Releases 下載發佈 ZIP，完整解壓後雙擊 `Start.command`。更新前請先儲存並退出遊戲及舊版啟動器。安裝需要 macOS 和 Python 3.10 或更新版本；首次啟動會以套件內的依賴建立 Python 環境。

遊戲資料預設位於 `~/Library/Application Support/MambaCraft1`。更新啟動器時會保留這個資料夾中的遊戲資料。`Uninstall.command` 則可永久刪除啟動器管理的資料及世界，執行前會要求明確確認。

## 帳號與目前限制

- 支援本地玩家，以及 LittleSkin 等相容 Yggdrasil 的皮膚站。登入憑證儲存在 macOS 鑰匙圈。
- Microsoft Java 登入使用瀏覽器裝置代碼流程。此專案的 Client ID 仍須通過 Minecraft Services 審核；在官方接受之前，正版登入可能回傳 `Invalid app registration`。相關資訊見 [Minecraft 官方說明](https://aka.ms/AppRegInfo)。正版登入、皮膚及遊戲流程尚待實機驗收。
- 不包含 Minecraft 遊戲本體；使用者須自行取得遊戲及相關授權。Bedrock 的實機進入世界及存檔功能仍需驗證。
