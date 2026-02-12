import os
import sys
import subprocess
import time

def run_script(script_name):
    print(f"--- Running {script_name} ---")
    script_path = os.path.join("execution", script_name)
    result = subprocess.run([sys.executable, script_path], capture_output=False)
    if result.returncode != 0:
        print(f"Error running {script_name}. Aborting.")
        return False
    return True

def main():
    print("Starting Daily Shorts Automation Job...")
    
    # 1. Research
    if not run_script("research_topic.py"): return

    # 2. Materials
    if not run_script("fetch_materials.py"): return

    # 3. Edit
    if not run_script("edit_video.py"): return

    # 4. Upload
    if not run_script("upload_video.py"): return

    print("Daily job finished successfully.")

if __name__ == "__main__":
    main()
