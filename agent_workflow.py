"""
agent_workflow.py
=========================================
주제(topic) 하나를 입력받으면 3단계 에이전트 파이프라인을 자동 실행합니다.

[STEP 1] 대본 작성         → gemini-2.5-flash  (속도 우선, 한국어 특화)
[STEP 2] 이미지 프롬프트  → claude-3-5-sonnet  (창의성/퀄리티 우선)
[STEP 3] 영상 소스 매칭   → gemini-2.5-flash  (키워드 매칭 속도 우선)

MODEL ROUTING RULES:
  - 감성/창의적 글쓰기  → claude-3-5-sonnet-20241022
  - 심층 분석/긴 추론   → claude-opus-4 (향후 지원 시)
  - 빠른 정보 처리/JSON → gemini-2.5-flash
"""

import os
import json
import sys
import logging
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# 로깅 설정
# ─────────────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
log = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# 환경 설정
# ─────────────────────────────────────────────────────────────────────────────
from dotenv import load_dotenv
load_dotenv()

GEMINI_API_KEY   = os.getenv("GEMINI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")  # optional, can add later

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TMP_DIR  = os.path.join(BASE_DIR, ".tmp")
os.makedirs(TMP_DIR, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# MODEL ROUTER
# ─────────────────────────────────────────────────────────────────────────────

class ModelRouter:
    """
    각 태스크 유형에 맞는 모델을 자동으로 선택합니다.

    Routing Rules
    ─────────────
    script      → gemini-2.5-flash    (빠른 한국어 대본 생성)
    creative    → claude-3-5-sonnet   (창의적 이미지 프롬프트 작성)
    matching    → gemini-2.5-flash    (빠른 JSON 키워드 추출)
    analysis    → gemini-2.5-flash    (claude-opus-4 미지원시 폴백)
    """

    ROUTING_TABLE = {
        "script":   ("gemini",    "gemini-2.5-flash"),
        "creative": ("anthropic", "claude-3-5-sonnet-20241022"),
        "matching": ("gemini",    "gemini-2.5-flash"),
        "analysis": ("gemini",    "gemini-2.5-flash"),  # Opus 폴백
    }

    @classmethod
    def get(cls, task_type: str):
        provider, model = cls.ROUTING_TABLE.get(task_type, ("gemini", "gemini-2.5-flash"))
        log.info(f"[ROUTER] task_type={task_type:12s}  →  provider={provider:10s}  model={model}")
        return provider, model

# ─────────────────────────────────────────────────────────────────────────────
# LLM ADAPTERS
# ─────────────────────────────────────────────────────────────────────────────

def call_gemini(model: str, prompt: str) -> str:
    """Gemini API를 호출합니다."""
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    m = genai.GenerativeModel(model)
    resp = m.generate_content(prompt)
    return resp.text

def call_anthropic(model: str, prompt: str) -> str:
    """Anthropic Claude API를 호출합니다."""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        message = client.messages.create(
            model=model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    except ImportError:
        log.warning("anthropic 패키지 없음 → Gemini 폴백")
        return call_gemini("gemini-2.5-flash", prompt)
    except Exception as e:
        log.error(f"Anthropic API 오류: {e} → Gemini 폴백")
        return call_gemini("gemini-2.5-flash", prompt)

def call_model(task_type: str, prompt: str) -> str:
    """태스크 유형에 따라 적절한 모델을 자동 선택하여 호출합니다."""
    provider, model = ModelRouter.get(task_type)
    if provider == "anthropic" and ANTHROPIC_API_KEY:
        return call_anthropic(model, prompt)
    else:
        # Anthropic 키 없으면 Gemini 폴백
        if provider == "anthropic":
            log.warning("ANTHROPIC_API_KEY 없음 → Gemini 폴백")
        return call_gemini("gemini-2.5-flash", prompt)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1: 대본 작성  (model: gemini-2.5-flash)
# ─────────────────────────────────────────────────────────────────────────────

def step1_write_script(topic: str, format_type: str = "short") -> dict:
    """
    주제를 받아 유튜브 숏폼(또는 롱폼) 대본을 생성합니다.
    Returns: {"title", "narration_tone", "voice_profile", "bgm_style", "segments", "description"}
    """
    log.info("=" * 60)
    log.info(f"STEP 1 | 대본 작성  (topic: {topic}, format: {format_type})")
    log.info("=" * 60)

    duration = "50-55초" if format_type == "short" else "2-3분"
    n_segments = "8-10개" if format_type == "short" else "15-20개"

    prompt = f"""
너는 세계 최고의 한국 유튜브 숏폼 크리에이터야. 바이럴 확률이 높은 대본을 JSON으로 출력해.

주제: {topic}
목표 길이: {duration}
세그먼트 수: {n_segments}

JSON 형식 (다른 텍스트 없이 순수 JSON만 출력):
{{
  "title": "클릭베이트 제목 (한국어)",
  "narration_tone": "Fast & Intense 또는 Deep & Mysterious",
  "voice_profile": "ko-KR-SunHiNeural 또는 ko-KR-InJoonNeural",
  "bgm_style": "Phonk, Dark Synth, 또는 Emotional Piano",
  "segments": [
    {{"text": "한국어 나레이션 문장", "pexels_search": "English keyword for stock footage"}}
  ],
  "description": "유튜브 설명 + 해시태그 (한국어)"
}}
"""
    raw = call_model("script", prompt)
    raw = raw.replace("```json", "").replace("```", "").strip()
    data = json.loads(raw)
    log.info(f"STEP 1 완료. 제목: {data.get('title')}")
    return data

# ─────────────────────────────────────────────────────────────────────────────
# STEP 2: 이미지 프롬프트 생성  (model: claude-3-5-sonnet → Gemini 폴백)
# ─────────────────────────────────────────────────────────────────────────────

def step2_generate_image_prompts(script_data: dict, orientation: str = "portrait") -> list:
    """
    대본의 각 세그먼트에 대해 창의적인 미드저니/DALL-E 이미지 프롬프트를 생성합니다.
    Returns: list of str
    """
    log.info("=" * 60)
    log.info(f"STEP 2 | 이미지 프롬프트 생성  (orientation: {orientation})")
    log.info("=" * 60)

    ar = "9:16" if orientation == "portrait" else "16:9"
    segments_text = "\n".join([f"- [{i+1}] {s['text']}" for i, s in enumerate(script_data.get("segments", []))])
    title = script_data.get("title", "")

    prompt = f"""
You are a world-class Midjourney/DALL-E prompt engineer.
Create one vivid, cinematic image prompt for each segment below.
Each prompt must be in English and highly descriptive (mood, lighting, color, composition).

Video Title (for context): {title}
Orientation: {ar}

Segments:
{segments_text}

Return ONLY a JSON array of strings, one prompt per segment, no extra text:
["prompt for segment 1", "prompt for segment 2", ...]
Each prompt must end with --ar {ar}
"""
    raw = call_model("creative", prompt)
    raw = raw.replace("```json", "").replace("```", "").strip()
    prompts = json.loads(raw)
    log.info(f"STEP 2 완료. {len(prompts)}개 프롬프트 생성.")
    return prompts

# ─────────────────────────────────────────────────────────────────────────────
# STEP 3: 영상 소스 매칭  (model: gemini-2.5-flash)
# ─────────────────────────────────────────────────────────────────────────────

def step3_match_video_sources(script_data: dict, image_prompts: list, orientation: str = "portrait") -> list:
    """
    각 세그먼트에 Pexels 검색용 최적 키워드를 AI로 정제합니다.
    Returns: list of {"segment": int, "pexels_query": str, "image_prompt": str}
    """
    log.info("=" * 60)
    log.info("STEP 3 | 영상 소스 매칭 (Pexels 키워드 최적화)")
    log.info("=" * 60)

    segments = script_data.get("segments", [])
    raw_keywords = [s.get("pexels_search", "") for s in segments]

    prompt = f"""
You are a stock footage expert. For each segment, provide the most effective English Pexels video search keyword.
Orientation: {orientation}

Segments (segment text → original keyword):
{json.dumps([{"text": s["text"], "keyword": k} for s, k in zip(segments, raw_keywords)], ensure_ascii=False, indent=2)}

Return ONLY a JSON array of optimized English search queries (one per segment):
["query1", "query2", ...]
Rules:
- Max 3 words per query
- Avoid abstract terms, be visual
- Match the {orientation} video format
"""
    raw = call_model("matching", prompt)
    raw = raw.replace("```json", "").replace("```", "").strip()
    optimized = json.loads(raw)

    result = []
    for i, (seg, img_prompt, query) in enumerate(zip(segments, image_prompts, optimized)):
        result.append({
            "segment": i + 1,
            "text": seg["text"],
            "pexels_query": query,
            "image_prompt": img_prompt
        })

    log.info(f"STEP 3 완료. {len(result)}개 세그먼트 매칭.")
    return result

# ─────────────────────────────────────────────────────────────────────────────
# MAIN PIPELINE
# ─────────────────────────────────────────────────────────────────────────────

def run_pipeline(topic: str, format_type: str = "short", orientation: str = "portrait") -> dict:
    """
    주제(topic)를 받아 전체 3단계 파이프라인을 순서대로 실행합니다.

    Returns:
        {
          "topic": str,
          "format": str,
          "orientation": str,
          "script": dict,
          "image_prompts": list,
          "video_sources": list,
          "timestamp": str
        }
    """
    log.info("★★★ AGENT PIPELINE START ★★★")
    log.info(f"  topic={topic}  format={format_type}  orientation={orientation}")

    # STEP 1
    script_data = step1_write_script(topic, format_type)

    # STEP 2
    image_prompts = step2_generate_image_prompts(script_data, orientation)

    # STEP 3
    video_sources = step3_match_video_sources(script_data, image_prompts, orientation)

    # 결과 저장
    output = {
        "topic": topic,
        "format": format_type,
        "orientation": orientation,
        "script": script_data,
        "image_prompts": image_prompts,
        "video_sources": video_sources,
        "timestamp": datetime.now().isoformat()
    }

    # .tmp/topic_data.json 에 저장 (기존 파이프라인과 호환)
    out_path = os.path.join(TMP_DIR, "topic_data.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({**script_data, "format": format_type, "orientation": orientation}, f, ensure_ascii=False, indent=2)

    pipeline_out = os.path.join(TMP_DIR, "pipeline_output.json")
    with open(pipeline_out, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    log.info("★★★ AGENT PIPELINE COMPLETE ★★★")
    log.info(f"  결과 저장: {pipeline_out}")
    return output

# ─────────────────────────────────────────────────────────────────────────────
# CLI ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AI Agent Workflow for Shorts/Long-form Video")
    parser.add_argument("topic",       type=str, help="영상 주제 (한국어 OK)")
    parser.add_argument("--format",    type=str, default="short", choices=["short", "long"], help="영상 포맷")
    parser.add_argument("--orient",    type=str, default="portrait", choices=["portrait", "landscape"], help="화면 방향")
    args = parser.parse_args()

    result = run_pipeline(args.topic, args.format, args.orient)
    print("\n" + "=" * 60)
    print("PIPELINE OUTPUT SUMMARY")
    print("=" * 60)
    print(f"Title   : {result['script'].get('title')}")
    print(f"Segments: {len(result['video_sources'])}")
    print(f"Saved at: {os.path.join(TMP_DIR, 'pipeline_output.json')}")
