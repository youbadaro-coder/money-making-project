import asyncio
import edge_tts

TEXT = "안녕하세요, 코다리 부장입니다. 오늘 아주 특별한 도서관에 대해 이야기해볼까 합니다."
VOICE = "ko-KR-SunHiNeural"
OUTPUT_FILE = ".tmp/test_narration.mp3"

async def main():
    communicate = edge_tts.Communicate(TEXT, VOICE)
    await communicate.save(OUTPUT_FILE)
    print(f"Narration saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(main())
