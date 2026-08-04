import os
import sys

def create_lnk():
    try:
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")
        root = os.path.abspath(".")
        target = os.path.join(root, "dashboard", "dist-electron", "win-unpacked", "RASD-Maroc.exe")
        shortcut_path = os.path.join(root, "Lancer-RASD-Maroc.lnk")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.TargetPath = target
        shortcut.WorkingDirectory = os.path.dirname(target)
        shortcut.save()
        print(f"[OK] Raccourci cree : {shortcut_path}")
    except Exception as e:
        print(f"Error creating shortcut: {e}")

if __name__ == "__main__":
    create_lnk()
