import os
import subprocess
import sys
from flask import Flask, request, jsonify, send_from_directory, Response

from flask_cors import CORS

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BIN_PYTHON = os.path.join(BASE_DIR, ".bin", "python", "python.exe")
TMP_DIR = os.path.join(BASE_DIR, ".tmp")

# Force UTF-8 encoding for console logs
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def run_script_yield(script_path, args=None):
    """Executes a script and yields its output line by line."""
    cmd = [BIN_PYTHON, script_path]
    if args:
        cmd.extend(args)
    
    print(f"Executing: {' '.join(cmd)}", flush=True)
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True,
        cwd=BASE_DIR
    )
    
    for line in iter(process.stdout.readline, ""):
        msg = line.strip()
        if msg:
            print(f"Script output: {msg}", flush=True)
            yield f"data: {msg}\n\n"
    
    process.stdout.close()
    return_code = process.wait()
    print(f"Process finished with code {return_code}", flush=True)
    yield f"data: [DONE] Process finished with code {return_code}\n\n"

@app.route('/')
def index():
    return send_from_directory(BASE_DIR, 'dashboard.html')

@app.route('/dashboard.js')
def serve_js():
    return send_from_directory(BASE_DIR, 'dashboard.js')

@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.json
    topic = data.get('topic', '')
    category = data.get('category', 'Touching')
    style = data.get('style', 'Cinematic')
    persona = data.get('persona', 'kodari')
    
    def stream():
        yield "data: [SERVER] Connected\n\n"
        yield f"data: 🚀 {persona.upper()}: 의장님, 요청하신 주제로 창작을 시작합니다! [{style}]\n\n"
        
        # Step 1: Research
        yield f"data: 📝 {persona.upper()}: 의장님 스타일의 감각적인 기획안을 작성 중입니다...\n\n"
        # Passing: category, topic, style
        yield from run_script_yield(os.path.join(BASE_DIR, "execution", "research_topic.py"), [category, topic, style])
        
        # Step 2: Fetch Materials
        yield f"data: 🎬 {persona.upper()}: 기획에 딱 맞는 고화질 영상들을 수집하고 있습니다...\n\n"
        yield from run_script_yield(os.path.join(BASE_DIR, "execution", "fetch_materials.py"))
        
        # Step 3: Edit Video
        yield f"data: ✂️ {persona.upper()}: 성우급 AI 음성과 음악, 자막을 입히는 중입니다. 잠시만요!\n\n"
        yield from run_script_yield(os.path.join(BASE_DIR, "execution", "edit_video.py"))
        
        yield f"data: ✅ {persona.upper()}: 짜잔! 월드클래스 쇼츠가 완성되었습니다. 프리뷰를 확인하세요!\n\n"

    return Response(stream(), mimetype='text/event-stream', headers={
        'Cache-Control': 'no-cache',
        'X-Accel-Buffering': 'no',
        'Connection': 'keep-alive'
    })

@app.route('/video')
def get_video():
    return send_from_directory(TMP_DIR, 'final_video.mp4')

if __name__ == '__main__':
    # Ensure .tmp exists
    os.makedirs(TMP_DIR, exist_ok=True)
    print(f"Starting server at http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
