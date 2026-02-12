from moviepy import ColorClip
import sys

print("Testing MoviePy effects...", flush=True)
try:
    clip = ColorClip(size=(100,100), color=(255,0,0), duration=1)
    
    # Test resize
    try:
        if hasattr(clip, 'resize'):
            print("clip.resize exists")
        else:
            print("clip.resize missing")
    except Exception as e:
        print(f"Error checking resize: {e}")

    try:
        if hasattr(clip, 'resized'):
            print("clip.resized exists")
        else:
            print("clip.resized missing")
    except Exception as e:
        print(f"Error checking resized: {e}")

    # Test crop
    try:
        if hasattr(clip, 'crop'):
            print("clip.crop exists")
        else:
            print("clip.crop missing")
    except Exception as e:
        print(f"Error checking crop: {e}")
        
    try:
        if hasattr(clip, 'cropped'):
            print("clip.cropped exists")
        else:
            print("clip.cropped missing")
    except Exception as e:
        print(f"Error checking cropped: {e}")

except Exception as e:
    print(f"Fatal error: {e}")

print("Test complete.")
