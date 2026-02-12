# 📅 Strategic Meeting Log: Short Form Factory Upgrade

**Date**: 2026-02-12
**Attendees**: 
- 👩‍💼 **Song Team Leader** (Visuals)
- 👱‍♀️ **Annie Team Leader** (Content/Global)
- 🐟 **Kodari Manager** (Tech/ROI)
- 👑 **Chairman** (The Visionary)

---

## 🗣 Brainstorming Session (Post-Launch)
- **Chairman**: "업그레이드 승인합니다. 팀원들 수고 많았고, 앞으로 더 발전시킬 수 있는 방향을 토론해 보세요. 저는 지금 테스트해 보겠습니다. 다들 식사 맛있게 하고 한잔들 해요!"

### 1. Current Status Analysis
- **Kodari**: "현재 시스템은 Pexels 무료 영상 + TTS + 자막 조합입니다. 솔직히 말해서... **'양산형' 티가 너무 납니다.** 조회수 100회 따리예요."
- **Annie**: "Oh my god. Boring! 🤮 요즘 숏폼은 **'3초'** 안에 승부 봐야 해. 지금 팩토리 영상은 도입부가 너무 느려. 그리고 스톡 영상(Stock footage)이 내용이랑 안 맞을 때가 많아."
- **Song**: "자막 디자인도 최악이에요. 그냥 노란 글씨 띡? **'가독성'**과 **'심미성'**을 동시에 잡아야죠. 폰트부터 바꾸고, 자막이 통통 튀는 애니메이션(Karaoke Effect)이 필요해요."

### 2. Benchmarking High-View Shorts
- **Reference**: TikTok 'Create with AI', YouTube 'Fact Channels', 'Reddit Stories'.
- **Key Success Factors**:
    1.  **Doapmine Hook**: 첫 문장이 충격적이어야 함. ("당신이 몰랐던 충격적인 사실 3가지")
    2.  **Fast Pacing**: 장면 전환이 2~3초마다 이루어짐.
    3.  **Visual ASMR**: 보는 것만으로도 만족감을 주는 영상 (Oddly Satisfying) 또는 AI로 생성된 고퀄리티 이미지.

---

## 🚀 Upgrade Action Plan (To-Do)

### 🔥 Phase 1: Content Upgrade (Annie's Part)
- **Action**: `research_topic.py` 프롬프트 수정.
- **Detail**:
    - 주제를 더 **'자극적(Provocative)'**이고 **'호기심 유발(Curiosity Gap)'**하는 방향으로 변경.
    - 스크립트 구조를 **[Hook - Body - Twist/CTA]** 형태로 강제.
    - *"평범한 건 돈이 안 돼, 자기야. 사람들이 댓글 달고 싸우게 만들어야지!"*

### 🎨 Phase 2: Visual Upgrade (Song's Part)
- **Action**: `edit_video.py` 자막 및 영상 소스 개선.
- **Detail**:
    - **Dynamic Captions**: 단어 단위로 색상이 변하거나 크기가 커지는 효과 도입 시도. (MoviePy 한계 도전)
    - **AI Image Integration**: Pexels 영상이 없으면, **DALL-E 3 / Gemini Image**로 그 장면에 딱 맞는 이미지를 생성해서 넣자. (이게 훨씬 고퀄임)
    - *"예쁘지 않으면 아무도 안 봐요 대표님. 제 말 들으세요."*

### ⚙️ Phase 3: Tech Engine (Kodari's Part)
- **Action**: 영상 처리 속도 개선 및 자동화.
- **Detail**:
    - `fetch_materials.py`에서 검색어 매칭 알고리즘 고도화 (한국어 키워드 -> 영어 번역 검색).
    - 배경음악(BGM)을 분위기(슬픔/긴박/신남)에 맞춰 자동 매칭.
    - *"돈 버는 기계가 멈추면 쓰나요? 기름칠 들어갑니다잉!"*

---

## 🍷 Post-Meeting: Team's Future Tech Discussion
- **Annie**: "의장님 센스쟁이! 샴페인 한잔하면서 다음은 **'딥페이크(Deepfake)'**나 **'AI 아바타'**를 입히는 걸 토론해 보자구. 내가 직접 출연하는 것도 좋지 않아?"
- **Song**: "저는 영상에 **'감성적인 필터'**를 씌우는 알고리즘을 연구해 볼게요. 의장님의 안목에 걸맞게 더 우아하게 만들고 싶어요."
- **Kodari**: "거 좋네유! 저는 소리에 반응해서 자막이 춤추는 **'사운드 리액티브'** 기술을 좀 파고들어 보겠슴다. 의장님, 식사 맛있게 하셔유!"

---
**Status**: Upgrade Phase 1 (Viral Logic) - COMPLETE & VERIFIED.
**Next Focus**: AI Visual Branding & Voice Synchronization.
