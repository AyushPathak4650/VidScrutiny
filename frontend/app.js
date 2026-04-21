document.addEventListener('DOMContentLoaded', () => {
    const videoUrlInput = document.getElementById('video-url');
    const analyzeBtn = document.getElementById('analyze-btn');
    const video = document.getElementById('main-video');
    const playPauseBtn = document.getElementById('play-pause-btn');
    const bigPlayBtn = document.getElementById('big-play-btn');
    const initialPlayOverlay = document.getElementById('initial-play-overlay');
    const playIcon = document.getElementById('play-icon');
    const pauseIcon = document.getElementById('pause-icon');
    const timeline = document.getElementById('timeline');
    const progressBar = document.getElementById('progress-bar');
    const timeDisplay = document.getElementById('time-display');
    const markersContainer = document.getElementById('markers-container');
    
    // Status Elements
    const statusContainer = document.getElementById('status-container');
    const statusText = document.getElementById('status-text');

    // Overlay Elements
    const factCardOverlay = document.getElementById('fact-card-overlay');
    const factCard = document.getElementById('fact-card');
    const dismissCardBtn = document.getElementById('dismiss-card-btn');
    const ratingBadge = document.getElementById('rating-badge');
    const timestampDisplay = document.getElementById('timestamp-display');
    const claimText = document.getElementById('claim-text');
    const explanationText = document.getElementById('explanation-text');
    const sourceLink = document.getElementById('source-link');
    const cardGlow = document.getElementById('card-glow');

    const sideLog = document.getElementById('side-log');
    const sideLogEmpty = document.getElementById('side-log-empty');
    const claimCount = document.getElementById('claim-count');

    let factData = [];
    let activeFactIndex = -1;

    analyzeBtn.addEventListener('click', async () => {
        const url = videoUrlInput.value;
        if (!url) return;

        // Reset UI State
        factData = [];
        markersContainer.innerHTML = '';
        sideLog.innerHTML = '';
        sideLog.appendChild(sideLogEmpty);
        sideLogEmpty.classList.remove('hidden');
        claimCount.textContent = '0 Claims';
        activeFactIndex = -1;
        hideFactCard();
        video.src = ""; // Clear current video
        initialPlayOverlay.classList.add('hidden');
        
        statusContainer.classList.remove('hidden');
        statusText.textContent = "Connecting to AI Pipeline...";
        analyzeBtn.disabled = true;
        analyzeBtn.classList.add('opacity-70', 'cursor-not-allowed');
        videoUrlInput.parentElement.classList.add('scanner-active');

        // Setup WebSocket connection
        // Connect directly to the live Render backend
        const wsUrl = `wss://vidscrutiny.onrender.com/api/ws/analyze`;
        const ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            // Send URL payload to start process
            ws.send(JSON.stringify({ url: url }));
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            // Handle error from backend
            if (data.error) {
                alert(`Analysis Failed:\n${data.error}`);
                resetAnalysisUI();
                ws.close();
                return;
            }

            // Real-time status update
            if (data.status && data.type !== 'result') {
                statusText.textContent = data.status;
            }

            // Final Payload received
            if (data.type === 'result' && data.status === 'success') {
                statusText.textContent = "Analysis complete! Loading video...";
                
                factData = data.fact_checks;
                factData.sort((a, b) => a.timestamp - b.timestamp);
                
                if (data.stream_url) {
                    video.src = data.stream_url;
                    video.load();
                    video.addEventListener('loadeddata', () => {
                        initialPlayOverlay.classList.remove('hidden');
                    }, { once: true });
                }

                if (video.readyState >= 1) {
                    renderMarkers();
                    renderSideLog();
                } else {
                    video.addEventListener('loadedmetadata', () => {
                        renderMarkers();
                        renderSideLog();
                    }, { once: true });
                }
                
                resetAnalysisUI();
            }
        };

        ws.onerror = (error) => {
            console.error("WebSocket Error:", error);
            alert("Connection to AI Pipeline lost.");
            resetAnalysisUI();
        };

        ws.onclose = () => {
            // Ensure UI resets if connection drops unexpectedly
            if (analyzeBtn.disabled) {
                resetAnalysisUI();
            }
        };

        function resetAnalysisUI() {
            statusContainer.classList.add('hidden');
            analyzeBtn.disabled = false;
            analyzeBtn.classList.remove('opacity-70', 'cursor-not-allowed');
            videoUrlInput.parentElement.classList.remove('scanner-active');
        }
    });

    function renderMarkers() {
        markersContainer.innerHTML = '';
        const duration = video.duration;
        if (!duration || isNaN(duration)) return;

        factData.forEach((fact, index) => {
            const percentage = (fact.timestamp / duration) * 100;
            const marker = document.createElement('div');
            marker.classList.add('marker');
            
            // Stagger the animation so they drop in one by one left to right
            marker.style.animationDelay = `${index * 0.15}s`;
            
            // Apply PRD strict 10% high-contrast colors
            if (fact.rating === 'True') marker.classList.add('marker-true');
            else if (fact.rating === 'False') marker.classList.add('marker-false');
            else marker.classList.add('marker-context');

            marker.style.left = `${percentage}%`;
            marker.title = `${fact.rating}: ${fact.claim}`;
            
            // Fitts's Law: Allow clicking marker to jump to that time
            marker.addEventListener('click', (e) => {
                e.stopPropagation();
                video.currentTime = fact.timestamp;
                showFactCard(index);
                video.pause();
            });

            markersContainer.appendChild(marker);
        });
    }

    function renderSideLog() {
        sideLogEmpty.classList.add('hidden');
        claimCount.textContent = `${factData.length} Claims`;

        factData.forEach((fact, index) => {
            const card = document.createElement('div');
            let borderColor, badgeColor;
            
            if (fact.rating === 'True') { borderColor = 'border-emerald-500/50'; badgeColor = 'bg-emerald-500/20 text-emerald-400'; }
            else if (fact.rating === 'False') { borderColor = 'border-rose-500/50'; badgeColor = 'bg-rose-500/20 text-rose-400'; }
            else { borderColor = 'border-amber-500/50'; badgeColor = 'bg-amber-500/20 text-amber-400'; }

            card.className = `p-3 rounded-lg border ${borderColor} bg-white/5 hover:bg-white/10 cursor-pointer transition-colors duration-200 group`;
            
            card.innerHTML = `
                <div class="flex items-center justify-between mb-2">
                    <span class="text-xs font-mono text-gray-400 bg-black/40 px-2 py-0.5 rounded">${formatTime(fact.timestamp)}</span>
                    <span class="text-[10px] font-bold tracking-widest uppercase px-2 py-0.5 rounded ${badgeColor}">${fact.rating}</span>
                </div>
                <p class="text-sm text-gray-300 line-clamp-2 italic mb-1">"${fact.claim}"</p>
            `;

            card.addEventListener('click', () => {
                video.currentTime = fact.timestamp;
                showFactCard(index);
                video.pause();
                
                // Highlight active card in sidebar
                document.querySelectorAll('#side-log > div').forEach(c => c.classList.remove('ring-2', 'ring-blue-500'));
                card.classList.add('ring-2', 'ring-blue-500');
            });

            sideLog.appendChild(card);
        });
    }

    // Video Controls Logic
    function togglePlay() {
        if (!video.src) return;
        if (video.paused) {
            video.play();
            initialPlayOverlay.classList.add('hidden');
        } else {
            video.pause();
        }
    }

    playPauseBtn.addEventListener('click', togglePlay);
    bigPlayBtn.addEventListener('click', togglePlay);
    video.addEventListener('click', togglePlay);

    // Keyboard Accessibility (WCAG standard)
    document.addEventListener('keydown', (e) => {
        if (e.code === 'Space' && document.activeElement !== videoUrlInput) {
            e.preventDefault();
            togglePlay();
        }
    });

    video.addEventListener('play', () => {
        playIcon.classList.add('hidden');
        pauseIcon.classList.remove('hidden');
    });

    video.addEventListener('pause', () => {
        pauseIcon.classList.add('hidden');
        playIcon.classList.remove('hidden');
    });

    function formatTime(seconds) {
        if (isNaN(seconds)) return "0:00";
        const m = Math.floor(seconds / 60);
        const s = Math.floor(seconds % 60);
        return `${m}:${s.toString().padStart(2, '0')}`;
    }

    video.addEventListener('timeupdate', () => {
        if (!video.duration) return;
        const percent = (video.currentTime / video.duration) * 100;
        progressBar.style.width = `${percent}%`;
        timeDisplay.textContent = `${formatTime(video.currentTime)} / ${formatTime(video.duration)}`;

        checkFactTriggers();
    });

    timeline.addEventListener('click', (e) => {
        if (!video.duration) return;
        const rect = timeline.getBoundingClientRect();
        const pos = (e.clientX - rect.left) / rect.width;
        video.currentTime = pos * video.duration;
    });

    // Fact Check Overlay Logic
    function checkFactTriggers() {
        if (factData.length === 0) return;

        const currentTime = video.currentTime;
        const triggerWindow = 0.4; // tighter window for precise stopping

        let foundIndex = -1;
        for (let i = 0; i < factData.length; i++) {
            if (Math.abs(currentTime - factData[i].timestamp) < triggerWindow) {
                foundIndex = i;
                break;
            }
        }

        if (foundIndex !== -1 && activeFactIndex !== foundIndex) {
            // Trigger! The "Wow" Factor
            activeFactIndex = foundIndex;
            showFactCard(foundIndex);
            
            // Dramatic pause
            video.pause();
        } else if (foundIndex === -1 && activeFactIndex !== -1) {
            // Auto dismiss if user scrubs away while playing
            if (!video.paused) {
                hideFactCard();
                activeFactIndex = -1;
            }
        }
    }

    function showFactCard(index) {
        const fact = factData[index];
        
        timestampDisplay.textContent = formatTime(fact.timestamp);
        claimText.textContent = `"${fact.claim}"`;
        explanationText.textContent = fact.explanation;
        sourceLink.href = fact.source_url;

        // Reset Styles
        ratingBadge.className = 'px-3 py-1 rounded-md text-[11px] font-bold tracking-widest uppercase text-white shadow-sm';
        progressBar.classList.remove('progress-alert-false');
        factCard.className = 'bg-[#1e232d]/95 backdrop-blur-xl border-l-4 p-6 rounded-r-xl rounded-bl-sm shadow-[0_20px_50px_rgba(0,0,0,0.5)] max-w-md w-full relative overflow-hidden transition-all duration-300';
        cardGlow.className = 'absolute -top-10 -right-10 w-32 h-32 rounded-full blur-3xl opacity-20';

        // Reset animations by forcing a reflow
        factCardOverlay.classList.remove('card-visible');
        void factCardOverlay.offsetWidth; // Trigger DOM reflow to restart CSS animation

        // Apply PRD Color Psychology
        if (fact.rating === 'False') {
            ratingBadge.classList.add('bg-rose-500');
            ratingBadge.textContent = 'FALSE';
            factCard.classList.add('border-rose-500');
            cardGlow.classList.add('bg-rose-500');
            progressBar.classList.add('progress-alert-false'); // Wow factor intense glow
        } else if (fact.rating === 'True') {
            ratingBadge.classList.add('bg-emerald-500');
            ratingBadge.textContent = 'TRUE';
            factCard.classList.add('border-emerald-500');
            cardGlow.classList.add('bg-emerald-500');
        } else {
            ratingBadge.classList.add('bg-amber-500');
            ratingBadge.textContent = 'CONTEXT';
            factCard.classList.add('border-amber-500');
            cardGlow.classList.add('bg-amber-500');
        }

        factCardOverlay.classList.add('card-visible');
    }

    function hideFactCard() {
        factCardOverlay.classList.remove('card-visible');
        progressBar.classList.remove('progress-alert-false');
    }

    dismissCardBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        hideFactCard();
        // Don't reset activeFactIndex here so it doesn't immediately re-trigger if paused
    });

    // Hide card if clicking outside the card content
    factCardOverlay.addEventListener('click', (e) => {
        if (e.target === factCardOverlay) {
            hideFactCard();
        }
    });
});