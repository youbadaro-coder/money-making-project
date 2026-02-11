// Main Entry Point
import { UI } from './ui.js';
import { Storage } from './storage.js';

// Application State
const state = {
    timeLeft: 25 * 60,
    timerId: null,
    isFocusSession: true,
    totalSessions: 0
};

// Application Logic
const App = {
    init() {
        UI.init();

        // Load initial data
        const weeklyData = Storage.getWeeklyData();
        state.totalSessions = Storage.getTodaySessions();

        // Initial Render
        this.updateTimerDisplay();
        UI.updateProgress(1);
        UI.updateMode(state.isFocusSession);
        UI.renderChart(weeklyData);
        UI.updateSessionCount(state.totalSessions);

        // Event Listeners
        this.bindEvents();
    },

    bindEvents() {
        UI.elements.startBtn.addEventListener('click', () => this.startTimer());
        UI.elements.pauseBtn.addEventListener('click', () => this.pauseTimer());
        UI.elements.resetBtn.addEventListener('click', () => this.resetTimer());

        UI.elements.focusTab.addEventListener('click', () => {
            if (!state.timerId) this.switchMode(true);
        });

        UI.elements.breakTab.addEventListener('click', () => {
            if (!state.timerId) this.switchMode(false);
        });
    },

    updateTimerDisplay() {
        const minutes = Math.floor(state.timeLeft / 60);
        const seconds = state.timeLeft % 60;
        UI.updateTimer(minutes, seconds);
    },

    startTimer() {
        if (state.timerId) return;

        UI.toggleButtons(true);

        state.timerId = setInterval(() => {
            state.timeLeft--;
            this.updateTimerDisplay();

            const total = state.isFocusSession ? 25 * 60 : 5 * 60;
            UI.updateProgress(state.timeLeft / total);

            if (state.timeLeft <= 0) {
                this.completeSession();
            }
        }, 1000);
    },

    pauseTimer() {
        clearInterval(state.timerId);
        state.timerId = null;
        UI.toggleButtons(false);
    },

    resetTimer() {
        this.pauseTimer();
        this.switchMode(true); // Reset to Focus mode by default
    },

    switchMode(isFocus) {
        state.isFocusSession = isFocus;
        state.timeLeft = isFocus ? 25 * 60 : 5 * 60;

        this.updateTimerDisplay();
        UI.updateProgress(1);
        UI.updateMode(isFocus);
    },

    completeSession() {
        this.pauseTimer();

        if (state.isFocusSession) {
            // Focus Session Completed
            const updatedData = Storage.incrementTodaySession();
            state.totalSessions = Storage.getTodaySessions();

            UI.renderChart(updatedData);
            UI.updateSessionCount(state.totalSessions);

            alert("오늘의 집중 세션 완료! 역시 우리 대표님 대단하십니다! 🚀");
            this.switchMode(false); // Switch to Break
        } else {
            // Break Session Completed
            alert("충분히 쉬셨나요? 다시 달릴 시간입니다! 충성! 🫡");
            this.switchMode(true); // Switch to Focus
        }
    }
};

// Start App
document.addEventListener('DOMContentLoaded', () => {
    App.init();
});
