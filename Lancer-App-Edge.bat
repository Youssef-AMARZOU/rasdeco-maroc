@echo off
title RASD Maroc — Mode Application Bureau Edge
echo Lancement du serveur local et de l'interface en mode App Desktop...

start "" msedge.exe --app="http://localhost:3000" --window-size=1400,900 --user-data-dir="%TEMP%\RASD_Maroc_Edge_Profile"
exit
