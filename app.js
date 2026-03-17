document.addEventListener('DOMContentLoaded', () => {
    const generateBtn    = document.getElementById('generate-btn');
    const topicInput     = document.getElementById('topic-input');
    const btnText        = generateBtn.querySelector('.btn-text');
    const spinner        = generateBtn.querySelector('.spinner');
    const resultSection  = document.getElementById('result-section');
    const outTitle       = document.getElementById('out-title');
    const outScript      = document.getElementById('out-script');
    const outHashtags    = document.getElementById('out-hashtags');
    const statusLog      = document.getElementById('status-log');
    const videoContainer = document.getElementById('video-container');
    const downloadBtn    = document.getElementById('download-btn');

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

    // ─── Polling state ────────────────────────────────────────────────────────
    let _pollTimer = null;

    function stopPolling() {
        if (_pollTimer) {
            clearInterval(_pollTimer);
            _pollTimer = null;
        }
    }

    async function pollStatus() {
        try {
            const res = await fetch('/api/status');
            if (!res.ok) return;
            const data = await res.json();

            // Show new messages
            if (data.messages && data.messages.length > 0) {
                for (const msg of data.messages) {
                    statusLog.textContent = msg;
                    console.log('[server]', msg);

                    // When research is done, populate the script preview placeholders
                    if (msg.includes('기획안') || msg.includes('STEP 1')) {
                        [outTitle, outScript, outHashtags].forEach(el => el.classList.remove('placeholder-anim'));
                        if (!outTitle.textContent)   outTitle.textContent   = `[자동 생성 중] ${topicInput.value}`;
                        if (!outScript.textContent)  outScript.textContent  = '나레이션 합성 중… 잠시만 기다려 주세요.';
                        if (!outHashtags.textContent) outHashtags.textContent = `#${topicInput.value.replace(/\s+/g, '')} #AI자동화 #숏폼팩토리`;
                    }
                }
            }

            // Check completion
            if (!data.running && data.done) {
                stopPolling();
                onPipelineComplete();
            }

            if (!data.running && !data.done) {
                // backend hasn't started yet – keep polling
            }

        } catch (e) {
            console.error('polling error', e);
        }
    }

    function startPolling() {
        stopPolling();
        _pollTimer = setInterval(pollStatus, 1500); // poll every 1.5 s
    }

    // ─── On pipeline complete ─────────────────────────────────────────────────
    function onPipelineComplete() {
        statusLog.textContent = '✅ 영상 합성 완료! 결과를 확인하세요.';
        generateBtn.disabled  = false;
        btnText.textContent   = '다시 생성하기';
        spinner.classList.add('hidden');

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

    // ─── Generate button ──────────────────────────────────────────────────────
    generateBtn.addEventListener('click', async () => {
        const topic = topicInput.value.trim();
        const formatSelect      = document.getElementById('format-select');
        const orientationSelect = document.getElementById('orientation-select');
        const format      = formatSelect      ? formatSelect.value      : 'short';
        const orientation = orientationSelect ? orientationSelect.value : 'portrait';

        if (!topic) {
            alert('어떤 주제로 콘텐츠를 만들고 싶으신지 입력해주세요!');
            topicInput.focus();
            return;
        }

        // UI – loading state
        generateBtn.disabled = true;
        btnText.textContent  = '생성 중...';
        spinner.classList.remove('hidden');

        resultSection.classList.remove('hidden');
        resultSection.scrollIntoView({ behavior: 'smooth' });

        [outTitle, outScript, outHashtags].forEach(el => {
            el.textContent = '';
            el.classList.add('placeholder-anim');
        });
        videoContainer.innerHTML = '<p id="video-placeholder" class="placeholder-anim" style="min-height:400px;display:flex;align-items:center;justify-content:center;border-radius:12px;background:rgba(0,0,0,0.3);">영상을 렌더링 중입니다...</p>';
        if (downloadBtn) downloadBtn.classList.add('hidden');
        statusLog.textContent = '🚀 엔진 시동 중...';

        try {
            const res = await fetch('/api/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ topic, format, orientation })
            });

            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                throw new Error(err.error || `HTTP ${res.status}`);
            }

            // Start polling for status updates
            startPolling();

        } catch (error) {
            stopPolling();
            alert(`생성 중 오류가 발생했습니다: ${error.message}`);
            console.error(error);
            statusLog.textContent = '❌ 생성 중 오류 발생';
            generateBtn.disabled = false;
            btnText.textContent  = '마법 시작하기';
            spinner.classList.add('hidden');
        }
    });

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
