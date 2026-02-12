import moviepy
print(f"MoviePy Version: {moviepy.__version__}")
print(dir(moviepy))
try:
    from moviepy import VideoFileClip
    print("Imported VideoFileClip from top level")
except ImportError:
    print("Failed to import VideoFileClip from top level")

try:
    from moviepy.editor import VideoFileClip
    print("Imported VideoFileClip from editor")
except ImportError:
    print("Failed to import VideoFileClip from editor")
