Set WshShell = CreateObject("WScript.Shell")
strPath = WshShell.CurrentDirectory & "\dashboard\dist-electron\win-unpacked\RASD-Maroc.exe"
WshShell.Run """" & strPath & """", 1, False
