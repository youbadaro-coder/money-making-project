import os
import json
import random
import asyncio
import textwrap
import numpy as np
import edge_tts
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips, AudioFileClip, CompositeAudioClip

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
        print(f"Error generating narration: {e}")
        return False

def create_text_image(text, width=1080, height=1920, fontsize=70, color='yellow', stroke_color='black', stroke_width=5):
    """
    Creates a transparent PIL Image with wrapped and centered text.
    Yellow text with black outline is standard for engaging shorts.
    """
    try:
        font = ImageFont.truetype(FONT_PATH, fontsize)
    except:
        font = ImageFont.load_default()

    # Wrap text to fit roughly 80% of width
    wrapper = textwrap.TextWrapper(width=15) # Approx characters per line for 1080px
    lines = wrapper.wrap(text)
    
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Calculate total height of the text block to center it vertically
    line_spacing = 15
    # Estimate line height
    ascent, descent = font.getmetrics()
    line_h = ascent + descent + line_spacing
    total_h = len(lines) * line_h

    current_y = (height - total_h) // 2

    for line in lines:
        left, top, right, bottom = font.getbbox(line)
        line_w = right - left
        current_x = (width - line_w) // 2
        
        # Draw outline
        draw.text((current_x, current_y), line, font=font, fill=color, 
                  stroke_width=stroke_width, stroke_fill=stroke_color)
        current_y += line_h

    return np.array(img)

async def process_segments(segments, voice_profile):
    """Processes each segment: generates audio and creates video-audio clips."""
    final_segment_clips = []
    
    for i, seg in enumerate(segments):
        text = seg.get('text', "")
        video_path = os.path.join(VIDEO_OUT_DIR, f"segment_{i}.mp4")
        audio_path = os.path.join(AUDIO_OUT_DIR, f"segment_{i}.mp3")
        
        print(f"Processing segment {i}: {text[:20]}...")
        
        # 1. Generate Narration
        if not await generate_narration(text, voice_profile, audio_path):
            continue
            
        # 2. Load Audio
        audio_clip = AudioFileClip(audio_path)
        duration = audio_clip.duration
        
        # 3. Load Video and Sync
        if os.path.exists(video_path):
            try:
                video_clip = VideoFileClip(video_path)
                
                # Resize and Crop to 1080x1920
                if video_clip.h != 1920:
                    video_clip = video_clip.resized(height=1920)
                
                if video_clip.w > 1080:
                    video_clip = video_clip.cropped(x1=video_clip.w/2 - 540, y1=0, width=1080, height=1920)
                elif video_clip.w < 1080:
                    video_clip = video_clip.resized(width=1080)
                    video_clip = video_clip.cropped(x1=0, y1=video_clip.h/2 - 960, width=1080, height=1920)
                
                # Loop or trim video to match audio duration
                if video_clip.duration < duration:
                    # Repeat the clip to cover the duration
                    n_loops = int(np.ceil(duration / video_clip.duration))
                    video_clip = concatenate_videoclips([video_clip] * n_loops)
                    video_clip = video_clip.subclipped(0, duration)
                else:
                    video_clip = video_clip.subclipped(0, duration)
                
                # Attach Audio
                video_clip = video_clip.with_audio(audio_clip)
                
                # 4. Add Caption Overlay
                txt_img = create_text_image(text)
                txt_clip = ImageClip(txt_img).with_duration(duration).with_position('center')
                
                composite_seg = CompositeVideoClip([video_clip, txt_clip])
                final_segment_clips.append(composite_seg)
                
            except Exception as e:
                print(f"Error processing video for segment {i}: {e}")
                continue
        else:
            print(f"Video for segment {i} not found. Skipping.")

    return final_segment_clips

async def edit_video():
    input_path = os.path.join(TEMP_DIR, 'topic_data.json')
    if not os.path.exists(input_path):
        print("topic_data.json not found.")
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    segments = data.get('segments', [])
    voice_profile = data.get('voice_profile', "ko-KR-SunHiNeural")
    
    if not segments:
        print("No segments found in data.")
        return

    print("--- Starting Superior Rendering Engine ---")
    
    # Process Segments
    segment_clips = await process_segments(segments, voice_profile)
    
    if not segment_clips:
        print("No clips were successfully processed.")
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
            # Lower volume for BGM (Mastering / Ducking)
            bgm_clip = bgm_clip.volumex(0.15) 
            
            # Mix with narration (which is already in final_video.audio)
            final_audio = CompositeAudioClip([final_video.audio, bgm_clip])
            final_video = final_video.with_audio(final_audio)
            print("Successfully mixed background music.")
        except Exception as e:
            print(f"Error adding BGM: {e}")
    
    # Limit to 59 seconds for Shorts
    if final_video.duration > 59:
        final_video = final_video.subclipped(0, 59)

    # Output path
    output_path = os.path.join(TEMP_DIR, 'final_video.mp4')
    
    print(f"Exporting final video: {output_path}")
    final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
    print("--- Video Production Complete! ---")

if __name__ == "__main__":
    asyncio.run(edit_video())
