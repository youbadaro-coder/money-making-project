Set WshShell = WScript.CreateObject("WScript.Shell")
strDesktop = WshShell.SpecialFolders("Desktop")
' If Desktop points to OneDrive, strDesktop will already have it correctly.
Set oShortcut = WshShell.CreateShortcut(strDesktop & "\바이럴쇼츠_생성하기.lnk")
oShortcut.TargetPath = "c:\ai작업\anti\수익화에이전트첫걸음\바이럴쇼츠_생성하기.bat"
oShortcut.WorkingDirectory = "c:\ai작업\anti\수익화에이전트첫걸음"
oShortcut.Save
WScript.Echo "Shortcut created successfully on " & strDesktop
