on launchMamba()
    set resourcesDir to (POSIX path of (path to me)) & "Contents/Resources/"
    set dataDir to (POSIX path of (path to home folder)) & "Library/Application Support/MambaCraft1"
    try
        set pythonExec to do shell script "/bin/cat " & quoted form of (resourcesDir & "python-path.txt")
        do shell script quoted form of pythonExec & " " & quoted form of (resourcesDir & "app/desktop.py") & " --data " & quoted form of dataDir
    on error errorMessage
        display dialog "MambaCraft 無法啟動。" & return & return & errorMessage & return & return & "可重新執行 Install.command 修復啟動器。" with title "MambaCraft" buttons {"完成"} default button "完成" with icon caution
    end try
end launchMamba

on open location incomingURL
    -- Custom URLs open native choosers only. They carry no paths or commands.
    if incomingURL is "mambacraft://choose-folder" then
        my chooseGameFolder()
    else if incomingURL is "mambacraft://choose-java-root" then
        my chooseJavaRoot()
    else if incomingURL is "mambacraft://choose-bedrock-root" then
        my chooseBedrockRoot()
    else if incomingURL is "mambacraft://import-bedrock-package" then
        my importBedrockPackage()
    else
        my launchMamba()
    end if
end open location

on chooseGameFolder()
    try
        set selectedFolder to choose folder with prompt "選擇 Minecraft 遊戲根目錄、versions 資料夾或啟動器 instances 資料夾"
        set folderPath to POSIX path of selectedFolder
        set resourcesDir to (POSIX path of (path to me)) & "Contents/Resources/"
        set dataDir to (POSIX path of (path to home folder)) & "Library/Application Support/MambaCraft1"
        set pythonExec to do shell script "/bin/cat " & quoted form of (resourcesDir & "python-path.txt")
        set resultText to do shell script quoted form of pythonExec & " " & quoted form of (resourcesDir & "app/desktop.py") & " --data " & quoted form of dataDir & " --add-root " & quoted form of folderPath
        display dialog resultText buttons {"好"} default button "好" with title "MambaCraft"
        my launchMamba()
    on error errorMessage number errorNumber
        if errorNumber is not -128 then
            display dialog "無法加入 Minecraft 資料夾。" & return & return & errorMessage with title "MambaCraft" buttons {"完成"} default button "完成" with icon caution
        end if
    end try
end chooseGameFolder

on chooseJavaRoot()
    try
        set selectedFolder to choose folder with prompt "選擇 Java 安裝／搜尋資料夾。沒有相容 Java 時，MambaCraft 會將所需版本下載到這裡。"
        set folderPath to POSIX path of selectedFolder
        set resourcesDir to (POSIX path of (path to me)) & "Contents/Resources/"
        set dataDir to (POSIX path of (path to home folder)) & "Library/Application Support/MambaCraft1"
        set pythonExec to do shell script "/bin/cat " & quoted form of (resourcesDir & "python-path.txt")
        set resultText to do shell script quoted form of pythonExec & " " & quoted form of (resourcesDir & "app/desktop.py") & " --data " & quoted form of dataDir & " --set-java-root " & quoted form of folderPath
        display dialog resultText buttons {"好"} default button "好" with title "MambaCraft"
        my launchMamba()
    on error errorMessage number errorNumber
        if errorNumber is not -128 then
            display dialog "無法設定 Java 資料夾。" & return & return & errorMessage with title "MambaCraft" buttons {"完成"} default button "完成" with icon caution
        end if
    end try
end chooseJavaRoot

on chooseBedrockRoot()
    try
        set selectedFolder to choose folder with prompt "選擇 mcpelauncher 的資料根目錄，也可以選 versions 或 games/com.mojang 子資料夾。"
        set folderPath to POSIX path of selectedFolder
        set resourcesDir to (POSIX path of (path to me)) & "Contents/Resources/"
        set dataDir to (POSIX path of (path to home folder)) & "Library/Application Support/MambaCraft1"
        set pythonExec to do shell script "/bin/cat " & quoted form of (resourcesDir & "python-path.txt")
        set resultText to do shell script quoted form of pythonExec & " " & quoted form of (resourcesDir & "app/desktop.py") & " --data " & quoted form of dataDir & " --set-bedrock-root " & quoted form of folderPath
        display dialog resultText buttons {"好"} default button "好" with title "MambaCraft"
        my launchMamba()
    on error errorMessage number errorNumber
        if errorNumber is not -128 then
            display dialog "無法設定 Bedrock 資料夾。" & return & return & errorMessage with title "MambaCraft" buttons {"完成"} default button "完成" with icon caution
        end if
    end try
end chooseBedrockRoot

on run
    my launchMamba()
end run

on importBedrockPackage()
    try
        set selectedFiles to choose file with prompt "選擇 Minecraft Android APK、XAPK、APKS、APKM 或 ZIP。分割 APK 請同時選齊 base 和 split。" with multiple selections allowed
        set resourcesDir to (POSIX path of (path to me)) & "Contents/Resources/"
        set dataDir to (POSIX path of (path to home folder)) & "Library/Application Support/MambaCraft1"
        set pythonExec to do shell script "/bin/cat " & quoted form of (resourcesDir & "python-path.txt")
        set commandText to quoted form of pythonExec & " " & quoted form of (resourcesDir & "app/desktop.py") & " --data " & quoted form of dataDir & " --import-bedrock"
        repeat with selectedFile in selectedFiles
            set commandText to commandText & " " & quoted form of (POSIX path of selectedFile)
        end repeat
        set resultText to do shell script commandText
        display dialog resultText buttons {"好"} default button "好" with title "MambaCraft"
    on error errorMessage number errorNumber
        if errorNumber is not -128 then
            display dialog "無法匯入 Bedrock 安裝包。" & return & return & errorMessage with title "MambaCraft" buttons {"完成"} default button "完成" with icon caution
        end if
    end try
end importBedrockPackage
