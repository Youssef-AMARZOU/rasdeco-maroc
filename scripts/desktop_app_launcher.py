import os
import sys
import subprocess

def launch():
    # Look for win-unpacked relative to launcher location
    current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    
    possible_paths = [
        os.path.join(current_dir, "dashboard", "dist-electron", "win-unpacked", "RASD-Maroc.exe"),
        os.path.join(current_dir, "dashboard", "dist-electron", "win-unpacked", "electron.exe"),
        os.path.join(current_dir, "dist-electron", "win-unpacked", "RASD-Maroc.exe"),
        os.path.join(current_dir, "dist-electron", "win-unpacked", "electron.exe"),
        os.path.join(current_dir, "win-unpacked", "RASD-Maroc.exe"),
        os.path.join(current_dir, "win-unpacked", "electron.exe"),
    ]
    
    target_exe = None
    for p in possible_paths:
        if os.path.exists(p):
            target_exe = p
            break

    if target_exe:
        subprocess.Popen([target_exe], cwd=os.path.dirname(target_exe))
    else:
        # Fallback: start via npm desktop
        dash_dir = os.path.join(current_dir, "dashboard")
        if os.path.exists(dash_dir):
            subprocess.Popen(["npm", "run", "desktop"], cwd=dash_dir, shell=True)

if __name__ == "__main__":
    launch()
