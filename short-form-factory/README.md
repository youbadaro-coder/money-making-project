# 🏭 Short Form Factory (숏폼 팩토리)

## 📌 Overview
이 프로젝트는 **Money-Making-Project**의 핵심 수익화 엔진인 **숏폼 자동 생성 공장**입니다.
AI를 활용하여 주제 선정부터 영상 편집, 업로드까지 전 과정을 자동화합니다.

## 👥 Management
- **General Manager**: Annie (애니 팀장) - 기획 및 총괄
- **Factory Manager**: Kodari (코다리 부장) - 기술 구현 및 운영

## 🛠 Tech Stack
- **Python**: Core Logic
- **MoviePy**: Video Editing
- **Edge-TTS**: AI Voice Generation
- **Google Gemini API**: Script & Topic Research
- **YouTube Data API**: Auto Upload

## 🚀 How to Run
1. `requirements.txt` 설치: `pip install -r requirements.txt`
2. `.env` 파일 설정 (API Key 입력)
3. `ShortsFactory_Launch.bat` 실행

## 📂 Structure
- `execution/`: 실행 스크립트 모음
  - `research_topic.py`: 주제 및 대본 생성
  - `fetch_materials.py`: 영상 소스 수집 (Pexels)
  - `edit_video.py`: 영상 편집 및 자막/오디오 합성
  - `upload_video.py`: 유튜브 업로드
- `server.py`: 대시보드 백엔드 서버
- `dashboard.html`: 제어판 UI

---
*Created by Anti-Gravity Agent & Kodari Manager*
