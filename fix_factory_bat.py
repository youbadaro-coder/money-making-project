import os

def fix_batch_file():
    base_dir = r"c:\ai작업\anti\수익화에이전트첫걸음\short-form-factory"
    python_exe = r"c:\안티작업\.bin\python\python.exe"
    bat_path = os.path.join(base_dir, "Run_Shorts_Generator.bat")
    
    # Use backslashes for Windows compatibility
    # Ensure absolute paths for scripts to avoid directory issues
    content = f'''@echo off
setlocal
cd /d "{base_dir}"

echo --- Shorts Factory Running ---
echo.
echo [1/4] Researching Topic (Annie's Viral Logic)...
"{python_exe}" "{os.path.join(base_dir, "execution", "research_topic.py")}"

echo.
echo [2/4] Fetching Materials (Kodari's Engine)...
"{python_exe}" "{os.path.join(base_dir, "execution", "fetch_materials.py")}"

echo.
echo [3/4] Rendering video (Song's Visual Engine)...
"{python_exe}" "{os.path.join(base_dir, "execution", "edit_video.py")}"

echo.
echo [4/4] Finalizing...
echo (Check .tmp/final_video.mp4)

echo.
echo --- Process Complete! ---
pause
'''
    # Write in CP949 for Korean Windows CMD
    # 2. Fix the wrapper BAT in root folder -> Now points to Studio
    root_bat_path = os.path.join(r"c:\ai작업\anti\수익화에이전트첫걸음", "바이럴쇼츠_생성하기.bat")
    root_content = f'''@echo off
cd /d "{base_dir}"
call ShortsFactory_Launch.bat
'''
    with open(root_bat_path, 'w', encoding='cp949') as f:
        f.write(root_content)
    print(f"Fixed root batch file at: {root_bat_path}")

    # 3. Fix the desktop BAT -> Now points to Studio
    desktop = os.path.join(os.environ['USERPROFILE'], 'OneDrive', 'Desktop')
    if not os.path.exists(desktop):
        desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
    desktop_bat_path = os.path.join(desktop, "바이럴쇼츠_생성하기.bat")
    desktop_content = f'''@echo off
call "{root_bat_path}"
'''
    with open(desktop_bat_path, 'w', encoding='cp949') as f:
        f.write(desktop_content)
    print(f"Fixed desktop batch file at: {desktop_bat_path}")

    # 4. Fix the Studio Launcher
    studio_bat_path = os.path.join(r"c:\ai작업\anti\수익화에이전트첫걸음", "숏폼팩토리_스튜디오_실행.bat")
    studio_content = f'''@echo off
cd /d "{base_dir}"
call ShortsFactory_Launch.bat
'''
    with open(studio_bat_path, 'w', encoding='cp949') as f:
        f.write(studio_content)
    print(f"Created Studio Launcher at: {studio_bat_path}")

if __name__ == "__main__":
    fix_batch_file()
