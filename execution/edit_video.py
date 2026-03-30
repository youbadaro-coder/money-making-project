import os
import json
import random
import asyncio
import textwrap
import numpy as np
import edge_tts
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips, AudioFileClip, CompositeAudioClip, AudioClip, concatenate_audioclips

# Korean font path
FONT_PATH = "C:/Windows/Fonts/malgunbd.ttf" # Use bold if available
if not os.path.exists(FONT_PATH):
    FONT_PATH = "C:/Windows/Fonts/malgun.ttf"
if not os.path.exists(FONT_PATH):
    FONT_PATH = "arial.ttf"

TEMP_DIR = ".tmp"
VIDEO_OUT_DIR = os.path.join(TEMP_DIR, "videos")
AUDIO_OUT_DIR = os.path.join(TEMP_DIR, "audio")
os.makedirs(AUDIO_OUT_DIR, exist_ok=True)

async def generate_narration(text, voice, output_path):
    """Generates TTS audio file."""
    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)
        return True
    except Exception as e:
        print(f"Error generating narration: {e}", flush=True)
        return False

def create_text_image(text, width=1080, height=1920, fontsize=65, color='white'):
    """
    Creates a transparent PIL Image with wrapped and centered text (White with black stroke).
    """
    try:
        font = ImageFont.truetype(FONT_PATH, fontsize)
    except:
        font = ImageFont.load_default()

    # Wrap text to max 2 lines
    wrapper = textwrap.TextWrapper(width=20) 
    lines = wrapper.wrap(text)[:2]
    
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Calculate metrics
    line_spacing = 15
    ascent, descent = font.getmetrics()
    line_h = ascent + descent + line_spacing
    total_h = len(lines) * line_h

    # USER REQUEST: Position lower (around 82% down)
    current_y = int(height * 0.82) - (total_h // 2)

    # Draw text with STROKE (Black outline)
    for line in lines:
        left, top, right, bottom = font.getbbox(line)
        line_w = right - left
        current_x = (width - line_w) // 2
        
        # White text with Black border
        draw.text((current_x, current_y), line, font=font, fill=color, 
                  stroke_width=2, stroke_fill='black')
        current_y += line_h

    return np.array(img)

async def process_segments(segments, voice_profile, orientation='portrait'):
    """Processes segments IN PARALLEL: generates audio and creates video-audio clips."""
    
    target_w, target_h = (1080, 1920) if orientation == 'portrait' else (1920, 1080)
    
    async def process_single_segment(i, seg):
        text = seg.get('text', "")
        video_path = os.path.join(VIDEO_OUT_DIR, f"segment_{i}.mp4")
        audio_path = os.path.join(AUDIO_OUT_DIR, f"segment_{i}.mp3")
        
        print(f"Processing segment {i} (Parallel): {text[:15]}...", flush=True)
        
        # 1. Generate Narration (TTS)
        if not await generate_narration(text, voice_profile, audio_path):
            return None
            
        # 2. Load Audio
        audio_clip = AudioFileClip(audio_path)
        
        # 3. Load Video and Sync
        if os.path.exists(video_path):
            try:
                # Use threads for faster video loading
                video_clip = VideoFileClip(video_path)
                
                # Resize and Crop
                if video_clip.h != target_h:
                    video_clip = video_clip.resized(height=target_h)
                
                if video_clip.w > target_w:
                    video_clip = video_clip.cropped(x1=video_clip.w/2 - target_w/2, y1=0, width=target_w, height=target_h)
                elif video_clip.w < target_w:
                    video_clip = video_clip.resized(width=target_w)
                    video_clip = video_clip.cropped(x1=0, y1=video_clip.h/2 - target_h/2, width=target_w, height=target_h)
                
                # Sync logic with 0.8s padding per segment for much smoother narration flow
                padding_duration = 0.8
                silence = AudioClip(frame_function=lambda t: [0, 0], duration=padding_duration, fps=44100)
                audio_clip = concatenate_audioclips([audio_clip, silence])
                duration = audio_clip.duration

                if video_clip.duration < duration:
                    n_loops = int(np.ceil(duration / video_clip.duration))
                    video_clip = concatenate_videoclips([video_clip] * n_loops)
                
                video_clip = video_clip.subclipped(0, duration).with_audio(audio_clip)
                
                # 4. Add Caption Overlay
                txt_img = create_text_image(text, width=target_w, height=target_h)
                txt_clip = ImageClip(txt_img).with_duration(duration).with_position('center')
                
                composite_seg = CompositeVideoClip([video_clip, txt_clip])
                
                return composite_seg
            except Exception as e:
                print(f"Error processing segment {i}: {e}")
                return None
        return None

    # Run all segments in parallel!
    tasks = [process_single_segment(i, seg) for i, seg in enumerate(segments)]
    results = await asyncio.gather(*tasks)
    
    # Filter out failed segments
    return [r for r in results if r is not None]

def get_best_codec():
    """Detects if NVIDIA NVENC is available for hardware acceleration."""
    import subprocess
    target = "h264_nvenc"
    try:
        cmd = ["ffmpeg", "-encoders"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        if target in result.stdout:
            print(f"--- GPU Acceleration Enabled: {target} ---", flush=True)
            return target
    except:
        pass
    print("--- GPU Acceleration Not Found. Falling back to CPU (libx264) ---", flush=True)
    return "libx264"

async def edit_video():
    input_path = os.path.join(TEMP_DIR, 'topic_data.json')
    if not os.path.exists(input_path):
        print("topic_data.json not found.")
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    segments = data.get('segments', [])
    voice_profile = data.get('voice_profile', "ko-KR-SunHiNeural")
    format_type = str(data.get('format', 'short')).lower()
    orientation = data.get('orientation', 'portrait')
    
    if not segments:
        print("No segments found in data.")
        return

    print(f"--- Starting Final Rendering Engine (Format: {format_type}) ---", flush=True)
    
    # Process Segments
    segment_clips = await process_segments(segments, voice_profile, orientation)
    
    if not segment_clips:
        print("No clips were successfully processed.", flush=True)
        return

    # Concatenate all segments
    final_video = concatenate_videoclips(segment_clips, method="compose")
    
    # 5. Add Background Music (BGM)
    bgm_path = os.path.join(TEMP_DIR, 'bgm.mp3')
    if os.path.exists(bgm_path):
        try:
            bgm_clip = AudioFileClip(bgm_path)
            # Loop BGM to match video duration
            bgm_clip = bgm_clip.loop(duration=final_video.duration)
            bgm_clip = bgm_clip.volumex(0.15) 
            
            # Mix with narration
            final_audio = CompositeAudioClip([final_video.audio, bgm_clip])
            final_video = final_video.with_audio(final_audio)
            print("Successfully mixed background music.", flush=True)
        except Exception as e:
            print(f"Error adding BGM: {e}", flush=True)

    # FINAL AUDIO PROTECTION: Add 1.5s silence at the very end to prevent cutoff
    final_silence = AudioClip(frame_function=lambda t: [0, 0], duration=1.5, fps=44100)
    final_audio_padded = concatenate_audioclips([final_video.audio, final_silence])
    
    # Ensure video duration matches audio exactly
    final_video = final_video.with_duration(final_audio_padded.duration).with_audio(final_audio_padded)
    
    # Limit duration (Long-form up to 300s)
    max_duration = 60.0 if format_type == 'short' else 310.0
    if final_video.duration > max_duration:
        final_video = final_video.with_duration(max_duration).subclipped(0, max_duration)

    # Output path
    output_path = os.path.join(TEMP_DIR, 'final_video.mp4')
    
    # GPU Acceleration Setup
    best_codec = get_best_codec()
    ffmpeg_params = ["-hwaccel", "cuda", "-hwaccel_output_format", "cuda"] if best_codec == "h264_nvenc" else []
    if best_codec == "h264_nvenc":
        ffmpeg_params.extend(["-preset", "p4", "-tune", "hq"])

    print(f"Exporting final video (Threads: 8, Codec: {best_codec})", flush=True)
    print(f"[PROGRESS] 95%", flush=True)
    
    final_video.write_videofile(
        output_path, 
        fps=24, 
        codec=best_codec, 
        audio_codec="aac",
        ffmpeg_params=ffmpeg_params,
        threads=8,
        logger=None # Reduce output noise
    )
    
    print("--- Video Production Complete! ---", flush=True)
    print(f"[PROGRESS] 100%", flush=True)

if __name__ == "__main__":
    asyncio.run(edit_video())
