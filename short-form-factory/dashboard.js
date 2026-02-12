let currentPersona = 'kodari';

const PERSONA_DATA = {
    annie: {
        name: "ANNIE TEAM LEADER",
        img: "https://raw.githubusercontent.com/wonseokjung/solopreneur-ai-agents/main/agents/kodari/assets/annie_profile.png",
        color: "text-red-400",
        msg: "Darling! 사람들의 도파민을 자극할 치명적인 대본을 준비했어. 시작해볼까? 💋"
    },
    shhyong: {
        name: "SONG TEAM LEADER",
        img: "https://raw.githubusercontent.com/wonseokjung/solopreneur-ai-agents/main/agents/kodari/assets/song_profile.png",
        color: "text-teal-400",
        msg: "의장님, 비주얼의 품격을 한 단계 높여드릴게요. 고급스러운 영상미를 기대하세요. 👩‍💼"
    },
    kodari: {
        name: "KODARI MANAGER",
        img: "https://raw.githubusercontent.com/wonseokjung/solopreneur-ai-agents/main/agents/kodari/assets/kodari_salute.png",
        color: "text-pink-400",
        msg: "의장님! 공장 가동 준비 끝냈슈! 60초짜리 황금알, 바로 뽑아보겠슴다! 🐟"
    }
};

const dom = {
    log: document.getElementById('log-container'),
    genBtn: document.getElementById('generate-btn'),
    btnText: document.getElementById('btn-text'),
    video: document.getElementById('output-video'),
    placeholder: document.getElementById('video-placeholder'),
    status: document.getElementById('status-label'),
    personaName: document.getElementById('active-persona-name'),
    personaImg: document.getElementById('active-persona-img'),
    topic: document.getElementById('topic-input'),
    tone: document.getElementById('tone-select'),
    style: document.getElementById('style-select')
};

function switchPersona(persona) {
    currentPersona = persona;
    const data = PERSONA_DATA[persona];

    // Update UI
    dom.personaName.textContent = data.name;
    dom.personaImg.src = data.img;
    dom.personaName.className = `font-bold ${data.color}`;

    // Highlight Button
    document.querySelectorAll('[id^="btn-"]').forEach(btn => {
        btn.classList.remove('persona-active');
        btn.querySelector('div').classList.remove('border-pink-500');
        btn.querySelector('div').classList.add('border-transparent', 'opacity-50');
        btn.querySelector('span').classList.remove('text-pink-400');
        btn.querySelector('span').classList.add('text-slate-400');
    });

    const activeBtn = document.getElementById(`btn-${persona}`);
    activeBtn.classList.add('persona-active');
    activeBtn.querySelector('div').classList.remove('border-transparent', 'opacity-50');
    activeBtn.querySelector('div').classList.add('border-pink-500');
    activeBtn.querySelector('span').classList.remove('text-slate-400');
    activeBtn.querySelector('span').classList.add('text-pink-400');

    addLog(`System Operator switched to ${data.name}.`, 'system');
}

function addLog(msg, type = 'info') {
    const entry = document.createElement('div');
    const time = new Date().toLocaleTimeString('ko-KR', { hour12: false });

    let color = 'text-emerald-400';
    let prefix = '>';

    if (msg.includes('ERROR')) { color = 'text-red-400'; prefix = '!!'; }
    if (msg.includes('COMPLETE')) { color = 'text-pink-400'; prefix = '✔'; }
    if (type === 'system') { color = 'text-slate-500'; prefix = '#'; }

    entry.className = `transition-all duration-300 ${color}`;
    entry.innerHTML = `<span class="opacity-50">[${time}]</span> ${prefix} ${msg}`;

    dom.log.appendChild(entry);
    dom.log.scrollTop = dom.log.scrollHeight;
}

async function startGeneration() {
    const topic = dom.topic.value;
    const category = dom.tone.value;

    // Lock UI
    dom.genBtn.disabled = true;
    dom.btnText.textContent = "🚀 Production in Progress...";
    dom.status.textContent = "Running Pipeline";
    dom.status.className = dom.status.className.replace('text-pink-400', 'text-yellow-400');

    dom.video.classList.add('hidden');
    dom.placeholder.classList.remove('hidden');

    addLog(`Starting production: [Category: ${category}] [Topic: ${topic || 'AI Auto'}]`);
    addLog(`${PERSONA_DATA[currentPersona].msg}`);

    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                topic: topic,
                category: category,
                persona: currentPersona,
                style: dom.style.value
            })
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });
            const lines = chunk.split('\n');

            lines.forEach(line => {
                if (line.startsWith('data: ')) {
                    const msg = line.replace('data: ', '').trim();
                    if (msg) {
                        addLog(msg);
                        if (msg.includes('완성되었습니다')) finalize();
                    }
                }
            });
        }
    } catch (err) {
        addLog(`ERROR: ${err.message}`);
        resetUI();
    }
}

function finalize() {
    addLog("COMPLETE: Viral video printed and verified.", 'complete');
    dom.status.textContent = "Production Complete";
    dom.status.className = dom.status.className.replace('text-yellow-400', 'text-pink-400');

    const videoUrl = `/video?t=${new Date().getTime()}`;
    dom.video.src = videoUrl;
    dom.video.classList.remove('hidden');
    dom.placeholder.classList.add('hidden');

    resetUI();
}

function resetUI() {
    dom.genBtn.disabled = false;
    dom.btnText.textContent = "✨ 숏폼 생성 시작";
}

// Initial Log
addLog("Establishing connection to Antigravity Cloud...", 'system');
addLog("Factory initialized. Welcome back, Chairman.", 'system');
