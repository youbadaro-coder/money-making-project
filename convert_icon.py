import os
from PIL import Image

def convert_to_ico(source_path, target_path):
    print(f"Converting {source_path} to {target_path}...")
    try:
        img = Image.open(source_path)
        # Resize to standard icon sizes and save as ICO
        icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        img.save(target_path, format='ICO', sizes=icon_sizes)
        print("Success!")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    src = r"d:\안티작업\0211\shhyong_character.png"
    dst = r"d:\안티작업\shortcuts_icon.ico"
    convert_to_ico(src, dst)
