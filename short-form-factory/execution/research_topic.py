import os
import json
import random
import google.generativeai as genai
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

print("Environment loaded.", flush=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")

genai.configure(api_key=GEMINI_API_KEY)

CATEGORIES = ["Touching", "Provocative", "Knowledge", "Funny", "Calm"]

def research_topic(category=None, user_topic=None, user_style=None):
    """
    Selects a category and uses Gemini to generate a video topic and script.
    """
    selected_category = category if category else random.choice(CATEGORIES)
    selected_style = user_style if user_style else "Cinematic"
    
    print(f"Selected Category: {selected_category}", flush=True)
    print(f"Selected Style: {selected_style}", flush=True)
    
    topic_context = f"Topic hint: {user_topic}" if user_topic else "Auto-generate a creative viral topic."

    model = genai.GenerativeModel('gemini-2.0-flash')
    
    prompt = f"""
    You are 'Annie', a provocative and genius Content Director.
    Your goal is to create a **VIRAL YOUTUBE SHORT** that keeps viewers hooked for approximately **50-55 seconds**.
    
    Category: "{selected_category}"
    Visual Style: "{selected_style}"
    Context: {topic_context}
    
    [STRATEGY: THE DOPAMINE HOOK]
    1. **The Hook (0-3s)**: Must be shocking, a weird question, or a bold statement.
    2. **The Body**: Fast-paced facts or storytelling. No fluff.
    3. **The Twist/CTA**: Leave them thinking.

    [STRICT CONTENT RULES]
    - **Tone**: Provocative, "Spicy", Emotional, or Mind-Blowing.
    - **Language**: Korean (Native, trendy slang allowed).
    - **Visuals**: 
        - If Style is "Stick Figure", use keywords like "minimalist stick figure animation", "whiteboard animation", "simple line drawing".
        - If Style is "Sketch", use "pencil drawing", "charcoal sketch", "hand drawn notebook".
        - If Style is "Anime", use "high quality anime style", "makoto shinkai aesthetic", "vibrant anime colors".
        - For others, use HIGHLY specific professional cinematography terms.

    Please generate a JSON object with:
    - "topic": A clickbait-style title (Korean).
    - "narration_tone": "Fast & Intense" or "Deep & Mysterious".
    - "voice_profile": "ko-KR-SunHiNeural" (Femme Fatale) or "ko-KR-InJoonNeural".
    - "bgm_style": "Phonk", "Dark Synth", or "Emotional Piano".
    - "segments": 8-10 fast segments (to fill ~50s). Each has:
        - "text": Narration (Short, punchy Korean sentences).
        - "pexels_search": English keywords matching the VISUAL STYLE.
    - "description": Viral description with hashtags.

    Output ONLY raw JSON.
    """

    try:
        response = model.generate_content(prompt)
        text_response = response.text.replace('```json', '').replace('```', '').strip()
        data = json.loads(text_response)
        
        data['category'] = selected_category
        data['style'] = selected_style
        
        os.makedirs('.tmp', exist_ok=True)
        output_path = os.path.join('.tmp', 'topic_data.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        print(f"Successfully generated topic data: {output_path}", flush=True)
        return data

    except Exception as e:
        print(f"Error generating topic: {e}")
        return None

if __name__ == "__main__":
    arg_category = sys.argv[1] if len(sys.argv) > 1 else None
    arg_topic = sys.argv[2] if len(sys.argv) > 2 else None
    arg_style = sys.argv[3] if len(sys.argv) > 3 else "Cinematic"
    research_topic(arg_category, arg_topic, arg_style)
