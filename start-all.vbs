' RASD-Maroc — Lancement silencieux
Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

rasdDir = fso.GetParentFolderName(WScript.ScriptFullName)

' Kill existing Electron processes
WshShell.Run "taskkill /F /IM electron.exe", 0, True

' Use direct electron binary path to avoid npx overhead
electronPath = rasdDir & "\node_modules\electron\dist\electron.exe"
mainPath = rasdDir & "\electron\main.js"
WshShell.Run """" & electronPath & """ """ & mainPath & """", 0, False
