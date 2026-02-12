import os
import win32com.client

def create_shortcut():
    desktop = os.path.join(os.environ['USERPROFILE'], 'OneDrive', 'Desktop')
    if not os.path.exists(desktop):
        desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
        
    target = r"c:\ai작업\anti\수익화에이전트첫걸음\바이럴쇼츠_생성하기.bat"
    path = os.path.join(desktop, "바이럴쇼츠_생성하기.lnk")
    
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(path)
    shortcut.Targetpath = target
    shortcut.WorkingDirectory = os.path.dirname(target)
    shortcut.IconLocation = target
    shortcut.save()
    print(f"Shortcut created at: {path}")

if __name__ == "__main__":
    create_shortcut()
