import os

def fix_all_launchers_final():
    base_dir = r"c:\ai작업\anti\수익화에이전트첫걸음\short-form-factory"
    root_dir = r"c:\ai작업\anti\수익화에이전트첫걸음"
    python_exe = r"c:\안티작업\.bin\python\python.exe"
    
    # 1. ShortsFactory_Launch.bat (Internal Launcher)
    # Simplify the script to reduce failure points
    factory_launch_bat = os.path.join(base_dir, "ShortsFactory_Launch.bat")
    factory_content = f'''@echo off
title Shorts Factory Studio
cd /d "{base_dir}"

echo --- Shorts Factory Studio Server ---
echo.
echo [1/1] Starting Factory Backend (Flask)...
start /b "" "{python_exe}" "{os.path.join(base_dir, "server.py")}"

echo.
echo [SUCCESS] Studio Dashboard is ready!
echo Launching browser for the Chairman...
timeout /t 3 > nul
start http://localhost:5000

echo.
echo ==========================================
echo  FACTORY SERVER IS ACTIVE IN BACKGROUND
echo  Close this window to stop the server later.
echo ==========================================
echo Running at http://localhost:5000
pause
'''
    with open(factory_launch_bat, 'w', encoding='cp949') as f:
        f.write(factory_content)
    print(f"Fixed: {factory_launch_bat}")

    # 2. root_dir\바이럴쇼츠_생성하기.bat
    root_bat = os.path.join(root_dir, "바이럴쇼츠_생성하기.bat")
    root_content = f'''@echo off
cd /d "{base_dir}"
call "{factory_launch_bat}"
'''
    with open(root_bat, 'w', encoding='cp949') as f:
        f.write(root_content)
    print(f"Fixed: {root_bat}")

    # 3. Desktop Shortcut
    desktop = os.path.join(os.environ['USERPROFILE'], 'OneDrive', 'Desktop')
    if not os.path.exists(desktop):
        desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
    
    desktop_bat = os.path.join(desktop, "바이럴쇼츠_생성하기.bat")
    desktop_content = f'''@echo off
call "{root_bat}"
'''
    with open(desktop_bat, 'w', encoding='cp949') as f:
        f.write(desktop_content)
    print(f"Fixed: {desktop_bat}")

if __name__ == "__main__":
    fix_all_launchers_final()
