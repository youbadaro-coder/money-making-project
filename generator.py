import os
import json
import logging
# from google import genai
# from google.genai import types

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_shorts_data(topic: str) -> dict:
    """
    안티그라비티(Antigravity) 내부에서 호출되거나, API 백엔드에서 호출될 핵심 비즈니스 로직.
    사용자의 '주제(Topic)'를 받아 제미나이(Gemini) API를 통해 유튜브 숏폼 대본과 이미지 프롬프트를 생성합니다.
    """
    logging.info(f"Generating shorts content for topic: {topic}")
    
    # 1. 제미나이 API 클라이언트 초기화 (실제 운영 시 주석 해제)
    # api_key = os.environ.get("GEMINI_API_KEY")
    # if not api_key:
    #     raise ValueError("GEMINI_API_KEY environment variable is not set.")
    # client = genai.Client(api_key=api_key)

    # 2. 강력한 시스템 프롬프트 (System Prompt) 작성
    # 안티그라비티 지식베이스를 활용해 가장 터질 확률이 높은 숏폼 구조(훅-전개-결론)를 강제합니다.
    prompt = f"""
    너는 세계 최고의 유튜브 숏폼 마케팅 전문가이자 미드저니 프롬프트 엔지니어 매니저야.
    다음 주제에 대한 30초 분량(약 120자 내외)의 유튜브 숏폼 대본과, 각 장면에 매칭되는 고퀄리티 영어 미드저니 이미지 프롬프트 3개를 작성해줘.
    
    주제: {topic}
    
    다음 JSON 형식으로만 정확히 반환해:
    {{
        "title": "시선을 끄는 자극적이고 호기심을 유발하는 영상 제목",
        "script": "(0~3초 훅) ...\\n(4~15초 전개) ...\\n(16~30초 결론) ...",
        "hashtags": "#해시태그1 #해시태그2 #해시태그3",
        "prompts": [
            "[Scene 1] 영어로 된 매우 구체적인 미드저니 프롬프트 (조명, 구도, 화풍 포함) --ar 9:16",
            "[Scene 2] 영어로 된 두 번째 미드저니 프롬프트 --ar 9:16",
            "[Scene 3] 영어로 된 세 번째 미드저니 프롬프트 --ar 9:16"
        ]
    }}
    """
    
    # 3. 모델 호출 (실제 구현 시 이 부분을 사용)
    # try:
    #     response = client.models.generate_content(
    #         model='gemini-2.5-flash',
    #         contents=prompt,
    #         config=types.GenerateContentConfig(
    #             response_mime_type="application/json",
    #         ),
    #     )
    #     return json.loads(response.text)
    # except Exception as e:
    #     logging.error(f"Gemini API Error: {e}")
    #     raise

    # [MVP 시뮬레이션용 하드코딩 반환 데이터]
    # 프론트엔드 HTML/JS에서 보여줄 데이터와 동일한 구조
    simulated_result = {
        "title": f"[충격] {topic}의 진짜 얼굴... 당신만 몰랐던 비밀 😱",
        "script": f"(0~3초 후킹)\n다들 {topic} 좋다고 난리죠? 근데 진짜 그럴까요? 속지 마세요.\n\n(4~15초 전개)\n사실 이 안에는 엄청난 비밀이 숨겨져 있습니다.\n연구 결과에 따르면 우리의 뇌는 충격적인 사실에 80% 더 반응한다고 해요.\n\n(16~30초 결론)\n오늘부터 이것만 기억하세요. 인생이 달라질 겁니다!\n자세한 내용은 고정 댓글 확인!",
        "hashtags": f"#{topic.replace(' ', '')} #비밀공개 #인생꿀팁 #충격과공포",
        "prompts": [
            f"Cinematic lighting, extreme close up, a person looking shocked at a glowing smartphone screen reading about {topic} in a dark room, neon cyberpunk vibe, hyper realistic --ar 9:16",
            f"A minimalist flat vector illustration representing the hidden secrets of {topic}, magnifying glass over a glowing brain, modern tech aesthetic --ar 9:16",
            f"Documentary style professional photograph, wide angle, silhouette of a person standing at the edge of a cliff overlooking a futuristic city at sunset, contemplating {topic} --ar 9:16"
        ]
    }
    
    logging.info("Content generation successful.")
    return simulated_result

if __name__ == "__main__":
    # 안티그라비티 시스템 내에서 직접 이 스크립트를 실행해 볼 수 있는 테스트 블록
    test_topic = "1인 기업 생존 전략"
    print(f"--- 테스트 시작: '{test_topic}' ---")
    result = generate_shorts_data(test_topic)
    print(json.dumps(result, ensure_ascii=False, indent=4))
    print("--- 테스트 종료 ---")
