document.addEventListener('DOMContentLoaded', () => {
    const generateBtn    = document.getElementById('generate-btn');
    const topicInput     = document.getElementById('topic-input');
    const btnText        = generateBtn.querySelector('.btn-text');
    const spinner        = generateBtn.querySelector('.spinner');

    // Bulk elements
    const modeSelect      = document.getElementById('mode-select');
    const singleWrapper   = document.getElementById('single-wrapper');
    const bulkWrapper     = document.getElementById('bulk-wrapper');
    const bulkTopicInput  = document.getElementById('bulk-topic-input');
    const generateBulkBtn = document.getElementById('generate-bulk-btn');
    const bulkBtnText     = generateBulkBtn ? generateBulkBtn.querySelector('.btn-text-bulk') : null;
    const bulkSpinner     = document.getElementById('bulk-spinner');

    const resultSection  = document.getElementById('result-section');
    const outTitle       = document.getElementById('out-title');
    const outScript      = document.getElementById('out-script');
    const outHashtags    = document.getElementById('out-hashtags');
    const statusLog      = document.getElementById('status-log');
    const videoContainer = document.getElementById('video-container');
    const downloadBtn    = document.getElementById('download-btn');

    if (modeSelect) {
        modeSelect.addEventListener('change', () => {
            if (modeSelect.value === 'bulk') {
                singleWrapper.classList.add('hidden');
                bulkWrapper.classList.remove('hidden');
                bulkWrapper.style.display = 'flex';
            } else {
                bulkWrapper.classList.add('hidden');
                singleWrapper.classList.remove('hidden');
            }
        });
    }

    // Tabs
    const tabs     = document.querySelectorAll('.tab');
    const tabPanes = document.querySelectorAll('.tab-pane');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tabPanes.forEach(pane => pane.classList.add('hidden'));
            tab.classList.add('active');
            const targetPane = document.getElementById(`tab-${tab.dataset.tab}`);
            if (targetPane) {
                targetPane.classList.remove('hidden');
                targetPane.classList.add('active');
            }
        });
    });

    // ─── Polling state (v3.1 Stable Timer) ────────────────────────────────────
    let _pollTimer = null;
    let _secondsElapsed = 0;
    let _timerInterval = null;
    let _emaTotalTime = 0; // Exponential Moving Average for Total Estimated Time
    const EMA_ALPHA = 0.2; // Smoothing factor (0 to 1). Lower is more stable.

    function updateProgressBar(percentage) {
        const bar = document.getElementById('progress-bar-fill');
        if (bar) bar.style.width = `${percentage}%`;
    }

    function formatTime(sec) {
        if (sec < 0 || isNaN(sec)) return "--:--";
        const m = Math.floor(sec / 60);
        const s = sec % 60;
        return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
    }

    function startTimer(format) {
        _secondsElapsed = 0;
        // Initial conservative guess: 10 mins for long, 3.5 mins for short
        _emaTotalTime = (format === 'long') ? 600 : 210; 
        
        const elapsedEl = document.getElementById('time-elapsed');
        const totalEl = document.getElementById('time-total');
        const remainingEl = document.getElementById('time-remaining');
        const progressContainer = document.getElementById('progress-container');
        
        progressContainer.classList.remove('hidden');
        if (elapsedEl) elapsedEl.textContent = `경과: 00:00`;
        if (totalEl) totalEl.textContent = `총 예상 소요: ${formatTime(_emaTotalTime)}`;
        if (remainingEl) remainingEl.textContent = `남은 시간: ${formatTime(_emaTotalTime)}`;
        updateProgressBar(5);

        if (_timerInterval) clearInterval(_timerInterval);
        _timerInterval = setInterval(() => {
            _secondsElapsed++;
            if (elapsedEl) elapsedEl.textContent = `경과: ${formatTime(_secondsElapsed)}`;
            
            // Calc remaining based on stable EMA total
            let remaining = Math.round(_emaTotalTime - _secondsElapsed);
            if (remaining < 5 && _secondsElapsed < _emaTotalTime) remaining = 5; 
            if (remainingEl) remainingEl.textContent = `남은 시간: ${formatTime(remaining)}`;
        }, 1000);
    }

    function stopPolling() {
        if (_pollTimer) { clearInterval(_pollTimer); _pollTimer = null; }
        if (_timerInterval) { clearInterval(_timerInterval); _timerInterval = null; }
    }

    async function pollStatus() {
        try {
            const res = await fetch('/api/status');
            if (!res.ok) return;
            const data = await res.json();

            const totalEl = document.getElementById('time-total');
            const remainingEl = document.getElementById('time-remaining');

            // 1. Update Progress Bar
            if (data.progress !== undefined) {
                updateProgressBar(data.progress);
                
                // 2. Stable Time Estimation (EMA)
                if (data.progress > 8 && data.progress < 100) {
                    const rawTotal = (_secondsElapsed / data.progress) * 100;
                    _emaTotalTime = (EMA_ALPHA * rawTotal) + (1 - EMA_ALPHA) * _emaTotalTime;
                    if (totalEl) totalEl.textContent = `총 예상 소요: ${formatTime(Math.round(_emaTotalTime))}`;
                }
            }

            // 3. Show new messages & Handle Special Data
            if (data.messages && data.messages.length > 0) {
                for (const msg of data.messages) {
                    // Check for Script Data Preview
                    if (msg.startsWith('[SCRIPT_DATA]')) {
                        try {
                            const scriptData = JSON.parse(msg.replace('[SCRIPT_DATA]', '').trim());
                            [outTitle, outScript, outHashtags].forEach(el => el.classList.remove('placeholder-anim'));
                            outTitle.textContent = scriptData.title;
                            outScript.textContent = scriptData.script;
                            outHashtags.textContent = scriptData.hashtags;
                            continue; // Don't show JSON in logs
                        } catch(e) {}
                    }

                    // Check for Bulk File notification
                    if (msg.includes('📁 영상 저장됨:')) {
                        const filename = msg.split('📁 영상 저장됨:')[1].trim();
                        addBulkItem(filename);
                    }

                    statusLog.textContent = msg;
                    if (msg.includes('❌') || msg.includes('🚨')) {
                        statusLog.style.color = '#f87171'; // Red for errors
                    } else {
                        statusLog.style.color = '#a5b4fc'; // Normal
                    }
                    console.log('[server]', msg);
                }
            }

            // 4. Check for Hard Errors
            if (data.error) {
                stopPolling();
                statusLog.textContent = `🚨 오류 발생: ${data.error}`;
                statusLog.style.color = '#ef4444';
                const headerText = document.getElementById('result-header-text');
                if (headerText) {
                    headerText.textContent = '❌ 생성 중단됨';
                    headerText.classList.remove('pulsing-text');
                }
                generateBtn.disabled = false;
                if (generateBulkBtn) generateBulkBtn.disabled = false;
                spinner.classList.add('hidden');
                if (bulkSpinner) bulkSpinner.classList.add('hidden');
                return;
            }

            // 5. Check completion
            if (!data.running && data.done) {
                updateProgressBar(100);
                const headerText = document.getElementById('result-header-text');
                if (headerText) {
                    headerText.textContent = '생성 완료! 🎉';
                    headerText.classList.remove('pulsing-text');
                }
                if (totalEl) totalEl.textContent = `총 소요 시간: ${formatTime(_secondsElapsed)}`;
                if (remainingEl) remainingEl.textContent = `남은 시간: 00:00`;
                
                setTimeout(() => {
                    stopPolling();
                    onPipelineComplete();
                }, 1000);
            }

        } catch (e) {
            console.error('polling error', e);
        }
    }

    function addBulkItem(filename) {
        const gallery = document.getElementById('bulk-result-gallery');
        const bulkList = document.getElementById('bulk-list');
        if (!gallery || !bulkList) return;

        gallery.classList.remove('hidden');
        
        const item = document.createElement('div');
        item.className = 'bulk-item';
        
        // Extract topic name from filename: final_video_1_topic.mp4
        const parts = filename.split('_');
        const topicDisplay = parts.slice(3).join('_').replace('.mp4', '') || filename;
        
        item.innerHTML = `
            <span class="topic-name">${topicDisplay}</span>
            <a href="/video/${filename}" class="bulk-download-link" download="${filename}">다운로드</a>
        `;
        bulkList.appendChild(item);
    }

    function startPolling(format) {
        stopPolling();
        startTimer(format);
        _pollTimer = setInterval(pollStatus, 1500); // poll every 1.5 s
    }

    // ─── On pipeline complete ─────────────────────────────────────────────────
    function onPipelineComplete() {
        statusLog.textContent = '✅ 완료! 모든 작업이 끝났습니다.';
        generateBtn.disabled  = false;
        btnText.textContent   = '다시 생성하기';
        spinner.classList.add('hidden');
        if (generateBulkBtn) {
            generateBulkBtn.disabled = false;
            bulkBtnText.textContent = '대량 생산 공장 가동 🚀';
            bulkSpinner.classList.add('hidden');
        }

        // Switch to video tab
        tabs.forEach(t => t.classList.remove('active'));
        tabPanes.forEach(pane => pane.classList.add('hidden'));
        const videoTab = document.querySelector('.tab[data-tab="video"]');
        if (videoTab) videoTab.classList.add('active');
        document.getElementById('tab-video').classList.remove('hidden');

        // Load video
        const videoUrl = `/video?t=${Date.now()}`;
        videoContainer.innerHTML = `
            <video width="100%" height="auto" style="max-height:500px;border-radius:12px;box-shadow:0 4px 20px rgba(0,0,0,0.5);" controls autoplay>
                <source src="${videoUrl}" type="video/mp4">
                브라우저가 비디오를 지원하지 않습니다.
            </video>`;
        if (downloadBtn) {
            downloadBtn.href = videoUrl;
            downloadBtn.classList.remove('hidden');
        }
    }

    // ─── Generate action (v4.4 Optimized) ─────────────────────────────────────
    async function startGeneration(topics, isBulk, btn, btnTextEl, spinnerEl) {
        const formatSelect      = document.getElementById('format-select');
        const orientationSelect = document.getElementById('orientation-select');
        const referenceInput    = document.getElementById('reference-input');
        
        const format      = formatSelect      ? formatSelect.value      : 'short';
        const orientation = orientationSelect ? orientationSelect.value : 'portrait';
        const references  = referenceInput    ? referenceInput.value.trim() : '';

        if (!topics || topics.length === 0) {
            alert('주제를 입력해주세요!');
            return;
        }

        // 1. UI Loading State
        btn.disabled = true;
        btnTextEl.textContent  = '공장 가동 중...';
        spinnerEl.classList.remove('hidden');

        // 2. Clear Results & Gallery
        resultSection.classList.remove('hidden');
        resultSection.scrollIntoView({ behavior: 'smooth' });
        
        const headerText = document.getElementById('result-header-text');
        if (headerText) {
            headerText.textContent = '생성 중... ⚙️';
            headerText.classList.add('pulsing-text');
        }
        
        const gallery = document.getElementById('bulk-result-gallery');
        const bulkList = document.getElementById('bulk-list');
        if (gallery) gallery.classList.add('hidden');
        if (bulkList) bulkList.innerHTML = '';

        [outTitle, outScript, outHashtags].forEach(el => {
            el.textContent = '';
            el.classList.add('placeholder-anim');
        });
        videoContainer.innerHTML = '<p id="video-placeholder" class="placeholder-anim" style="min-height:400px;display:flex;align-items:center;justify-content:center;border-radius:12px;background:rgba(0,0,0,0.3);">영상을 렌더링 중입니다...</p>';
        if (downloadBtn) downloadBtn.classList.add('hidden');
        
        statusLog.textContent = isBulk ? `🚀 엔진 시동 중... [대량 생산 모드: 총 ${topics.length}개]` : `🚀 엔진 시동 중...`;

        // 3. Initiate API Call
        try {
            const res = await fetch('/api/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ topics, format, orientation, isBulk, references })
            });

            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                throw new Error(err.error || `HTTP ${res.status}`);
            }

            // Start polling for status updates
            startPolling(format);

        } catch (error) {
            stopPolling();
            alert(`생성 중 오류: ${error.message}`);
            if (headerText) {
                headerText.textContent = '❌ 생성 중 오류 발생';
                headerText.classList.remove('pulsing-text');
            }
            btn.disabled = false;
            btnTextEl.textContent  = isBulk ? '대량 생산 공장 가동 🚀' : '마법 시작하기';
            spinnerEl.classList.add('hidden');
        }
    }

    generateBtn.addEventListener('click', () => {
        const topic = topicInput.value.trim();
        if (!topic) {
            alert('단일 주제를 입력해주세요!');
            topicInput.focus();
            return;
        }
        startGeneration([topic], false, generateBtn, btnText, spinner);
    });

    if (generateBulkBtn) {
        generateBulkBtn.addEventListener('click', () => {
            const rawText = bulkTopicInput.value.trim();
            if (!rawText) {
                alert('여러 주제를 쉼표나 줄바꿈으로 입력해주세요!');
                bulkTopicInput.focus();
                return;
            }
            // Parse by newline or comma
            const topics = rawText.split(/[\n,]+/).map(t => t.trim()).filter(t => t.length > 0);
            startGeneration(topics, true, generateBulkBtn, bulkBtnText, bulkSpinner);
        });
    }

    // ─── Copy button ──────────────────────────────────────────────────────────
    const copyAllBtn = document.querySelector('.copy-all-btn');
    if (copyAllBtn) {
        copyAllBtn.addEventListener('click', () => {
            const scriptTab = document.getElementById('tab-script');
            const promptTab = document.getElementById('tab-prompts');
            let textToCopy  = '';
            if (scriptTab && !scriptTab.classList.contains('hidden')) {
                textToCopy = `제목:\n${outTitle.textContent}\n\n대본:\n${outScript.textContent}\n\n해시태그:\n${outHashtags.textContent}`;
            }
            navigator.clipboard.writeText(textToCopy).then(() => {
                const orig = copyAllBtn.innerHTML;
                copyAllBtn.innerHTML = '<span style="font-size:12px;font-weight:bold;">Copied!</span>';
                setTimeout(() => { copyAllBtn.innerHTML = orig; }, 2000);
            });
        });
    }
});
