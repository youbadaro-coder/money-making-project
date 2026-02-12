import os

def create_desktop_bat():
    # Target desktop path (OneDrive confirmed)
    desktop = os.path.join(os.environ['USERPROFILE'], 'OneDrive', 'Desktop')
    if not os.path.exists(desktop):
        desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
        
    bat_path = os.path.join(desktop, "바이럴쇼츠_생성하기.bat")
    
    # Use 'cp949' which is the default for Korean Windows CMD
    content = '@echo off\ncall "c:\\ai작업\\anti\\수익화에이전트첫걸음\\바이럴쇼츠_생성하기.bat"\npause'
    
    try:
        with open(bat_path, 'w', encoding='cp949') as f:
            f.write(content)
        print(f"Created batch file at: {bat_path}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_desktop_bat()
