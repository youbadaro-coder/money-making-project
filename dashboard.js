let selectedTone = 'Emotional';
let selectedStyle = 'Cinematic';
let currentPersona = 'kodari';

const logContainer = document.getElementById('log-container');
const outputVideo = document.getElementById('output-video');
const videoPlaceholder = document.getElementById('video-placeholder');
const statusIndicator = document.getElementById('status-indicator');
const generateBtn = document.getElementById('generate-btn');

const PERSONA_MSGS = {
    annie: "자기야, 심리학적으로 사람들을 훅 끌어들일 수 있는 스크립트를 짜볼게. 기대해! 😘",
    shhyong: "대표님, 비주얼은 제가 책임집니다. 최고의 시네마틱 앵글로 가져올게요. (윙크)",
    kodari: "충성! 완벽한 타이밍에 자막과 음악을 입혀보겠습니다. 바로 가시죠!"
};

function selectTone(btn, tone) {
    selectedTone = tone;
    document.querySelectorAll('#tone-picker button').forEach(b => {
        b.className = "glass p-3 rounded-xl border-transparent";
    });
    btn.className = "glass p-3 rounded-xl border-teal-500 bg-teal-500/20 text-white font-medium";
}

function selectStyle(btn, style) {
    selectedStyle = style;
    document.querySelectorAll('#style-picker button').forEach(b => {
        b.className = "glass p-3 rounded-xl border-transparent";
    });
    btn.className = "glass p-3 rounded-xl border-red-500 bg-red-500/20 text-white font-medium";
}

function switchPersona(persona) {
    currentPersona = persona;
    document.getElementById('persona-chat').textContent = `"${PERSONA_MSGS[persona]}"`;

    // Smooth transition for icons
    ['annie', 'shhyong', 'kodari'].forEach(p => {
        const el = document.getElementById(`${p}-icon`);
        if (p === persona) {
            el.classList.add('scale-125', 'border-opacity-100');
            el.classList.remove('opacity-50');
        } else {
            el.classList.remove('scale-125', 'border-opacity-100');
            el.classList.add('opacity-50');
        }
    });
}

function addLog(msg, type = 'info') {
    const div = document.createElement('div');
    const timestamp = new Date().toLocaleTimeString();

    if (msg.startsWith('[START]')) {
        div.className = "text-yellow-400 font-bold mt-2";
    } else if (msg.startsWith('[COMPLETE]')) {
        div.className = "text-pink-400 font-bold mt-2";
    } else if (msg.startsWith('[DONE]')) {
        div.className = "text-slate-500 italic";
    } else {
        div.className = "pl-2";
    }

    div.textContent = `[${timestamp}] ${msg}`;
    logContainer.appendChild(div);
    logContainer.scrollTop = logContainer.scrollHeight;
}

async function startGeneration() {
    const topic = document.getElementById('topic-input').value;

    // UI Setup
    generateBtn.disabled = true;
    generateBtn.classList.add('opacity-50', 'cursor-not-allowed');
    generateBtn.innerHTML = `<span>⏳</span> 생성 중...`;
    statusIndicator.textContent = "Processing pipeline...";

    outputVideo.classList.add('hidden');
    videoPlaceholder.classList.remove('hidden');

    logContainer.innerHTML = '';
    addLog(`Starting production: ${selectedCategory} | ${topic || 'Auto-topic'}`);

    try {
        const response = await fetch('http://localhost:5000/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                topic: topic,
                category: selectedTone,
                tone: selectedTone,
                style: selectedStyle,
                persona: currentPersona
            })
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');

            lines.forEach(line => {
                if (line.startsWith('data: ')) {
                    const msg = line.replace('data: ', '');
                    if (msg.trim()) {
                        addLog(msg);
                        if (msg.includes('완성되었습니다')) {
                            finishGeneration();
                        }
                    }
                }
            });
        }
    } catch (error) {
        addLog(`Error: ${error.message}`, 'error');
        generateBtn.disabled = false;
        generateBtn.classList.remove('opacity-50', 'cursor-not-allowed');
        generateBtn.innerHTML = `✨ 영상 생성 시작`;
    }
}

function finishGeneration() {
    addLog("Pipeline completed successfully!");
    statusIndicator.textContent = "Generation complete!";

    // Refresh video
    const videoUrl = `http://localhost:5000/video?t=${new Date().getTime()}`;
    outputVideo.src = videoUrl;
    outputVideo.classList.remove('hidden');
    videoPlaceholder.classList.add('hidden');
    outputVideo.play();

    generateBtn.disabled = false;
    generateBtn.classList.remove('opacity-50', 'cursor-not-allowed');
    generateBtn.innerHTML = `✨ 영상 생성 시작`;

    alert("자기야! 영상 다 만들었어! 제어판에서 확인해봐. ❤️");
}
