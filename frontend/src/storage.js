// Storage Module for managing local data
export const Storage = {
    KEY: 'kodari-weekly-sessions',

    getWeeklyData() {
        return JSON.parse(localStorage.getItem(this.KEY)) || [0, 0, 0, 0, 0, 0, 0];
    },

    saveWeeklyData(data) {
        localStorage.setItem(this.KEY, JSON.stringify(data));
    },

    incrementTodaySession() {
        const data = this.getWeeklyData();
        const todayIndex = (new Date().getDay() + 6) % 7; // Mon=0, Sun=6
        data[todayIndex]++;
        this.saveWeeklyData(data);
        return data;
    },
    
    getTodaySessions() {
        const data = this.getWeeklyData();
        const todayIndex = (new Date().getDay() + 6) % 7;
        return data[todayIndex];
    }
};
