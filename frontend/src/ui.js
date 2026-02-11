// Data for Kodari's messages
const KODARI_MESSAGES = {
    focus: [
        "대표님, 지금 이 25분이 미래를 바꿉니다! 집중 가즈아!",
        "방해 금지! 코다리가 입구 지키고 있겠습니다! 😎",
        "크으~ 대표님의 집중하는 모습, 너무 섹시(?)하십니다!",
        "한 번만 더 집중하면 성공입니다! 맡겨만 주십시오!"
    ],
    break: [
        "고생하셨습니다! 커피 한 잔의 여유 어떠신가요? ☕",
        "5분만 푹 쉬고 오세요. 코다리도 좀 쉬겠습니다. 🐟",
        "대표님, 스트레칭 한 번 쭈욱~ 하시죠!",
        "잠깐 쉬어야 뇌가 돌아갑니다. 역시 대표님의 안목!"
    ]
};

const RADIUS = 110;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

// UI Module
export const UI = {
    elements: {
        timerDisplay: document.getElementById('timer-display'),
        progressRing: document.getElementById('timer-progress'),
        statusBadge: document.getElementById('status-badge'),
        startBtn: document.getElementById('start-btn'),
        pauseBtn: document.getElementById('pause-btn'),
        resetBtn: document.getElementById('reset-btn'),
        focusTab: document.getElementById('focus-tab'),
        breakTab: document.getElementById('break-tab'),
        sessionCountDisplay: document.getElementById('session-count'),
        kodariMsg: document.getElementById('kodari-msg'),
        weeklyChart: document.getElementById('weekly-chart')
    },

    init() {
        this.elements.progressRing.style.strokeDasharray = CIRCUMFERENCE;
    },

    updateTimer(minutes, seconds) {
        this.elements.timerDisplay.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        document.title = `(${this.elements.timerDisplay.textContent}) 코다리 뽀모도로`;
    },

    updateProgress(ratio) {
        const offset = CIRCUMFERENCE - (ratio * CIRCUMFERENCE);
        this.elements.progressRing.style.strokeDashoffset = offset;
    },

    toggleButtons(isRunning) {
        if (isRunning) {
            this.elements.startBtn.classList.add('hidden');
            this.elements.pauseBtn.classList.remove('hidden');
        } else {
            this.elements.startBtn.classList.remove('hidden');
            this.elements.pauseBtn.classList.add('hidden');
        }
    },

    updateMode(isFocus) {
        if (isFocus) {
            this.elements.statusBadge.textContent = "FOCUS TIME 🎯";
            this.elements.statusBadge.className = "bg-pink-500/10 text-pink-400 px-4 py-1 rounded-full text-sm font-bold border border-pink-500/20 inline-block animate-bounce-subtle";
            this.elements.progressRing.style.stroke = "#ec4899";
            this.elements.focusTab.className = "flex-1 py-2 text-sm font-bold rounded-lg bg-pink-500/20 text-pink-200 transition-all";
            this.elements.breakTab.className = "flex-1 py-2 text-sm font-bold rounded-lg text-slate-400 hover:text-white transition-all";
        } else {
            this.elements.statusBadge.textContent = "BREAK TIME ☕";
            this.elements.statusBadge.className = "bg-emerald-500/10 text-emerald-400 px-4 py-1 rounded-full text-sm font-bold border border-emerald-500/20 inline-block animate-bounce-subtle";
            this.elements.progressRing.style.stroke = "#10b981";
            this.elements.breakTab.className = "flex-1 py-2 text-sm font-bold rounded-lg bg-emerald-500/20 text-emerald-200 transition-all";
            this.elements.focusTab.className = "flex-1 py-2 text-sm font-bold rounded-lg text-slate-400 hover:text-white transition-all";
        }
        this.updateMessage(isFocus);
    },

    updateMessage(isFocus) {
        const msgs = isFocus ? KODARI_MESSAGES.focus : KODARI_MESSAGES.break;
        const randomMsg = msgs[Math.floor(Math.random() * msgs.length)];
        this.elements.kodariMsg.textContent = `"${randomMsg}"`;
    },

    updateSessionCount(count) {
        this.elements.sessionCountDisplay.textContent = `Today: ${count} sessions`;
    },

    renderChart(weeklyData) {
        const days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'];
        const todayIndex = (new Date().getDay() + 6) % 7;
        const maxSessions = Math.max(...weeklyData, 4);

        this.elements.weeklyChart.innerHTML = '';

        weeklyData.forEach((count, index) => {
            const heightPercentage = (count / maxSessions) * 100;
            const isToday = index === todayIndex;

            const dayCol = document.createElement('div');
            dayCol.className = 'flex-1 flex flex-col items-center gap-2 h-full';
            dayCol.innerHTML = `
                <div class="w-full flex-1 bg-slate-700/30 rounded-t-lg relative group flex items-end">
                    <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 bg-pink-500 text-[10px] text-white px-1.5 py-0.5 rounded opacity-0 group-hover:opacity-100 transition-opacity z-10 whitespace-nowrap">
                        ${count}
                    </div>
                    <div class="w-full rounded-t-lg transition-all duration-1000 ${isToday ? 'bg-pink-500 shadow-[0_0_15px_rgba(236,72,153,0.5)]' : 'bg-pink-500/30'}" 
                         style="height: ${heightPercentage}%"></div>
                </div>
                <span class="text-[10px] font-bold ${isToday ? 'text-pink-400' : 'text-slate-500'}">${days[index]}</span>
            `;
            this.elements.weeklyChart.appendChild(dayCol);
        });
    }
};
