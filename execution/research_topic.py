import os
import json
import random
import google.generativeai as genai
from dotenv import load_dotenv
import sys
from datetime import datetime

# Load environment variables
load_dotenv()

print("Environment loaded.", flush=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")

genai.configure(api_key=GEMINI_API_KEY)

CATEGORIES = ["Touching", "Provocative", "Knowledge", "Funny", "Calm"]

def research_topic(category=None, user_topic=None, user_style=None, format_type='short', orientation='portrait', references=''):
    """
    Selects a category and uses Gemini to generate a video topic and script.
    """
    print(f"[PROGRESS] 10%", flush=True)
    selected_category = category if category else random.choice(CATEGORIES)
    selected_style = user_style if user_style else "Cinematic"
    
    print(f"Selected Category: {selected_category}", flush=True)
    print(f"Selected Style: {selected_style}", flush=True)
    if references:
        print(f"Applying Style Reference: {references[:50]}...", flush=True)
    
    topic_context = f"Topic hint: {user_topic}" if user_topic else "Auto-generate a creative viral topic."

    # Load History
    history_path = os.path.join('data', 'history.json')
    history_data = []
    if os.path.exists(history_path):
        try:
            with open(history_path, 'r', encoding='utf-8') as f:
                history_data = json.load(f)
        except:
            history_data = []
    
    # Last 5 topics for context
    history_context = ", ".join([h.get('topic', '') for h in history_data[-5:]]) if history_data else "None yet."

    duration_prompt = "approximately **50-55 seconds**." if format_type == 'short' else "approximately **2-3 minutes**."
    num_segments = "8-10 fast segments (to fill ~50s)." if format_type == 'short' else "15-20 segments (to fill 2-3 minutes)."

    model = genai.GenerativeModel('gemini-1.5-pro')
    
    # STYLE REFERENCE INJECTION
    ref_prompt = ""
    if references:
        ref_prompt = f"""
        [STYLE & CONTENT REFERENCES]
        The user has provided the following YouTube URLs or style descriptions:
        "{references}"
        
        Analyze these references for:
        1. **Tone & Pacing**: Is it fast-paced, calm, provocative, or professional?
        2. **Script Structure**: How does it hook the user? How are the facts presented?
        3. **Caption/Subtitle Style**: Should the text be punchy, short, or descriptive?
        
        Mimic this style for the new video generation while using the new topic.
        """

    prompt = f"""
    You are 'Annie', a provocative and genius Content Director.
    Your goal is to create a **VIRAL YOUTUBE VIDEO** that keeps viewers hooked for {duration_prompt}
    
    Category: "{selected_category}"
    Visual Style: "{selected_style}"
    Context: {topic_context}
    
    {ref_prompt}

    [STRATEGY: THE DOPAMINE HOOK]
    1. **The Hook (0-3s)**: Must be shocking, a weird question, or a bold statement.
    2. **The Body**: Fast-paced facts or storytelling. No fluff.
    3. **The Twist/CTA**: Leave them thinking.

    [STRICT CONTENT RULES]
    - **Tone**: Provocative, "Spicy", Emotional, or Mind-Blowing.
    - **Language**: Korean (Native, trendy slang allowed).
    - **Visuals**: 
        - If Style is "Stick Figure", use keywords like "minimalist stick figure illustration", "whiteboard design", "simple line art".
        - If Style is "Sketch", use "charcoal drawing", "pencil illustration", "artistic sketch background", "hand-drawn artistic subject". **NEVER use keywords like 'hand', 'pen', 'writing', or 'drawing action'. Focus only on the artistic result.**
        - If Style is "Anime", use "high quality anime style", "makoto shinkai aesthetic", "vibrant anime colors".
        - For others, use HIGHLY specific professional cinematography terms.

    - **History Context**: Use the following previous topics to ensure variety and avoid repetition:
    {history_context}

    Please generate a JSON object with:
    - "topic": A clickbait-style title (Korean).
    - "narration_tone": "Fast & Intense" or "Deep & Mysterious".
    - "voice_profile": "ko-KR-SunHiNeural" (Femme Fatale) or "ko-KR-InJoonNeural".
    - "bgm_style": "Phaking Phonk", "Dark Synth", or "Emotional Piano".
    - "segments": {num_segments} Each has:
        - "text": Narration (Short, punchy Korean sentences).
        - "pexels_search": English keywords matching the VISUAL STYLE.
    - "description": Viral description with hashtags.

    Output ONLY raw JSON.
    """

    try:
        print("[DEBUG] Sending prompt to Gemini Model...", flush=True)
        response = model.generate_content(prompt)
        
        # Check safety/block
        if not response.text:
            print(f"[ERROR] Gemini returned empty response. Prompt might be blocked.", flush=True)
            if hasattr(response, 'prompt_feedback'):
                print(f"[SAFETY FEEDBACK] {response.prompt_feedback}", flush=True)
            return None
            
        print("[DEBUG] Received response from Gemini. Parsing...", flush=True)
        text_response = response.text.replace('```json', '').replace('```', '').strip()
        data = json.loads(text_response)
        
        data['category'] = selected_category
        data['style'] = selected_style
        data['format'] = format_type
        data['orientation'] = orientation
        data['timestamp'] = datetime.now().isoformat()
        
        # Save to .tmp for current run
        os.makedirs('.tmp', exist_ok=True)
        output_path = os.path.join('.tmp', 'topic_data.json')
        print(f"[DEBUG] Saving data to {output_path}...", flush=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        # Append to History
        os.makedirs('data', exist_ok=True) # Ensure data directory exists
        history_data.append({
            "topic": data.get('topic'),
            "category": selected_category,
            "style": selected_style,
            "timestamp": data['timestamp']
        })
        # Keep last 50 entries
        with open(history_path, 'w', encoding='utf-8') as f:
            json.dump(history_data[-50:], f, ensure_ascii=False, indent=2)

        print(f"Successfully generated topic data mimicking reference style.", flush=True)
        print(f"[PROGRESS] 25%", flush=True)
        return data

    except Exception as e:
        print(f"Error generating topic: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    arg_category = sys.argv[1] if len(sys.argv) > 1 else None
    arg_topic = sys.argv[2] if len(sys.argv) > 2 else None
    arg_style = sys.argv[3] if len(sys.argv) > 3 else "Cinematic"
    arg_format = sys.argv[4] if len(sys.argv) > 4 else "short"
    arg_orientation = sys.argv[5] if len(sys.argv) > 5 else "portrait"
    arg_references = sys.argv[6] if len(sys.argv) > 6 else ""
    research_topic(arg_category, arg_topic, arg_style, arg_format, arg_orientation, arg_references)
