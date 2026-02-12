import os
import json
import random
import shutil
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
LOCAL_VIDEO_DIR = r"d:\안티작업\0211"

def fetch_from_pexels(keywords):
    if not PEXELS_API_KEY:
        print("PEXELS_API_KEY not found in .env. Skipping Pexels search.")
        return []

    print(f"Searching Pexels for: {keywords}")
    headers = {"Authorization": PEXELS_API_KEY}
    
    # Use the first 2-3 keywords for a broader search
    query = " ".join(keywords[:3])
    url = f"https://api.pexels.com/videos/search?query={query}&orientation=portrait&per_page=10"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        results = response.json()
        
        video_links = []
        for video in results.get('videos', []):
            # Get the best vertical HD file
            video_files = video.get('video_files', [])
            # Filter for mp4 and reasonable resolution
            best_file = None
            for f in video_files:
                if f['file_type'] == 'video/mp4':
                    if not best_file or (f['width'] or 0) > (best_file['width'] or 0):
                        best_file = f
            
            if best_file:
                video_links.append(best_file['link'])
        
        return video_links
    except Exception as e:
        print(f"Error searching Pexels: {e}")
        return []

def download_video(url, dest_path):
    try:
        print(f"Downloading {url} to {dest_path}...")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(dest_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                 f.write(chunk)
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

def fetch_materials():
    # Load topic data
    input_path = os.path.join('.tmp', 'topic_data.json')
    if not os.path.exists(input_path):
        print("topic_data.json not found. Run research_topic.py first.")
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    segments = data.get('segments', [])
    bgm_style = data.get('bgm_style', "Cinematic")
    output_dir = os.path.join('.tmp', 'videos')
    os.makedirs(output_dir, exist_ok=True)
    
    # Clear existing videos
    for f in os.listdir(output_dir):
        if f.endswith('.mp4'):
            try:
                os.remove(os.path.join(output_dir, f))
            except:
                pass # Already handled by server restart logic

    print(f"Collecting materials for {len(segments)} segments...")
    collected_count = 0

    for i, seg in enumerate(segments):
        search_terms = seg.get('pexels_search', "emotional")
        if isinstance(search_terms, list):
            queries = search_terms
        else:
            queries = [search_terms]
            
        success = False
        # Try specific queries
        for query in queries:
            print(f"Segment {i}: Searching Pexels for '{query}'...")
            video_links = fetch_from_pexels([query])
            if video_links:
                dest = os.path.join(output_dir, f"segment_{i}.mp4")
                if download_video(video_links[0], dest):
                    collected_count += 1
                    success = True
                    break
        
        # Try general topic keywords if specific fails
        if not success:
            top_words = data.get('topic', "").split()[:2]
            print(f"Segment {i}: Specific search failed. Trying topic keywords: {top_words}")
            video_links = fetch_from_pexels(top_words)
            if video_links:
                dest = os.path.join(output_dir, f"segment_{i}.mp4")
                if download_video(video_links[0], dest):
                    collected_count += 1
                    success = True

        # Final local fallback
        if not success:
            print(f"Segment {i}: Pexels failed completely. Falling back to local...")
            if os.path.exists(LOCAL_VIDEO_DIR):
                all_files = os.listdir(LOCAL_VIDEO_DIR)
                video_files = [f for f in all_files if f.lower().endswith('.mp4')]
                if video_files:
                    src_path = os.path.join(LOCAL_VIDEO_DIR, random.choice(video_files))
                    dst_path = os.path.join(output_dir, f"segment_{i}.mp4")
                    shutil.copy2(src_path, dst_path)
                    collected_count += 1

    # BGM Sourcing (Placeholder for now, but we can try to download a generic one)
    # In a real scenario, we'd have a library of BGM files.
    # For this lab, let's download a sample royalty-free track if possible.
    bgm_path = os.path.join('.tmp', 'bgm.mp3')
    if not os.path.exists(bgm_path):
        sample_bgm_url = "https://www.chosic.com/wp-content/uploads/2021/07/Slow-Cinematic-Background-Music.mp3"
        print(f"Downloading sample BGM: {sample_bgm_url}")
        download_video(sample_bgm_url, bgm_path)

    print(f"Total materials collected: {collected_count} segments in {output_dir}")

if __name__ == "__main__":
    fetch_materials()
