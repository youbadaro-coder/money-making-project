"""
server.py - Shorts Factory V2 Backend (Job-based polling architecture)
=======================================================================
SSE/chunked-transfer-encoding 방식은 Windows Werkzeug에서 불안정합니다.
대신 백그라운드 쓰레드로 파이프라인을 실행하고,
프론트엔드는 /api/status 엔드포인트를 polling하는 방식을 사용합니다.
"""

import os
import subprocess
import sys
import json
import queue
import threading
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
BIN_PYTHON = sys.executable
TMP_DIR    = os.path.join(BASE_DIR, ".tmp")
os.makedirs(TMP_DIR, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# Global job state (one job at a time is sufficient for this single-user tool)
# ─────────────────────────────────────────────────────────────────────────────

_job_lock   = threading.Lock()
_job_status = {
    "running":   False,
    "done":      False,
    "error":     None,
    "progress":  0,     # 0-100 percentage
    "messages":  [],   # list of str, newest at end
    "cursor":    0,    # next unread index (used by polling)
}

def _job_reset():
    with _job_lock:
        _job_status.update(running=True, done=False, error=None, messages=[], cursor=0, progress=0)
    
    # 🚨 CRITICAL: Delete old results to prevent duplication
    try:
        for f in ["topic_data.json", "final_video.mp4"]:
            p = os.path.join(TMP_DIR, f)
            if os.path.exists(p):
                os.remove(p)
                print(f"--- Deleted stale file: {f} ---")
    except Exception as e:
        print(f"Error clearing stale data: {e}")

def _job_push(msg: str):
    with _job_lock:
        # Check if message is a progress update: [PROGRESS] X%
        if "[PROGRESS]" in msg:
            try:
                prog_str = msg.split("[PROGRESS]")[1].split("%")[0].strip()
                _job_status["progress"] = int(prog_str)
                return # Don't push progress messages to the log array
            except:
                pass
        _job_status["messages"].append(msg)

def _run_script(script_path, args=None):
    """Run a Python script and push each output line into _job_status['messages']."""
    cmd = [BIN_PYTHON, script_path]
    if args:
        cmd.extend([str(a) for a in args])

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"

    _job_push(f"[실행중] {os.path.basename(script_path)}")
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            cwd=BASE_DIR,
            env=env,
        )
        for raw in iter(process.stdout.readline, b""):
            line = raw.decode("utf-8", errors="replace").rstrip()
            if line:
                _job_push(line)
        process.stdout.close()
        rc = process.wait()
        _job_push(f"[완료] {os.path.basename(script_path)} (exit={rc})")
        return rc == 0
    except Exception as e:
        _job_push(f"[에러] {e}")
        return False


def _pipeline_worker(topics, category, style, persona, format_type, orientation, is_bulk, references):
    """Runs the full 3-step pipeline for one or multiple topics with aggregate progress."""
    print(f"--- Pipeline Starting with Topics: {topics} (Format: {format_type}) ---", flush=True)
    if references:
        print(f"--- Style References Provided: {references[:100]}... ---", flush=True)
    try:
        total_topics = len(topics)
        for idx, topic in enumerate(topics):
            current_topic_num = idx + 1
            topic = str(topic).strip()
            if not topic:
                continue
            
            # 🚨 CRITICAL: Remove specific data for this run to avoid duplication
            try:
                for f in ["topic_data.json", "final_video.mp4"]:
                    p = os.path.join(TMP_DIR, f)
                    if os.path.exists(p):
                        os.remove(p)
            except:
                pass
                
            prefix = f"[{current_topic_num}/{total_topics}] " if total_topics > 1 else ""
            _job_push(f"🚀 {prefix}{persona.upper()}: '{topic}' 주제로 시작합니다!")

            # 헬퍼 함수: 하위 작업의 %를 전체 %로 변환
            def _push_agg_progress(sub_prog):
                agg = ((current_topic_num - 1) / total_topics) * 100 + (sub_prog / total_topics)
                _job_status["progress"] = int(agg)

            # STEP 1
            _job_push(f"{prefix}📝 [STEP 1] 대본 작성 중...")
            _push_agg_progress(10)
            ok = _run_script(os.path.join(BASE_DIR, "execution", "research_topic.py"),
                             [category, topic, style, format_type, orientation, references])
            if not ok:
                err_msg = f"{prefix}❌ [STEP 1] 대본 작성 실패. 중단합니다."
                _job_push(err_msg)
                with _job_lock:
                    _job_status["error"] = err_msg
                break

            # Push script data to UI immediately
            try:
                data_path = os.path.join(TMP_DIR, "topic_data.json")
                if os.path.exists(data_path):
                    with open(data_path, 'r', encoding='utf-8') as f:
                        script_content = json.load(f)
                        display_data = {
                            "title": script_content.get("title", ""),
                            "script": script_content.get("script", ""),
                            "hashtags": script_content.get("hashtags", "")
                        }
                        _job_push(f"[SCRIPT_DATA] {json.dumps(display_data)}")
            except Exception as e:
                print(f"Error pushing script data: {e}")

            # STEP 2
            _job_push(f"{prefix}🎬 [STEP 2] 영상 소스 수집 중...")
            _push_agg_progress(30)
            # CRITICAL: ensure Step 2 only runs if Step 1 succeeded (topic_data exists)
            if not os.path.exists(os.path.join(TMP_DIR, "topic_data.json")):
                err_msg = f"{prefix}❌ [STEP 2] 주제 데이터가 생성되지 않았습니다."
                _job_push(err_msg)
                with _job_lock:
                    _job_status["error"] = err_msg
                break

            ok = _run_script(os.path.join(BASE_DIR, "execution", "fetch_materials.py"))
            if not ok:
                _job_push(f"{prefix}⚠️ 일부 소스 수집 실패 (계속 진행)")

            # STEP 3
            _job_push(f"{prefix}✂️ [STEP 3] 나레이션 합성 & 영상 편집 중... (수분 소요)")
            _push_agg_progress(60)
            ok = _run_script(os.path.join(BASE_DIR, "execution", "edit_video.py"))
            if not ok:
                err_msg = f"{prefix}❌ [STEP 3] 영상 편집 실패. 중단합니다."
                _job_push(err_msg)
                with _job_lock:
                    _job_status["error"] = err_msg
                break

            _push_agg_progress(100)
            
            # FINAL TRUTH CHECK: Verify if the file actually exists
            final_path = os.path.join(TMP_DIR, "final_video.mp4")
            if not os.path.exists(final_path):
                err_msg = f"{prefix}❌ 영상 합성이 완료되었으나 파일이 존재하지 않습니다."
                _job_push(err_msg)
                with _job_lock:
                    _job_status["error"] = err_msg
                break

            # 덮어쓰기 방지 처리 (Bulk Mode)
            if is_bulk:
                import shutil
                original_final = os.path.join(TMP_DIR, "final_video.mp4")
                if os.path.exists(original_final):
                    # Sanitize topic for filename
                    safe_topic = "".join(c for c in topic if c.isalnum() or c in " _-").strip().replace(' ', '_')
                    bulk_filename = f"final_video_{current_topic_num}_{safe_topic}.mp4"
                    bulk_out = os.path.join(TMP_DIR, bulk_filename)
                    shutil.copy2(original_final, bulk_out)
                    _job_push(f"{prefix}📁 영상 저장됨: {bulk_filename}")

        if not _job_status["error"]:
            if total_topics > 1:
                _job_push(f"✅ 완성! 총 {total_topics}개의 숏폼 공장 가동을 성공적으로 마쳤습니다.")
            else:
                _job_push("✅ 완성! 영상 탭에서 결과를 확인하세요!")

    except Exception as e:
        import traceback
        traceback.print_exc()
        _job_push(f"❌ 예상치 못한 오류: {e}")
    finally:
        with _job_lock:
            _job_status["running"] = False
            _job_status["done"]    = True


# ─────────────────────────────────────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")

@app.route("/app.js")
def serve_js():
    return send_from_directory(BASE_DIR, "app.js")

@app.route("/styles.css")
def serve_css():
    return send_from_directory(BASE_DIR, "styles.css")

@app.route("/api/generate", methods=["POST"])
def generate():
    """Start a background pipeline and immediately return 200."""
    data        = request.json or {}
    
    topics      = data.get("topics", [])
    if not topics: # backward compatibility
        legacy_topic = data.get("topic")
        if legacy_topic:
            topics = [legacy_topic]
            
    is_bulk     = data.get("isBulk", False)
    category    = data.get("category", "Touching")
    style       = data.get("style", "Cinematic")
    persona     = data.get("persona", "kodari")
    format_type = data.get("format", "short")
    orientation = data.get("orientation", "portrait")
    references  = data.get("references", "")

    with _job_lock:
        if _job_status["running"]:
            return jsonify({"ok": False, "error": "이미 생성 중입니다."}), 429

    _job_reset()
    t = threading.Thread(
        target=_pipeline_worker,
        args=(topics, category, style, persona, format_type, orientation, is_bulk, references),
        daemon=True,
    )
    t.start()
    return jsonify({"ok": True, "message": "파이프라인 시작됨"})


@app.route("/api/status", methods=["GET"])
def status():
    """Polling endpoint: returns new log messages since last poll."""
    with _job_lock:
        running  = _job_status["running"]
        done     = _job_status["done"]
        error    = _job_status["error"]
        cursor   = _job_status["cursor"]
        all_msgs = _job_status["messages"]

    new_msgs = all_msgs[cursor:]
    new_cursor = cursor + len(new_msgs)

    # advance cursor for next call
    with _job_lock:
        _job_status["cursor"] = new_cursor

    return jsonify({
        "running":  running,
        "done":     done,
        "error":    error,
        "progress": _job_status["progress"],
        "messages": new_msgs,
    })


@app.route("/video")
def get_video():
    return send_from_directory(TMP_DIR, "final_video.mp4")

@app.route("/video/<path:filename>")
def get_bulk_video(filename):
    return send_from_directory(TMP_DIR, filename)


if __name__ == "__main__":
    print("Starting server at http://localhost:5002")
    app.run(host="0.0.0.0", port=5002, debug=False, threaded=True)
