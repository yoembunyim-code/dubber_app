<!DOCTYPE html>
<html lang="km">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>អ្នកបកប្រែវីដេអូខ្មែរ - សំឡេងដូចមនុស្ស</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        body {
            font-family: 'Khmer OS', 'Noto Sans Khmer', sans-serif;
            background: linear-gradient(145deg, #f5f3f0 0%, #e8e4de 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            width: 100%;
            background: rgba(255, 255, 255, 0.85);
            backdrop-filter: blur(12px);
            border-radius: 40px;
            padding: 30px 28px;
            box-shadow: 0 25px 50px -12px rgba(0,0,0,0.3);
            border: 1px solid rgba(255,255,255,0.5);
            transition: 0.3s;
        }
        h1 {
            font-size: 2.2rem;
            font-weight: 700;
            color: #2d2a24;
            text-align: center;
            margin-bottom: 8px;
            letter-spacing: 1px;
        }
        .sub {
            text-align: center;
            color: #6b6258;
            font-size: 0.95rem;
            margin-bottom: 25px;
            border-bottom: 2px dashed #d6cec4;
            padding-bottom: 15px;
        }
        .video-section {
            background: #1e1b17;
            border-radius: 28px;
            overflow: hidden;
            margin-bottom: 25px;
            position: relative;
            box-shadow: inset 0 4px 8px rgba(0,0,0,0.6);
        }
        #videoPlayer {
            width: 100%;
            display: block;
            background: #000;
            aspect-ratio: 16 / 9;
            object-fit: contain;
        }
        .video-controls {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin: 15px 0 20px;
        }
        .video-controls input[type="file"] {
            flex: 1;
            min-width: 150px;
            padding: 10px 14px;
            background: #ffffffcc;
            border-radius: 60px;
            border: 1px solid #ccc;
            font-size: 0.9rem;
            cursor: pointer;
        }
        .video-controls input[type="text"] {
            flex: 2;
            min-width: 200px;
            padding: 10px 18px;
            border-radius: 60px;
            border: 1px solid #ccc;
            background: white;
            font-size: 0.95rem;
            outline: none;
            transition: 0.2s;
        }
        .video-controls input[type="text"]:focus {
            border-color: #b48b6e;
            box-shadow: 0 0 0 3px #b48b6e55;
        }
        .video-controls button {
            padding: 10px 24px;
            background: #2d2a24;
            color: white;
            border: none;
            border-radius: 60px;
            font-weight: 600;
            font-size: 0.95rem;
            cursor: pointer;
            transition: 0.2s;
            white-space: nowrap;
        }
        .video-controls button:hover {
            background: #4a3f36;
            transform: scale(1.02);
        }
        .translate-area {
            display: flex;
            flex-direction: column;
            gap: 14px;
            margin: 20px 0 18px;
        }
        .translate-area textarea {
            width: 100%;
            min-height: 100px;
            padding: 16px 18px;
            border-radius: 24px;
            border: 1px solid #ddd;
            font-size: 1rem;
            font-family: inherit;
            background: #fefcf9;
            resize: vertical;
            transition: 0.2s;
            line-height: 1.7;
        }
        .translate-area textarea:focus {
            border-color: #b48b6e;
            box-shadow: 0 0 0 4px #b48b6e33;
            outline: none;
        }
        .action-row {
            display: flex;
            flex-wrap: wrap;
            gap: 14px;
            justify-content: space-between;
            align-items: center;
        }
        .btn-group {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        .btn {
            padding: 12px 28px;
            border: none;
            border-radius: 60px;
            font-weight: 600;
            font-size: 1rem;
            cursor: pointer;
            transition: 0.2s;
            background: #e4ddd4;
            color: #2d2a24;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        }
        .btn-primary {
            background: #b48b6e;
            color: white;
            box-shadow: 0 6px 14px #b48b6e55;
        }
        .btn-primary:hover {
            background: #9d7a60;
            transform: translateY(-2px);
        }
        .btn-danger {
            background: #c73b3b;
            color: white;
        }
        .btn-danger:hover {
            background: #a52e2e;
        }
        .btn-success {
            background: #3a7d5c;
            color: white;
        }
        .btn-success:hover {
            background: #2d6247;
        }
        .settings {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            background: #f3efe9;
            padding: 18px 22px;
            border-radius: 40px;
            margin: 18px 0 8px;
            align-items: center;
        }
        .settings label {
            display: flex;
            align-items: center;
            gap: 8px;
            font-weight: 500;
            color: #3d352c;
        }
        .settings select, .settings input[type="range"] {
            padding: 6px 12px;
            border-radius: 40px;
            border: 1px solid #ccc;
            background: white;
            font-size: 0.9rem;
        }
        .settings input[type="range"] {
            width: 110px;
            accent-color: #b48b6e;
        }
        .status {
            margin-top: 14px;
            padding: 14px 18px;
            border-radius: 30px;
            background: #ede8e1;
            color: #2d2a24;
            font-size: 0.95rem;
            min-height: 50px;
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
            border-left: 5px solid #b48b6e;
        }
        .status .spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #ccc;
            border-top: 3px solid #b48b6e;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }
        @keyframes spin { 100% { transform: rotate(360deg); } }
        .footer {
            text-align: center;
            font-size: 0.8rem;
            color: #8a7e72;
            margin-top: 20px;
        }
        @media (max-width: 600px) {
            .container { padding: 18px; }
            h1 { font-size: 1.6rem; }
            .settings { flex-direction: column; align-items: stretch; }
        }
    </style>
</head>
<body>
<div class="container">
    <h1>🎬 អ្នកបកប្រែវីដេអូខ្មែរ</h1>
    <div class="sub">បញ្ចូលអត្ថបទ ជ្រើសសំឡេង ហើយស្តាប់ដូចមនុស្សនិយាយ</div>

    <!-- Video Player -->
    <div class="video-section">
        <video id="videoPlayer" controls playsinline>
            <source src="" type="video/mp4">
            Your browser does not support video.
        </video>
    </div>

    <!-- Video Controls -->
    <div class="video-controls">
        <input type="file" id="videoUpload" accept="video/*">
        <input type="text" id="videoUrl" placeholder="បិទភ្ជាប់ URL វីដេអូ (MP4)">
        <button id="loadVideoBtn">📥 ដាក់វីដេអូ</button>
    </div>

    <!-- Translate Area -->
    <div class="translate-area">
        <textarea id="textInput" placeholder="សរសេរអត្ថបទខ្មែរនៅទីនេះ ឬចម្លងពីកន្លែងណា...">សួស្តី! ថ្ងៃនេះយើងនឹងរៀនពីរបៀបបកប្រែវីដេអូជាភាសាខ្មែរ។ សូមស្តាប់សំឡេងនេះដោយយកចិត្តទុកដាក់។</textarea>
    </div>

    <!-- Action Buttons -->
    <div class="action-row">
        <div class="btn-group">
            <button class="btn btn-primary" id="speakBtn">🔊 អានអត្ថបទ</button>
            <button class="btn btn-danger" id="stopBtn">⏹ បញ្ឈប់</button>
            <button class="btn btn-success" id="clearBtn">🗑 សម្អាត</button>
        </div>
    </div>

    <!-- Settings -->
    <div class="settings">
        <label>🗣 សំឡេង:
            <select id="voiceSelect"></select>
        </label>
        <label>🐢 ល្បឿន:
            <input type="range" id="rateSlider" min="0.5" max="2" step="0.1" value="1.0">
            <span id="rateValue">1.0</span>
        </label>
        <label>🔊 កម្រិត:
            <input type="range" id="volumeSlider" min="0" max="1" step="0.05" value="1.0">
            <span id="volumeValue">100%</span>
        </label>
    </div>

    <!-- Status -->
    <div class="status" id="statusBar">
        <span>⏳ ត្រៀមខ្លួនជាស្រេច</span>
    </div>
    <div class="footer">បង្កើតដោយស្មារតីស្រឡាញ់ភាសាខ្មែរ 🇰🇭</div>
</div>

<script>
    (function() {
        // ---------- DOM refs ----------
        const video = document.getElementById('videoPlayer');
        const videoUpload = document.getElementById('videoUpload');
        const videoUrl = document.getElementById('videoUrl');
        const loadVideoBtn = document.getElementById('loadVideoBtn');
        const textInput = document.getElementById('textInput');
        const speakBtn = document.getElementById('speakBtn');
        const stopBtn = document.getElementById('stopBtn');
        const clearBtn = document.getElementById('clearBtn');
        const voiceSelect = document.getElementById('voiceSelect');
        const rateSlider = document.getElementById('rateSlider');
        const rateValue = document.getElementById('rateValue');
        const volumeSlider = document.getElementById('volumeSlider');
        const volumeValue = document.getElementById('volumeValue');
        const statusBar = document.getElementById('statusBar');

        // ---------- Speech Synthesis ----------
        let synth = window.speechSynthesis;
        let currentUtterance = null;
        let isSpeaking = false;
        let queue = [];
        let isPaused = false;

        // Populate voices (will refresh when voices changed)
        function populateVoiceList() {
            const voices = synth.getVoices();
            voiceSelect.innerHTML = '';
            // Prefer Khmer voices if exist, else fallback to any
            let khmerVoices = voices.filter(v => v.lang.startsWith('km'));
            let list = khmerVoices.length > 0 ? khmerVoices : voices;
            if (list.length === 0) {
                let opt = document.createElement('option');
                opt.value = '';
                opt.textContent = 'គ្មានសំឡេងសម្រាប់ឧបករណ៍អ្នក';
                voiceSelect.appendChild(opt);
                return;
            }
            list.forEach(voice => {
                let opt = document.createElement('option');
                opt.value = voice.name;
                opt.textContent = voice.name + ' (' + voice.lang + ')';
                if (voice.lang.startsWith('km')) {
                    opt.selected = true;
                }
                voiceSelect.appendChild(opt);
            });
            // if no Khmer selected, select first
            if (!voiceSelect.value && list.length > 0) {
                voiceSelect.selectedIndex = 0;
            }
        }

        // Load voices when they change (async)
        if (synth) {
            synth.onvoiceschanged = populateVoiceList;
            // immediate call if already loaded
            setTimeout(populateVoiceList, 100);
        }

        // ---------- Utils ----------
        function setStatus(text, isLoading = false) {
            if (isLoading) {
                statusBar.innerHTML = <span class="spinner"></span> ${text};
            } else {
                statusBar.innerHTML = <span>${text}</span>;
            }
        }

        // Split text into sentences (keep punctuation)
        function splitIntoSentences(text) {
            // split by . ! ? and newline, but keep the punctuation
            let sentences = text.match(/[^.!?]+[.!?]+|[^.!?]+$/g);
            if (!sentences) return [text];
            return sentences.map(s => s.trim()).filter(s => s.length > 0);
        }

        // Speak with natural pauses
        function speakSentences(sentences, rate, volume, voiceName) {
            if (!synth) {
                setStatus('❌ កម្មវិធីរុករករបស់អ្នកមិនគាំទ្រ Speech Synthesis');
                return;
            }
            if (isSpeaking) {
                stopSpeaking();
            }
            if (sentences.length === 0) {
                setStatus('⚠️ គ្មានអត្ថបទដើម្បីអាន');
                return;
            }

            isSpeaking = true;
            queue = [...sentences];
            let index = 0;

            function speakNext() {
                if (!isSpeaking || index >= queue.length) {
                    isSpeaking = false;
                    setStatus('✅ អានចប់ហើយ!');
                    return;
                }

                let sentence = queue[index];
                if (sentence.trim().length === 0) {
                    index++;
                    speakNext();
                    return;
                }

                let utterance = new SpeechSynthesisUtterance(sentence);
                // Set language to Khmer if possible, but fallback to default
                utterance.lang = 'km-KH';
                // Find voice by name
                let voices = synth.getVoices();
                let selectedVoice = voices.find(v => v.name === voiceName);
                if (selectedVoice) {
                    utterance.voice = selectedVoice;
                } else {
                    // try to find any Khmer voice
                    let khmer = voices.find(v => v.lang.startsWith('km'));
                    if (khmer) utterance.voice = khmer;
                }
                utterance.rate = rate;
                utterance.volume = volume;
                utterance.pitch = 1.0;

                // Event: on end -> next sentence with pause
                utterance.onend = function() {
                    index++;
                    // natural pause between sentences (0.4 - 0.8 sec)
                    setTimeout(() => {
                        speakNext();
                    }, 450);
                };

                utterance.onerror = function(e) {
                    console.warn('Speech error:', e);
                    index++;
                    setTimeout(() => {
                        speakNext();
                    }, 300);
                };

                currentUtterance = utterance;
                setStatus🔊 កំពុងនិយាយ (${index+1}/${queue.length})...`, true);
                synth.speak(utterance);
            }

            speakNext();
        }

        function stopSpeaking() {
            if (synth) {
                synth.cancel();
            }
            isSpeaking = false;
            queue = [];
            currentUtterance = null;
            setStatus('⏹ បានបញ្ឈប់');
        }

        // ---------- Main Speak action ----------
        function handleSpeak() {
            let text = textInput.value.trim();
            if (!text) {
                setStatus('⚠️ សូមបញ្ចូលអត្ថបទជាមុនសិន');
                return;
            }

            // Check if any voice available
            let voices = synth.getVoices();
            if (voices.length === 0) {
                setStatus('⏳ កំពុងផ្ទុកសំឡេង... សូមរងចាំបន្តិច');
                setTimeout(() => {
                    handleSpeak(); // retry
                }, 300);
                return;
            }

            let rate = parseFloat(rateSlider.value);
            let volume = parseFloat(volumeSlider.value);
            let voiceName = voiceSelect.value;

            // Split text into sentences
            let sentences = splitIntoSentences(text);
            speakSentences(sentences, rate, volume, voiceName);
        }

        // ---------- Load Video ----------
        function loadVideo(src) {
            if (!src) return;
            video.src = src;
            video.load();
            video.play().catch(() => {});
            setStatus('📹 វីដេអូកំពុងចាក់');
        }

        // ---------- Event Listeners ----------
        speakBtn.addEventListener('click', handleSpeak);

        stopBtn.addEventListener('click', function() {
            stopSpeaking();
            // also pause video if needed
            video.pause();
        });

        clearBtn.addEventListener('click', function() {
            textInput.value = '';
            setStatus('🗑 បានសម្អាតអត្ថបទ');
        });

        // Video upload
        videoUpload.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const url = URL.createObjectURL(file);
                loadVideo(url);
                // auto fill URL input
                videoUrl.value = url;
            }
        });

        // Load from URL
        loadVideoBtn.addEventListener('click', function() {
            let url = videoUrl.value.trim();
            if (url) {
                loadVideo(url);
            } else {
                setStatus('⚠️ សូមបញ្ចូល URL វីដេអូ');
            }
        });

        // Range sliders display
        rateSlider.addEventListener('input', function() {
            rateValue.textContent = parseFloat(this.value).toFixed(1);
        });
        volumeSlider.addEventListener('input', function() {
            volumeValue.textContent = Math.round(parseFloat(this.value) * 100) + '%';
        });

        // Auto-load voices if not loaded
        setInterval(() => {
            if (voiceSelect.options.length === 0) {
                populateVoiceList();
            }
        }, 2000);

        // ---------- Init status ----------
        setStatus('🎤 ត្រៀមខ្លួនជាស្រេច');
    })();
</script>
</body>
</html>
