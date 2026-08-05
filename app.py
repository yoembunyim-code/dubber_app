from flask import Flask, render_template_string

app = Flask(_name_)

html_content = """
<!DOCTYPE html>
<html lang="km">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>អ្នកបកប្រែវីដេអូខ្មែរ - VIP</title>
    <style>
        /* ចំណាំ៖ CSS ទាំងអស់នេះស្ថិតក្នុង string របស់ Python ដូច្នេះ # មិនបង្កជា SyntaxError ទេ */
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        body {
            font-family: 'Khmer OS', 'Noto Sans Khmer', sans-serif;
            background: linear-gradient(145deg, #f5f3f8 0%, #e8e4de 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            max-width: 850px;
            width: 100%;
            background: rgba(255,255,255,0.9);
            backdrop-filter: blur(12px);
            border-radius: 40px;
            padding: 30px 28px;
            box-shadow: 0 25px 50px -12px rgba(0,0,0,0.3);
            border: 1px solid rgba(255,255,255,0.5);
        }
        h1 {
            font-size: 2.2rem;
            color: #2d2a24;
            text-align: center;
        }
        .sub {
            text-align: center;
            color: #6b6258;
            margin-bottom: 20px;
            border-bottom: 2px dashed #d6cec4;
            padding-bottom: 12px;
        }
        .telegram-section {
            background: #f3efe9;
            padding: 14px 20px;
            border-radius: 60px;
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            align-items: center;
            margin-bottom: 20px;
        }
        .telegram-section label {
            font-weight: 600;
            color: #3d352c;
        }
        .telegram-section input {
            flex: 1;
            min-width: 150px;
            padding: 10px 16px;
            border-radius: 40px;
            border: 1px solid #ccc;
            font-size: 0.95rem;
        }
        .telegram-section button {
            padding: 10px 24px;
            background: #2d2a24;
            color: white;
            border: none;
            border-radius: 40px;
            font-weight: 600;
            cursor: pointer;
        }
        .telegram-section button:hover {
            background: #4a3f36;
        }
        #telegramStatus {
            font-size: 0.9rem;
            color: #3a7d5c;
        }
        .video-section {
            background: #1e1b17;
            border-radius: 28px;
            overflow: hidden;
            margin-bottom: 20px;
        }
        #videoPlayer {
            width: 100%;
            display: block;
            aspect-ratio: 16/9;
            background: #000;
        }
        .video-controls {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin: 12px 0 18px;
        }
        .video-controls input[type="file"] {
            flex: 1;
            min-width: 140px;
            padding: 8px 14px;
            border-radius: 60px;
            border: 1px solid #ccc;
            background: white;
        }
        .video-controls input[type="text"] {
            flex: 2;
            min-width: 180px;
            padding: 10px 18px;
            border-radius: 60px;
            border: 1px solid #ccc;
        }
        .video-controls button {
            padding: 10px 24px;
            background: #b48b6e;
            color: white;
            border: none;
            border-radius: 60px;
            font-weight: 600;
            cursor: pointer;
        }
        .translate-area textarea {
            width: 100%;
            min-height: 100px;
            padding: 16px;
            border-radius: 24px;
            border: 1px solid #ddd;
            font-family: inherit;
            font-size: 1rem;
            background: #fefcf9;
            resize: vertical;
        }
        .action-row {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            margin: 16px 0 12px;
        }
        .action-row .btn {
            padding: 12px 28px;
            border: none;
            border-radius: 60px;
            font-weight: 600;
            background: #e4ddd4;
            cursor: pointer;
        }
        .btn-primary {
            background: #b48b6e !important;
            color: white !important;
        }
        .btn-danger {
            background: #c73b3b !important;
            color: white !important;
        }
        .btn-success {
            background: #3a7d5c !important;
            color: white !important;
        }
        .settings {
            background: #f3efe9;
            padding: 16px 22px;
            border-radius: 40px;
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            align-items: center;
            margin: 12px 0;
        }
        .settings label {
            display: flex;
            align-items: center;
            gap: 8px;
            font-weight: 500;
        }
        .settings select, .settings input[type="range"] {
            padding: 6px 12px;
            border-radius: 40px;
            border: 1px solid #ccc;
        }
        .vip-info {
            background: #fff3e0;
            padding: 14px 20px;
            border-radius: 30px;
            margin: 14px 0;
            border-left: 6px solid #b48b6e;
            font-size: 0.95rem;
        }
        .vip-info a {
            color: #b48b6e;
            font-weight: bold;
            text-decoration: none;
        }
        .status {
            padding: 14px 18px;
            border-radius: 30px;
            background: #ede8e1;
            min-height: 50px;
            display: flex;
            align-items: center;
            gap: 10px;
            border-left: 5px solid #b48b6e;
        }
        .footer {
            text-align: center;
            font-size: 0.8rem;
            color: #8a7e72;
            margin-top: 18px;
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
    <div class="sub">បញ្ចូលអត្ថបទ ជ្រើសសំឡេង និងទទួលបានសំឡេងដូចមនុស្ស</div>

    <!-- ====== 1. Telegram Section ====== -->
    <div class="telegram-section">
        <label>📱 Telegram៖</label>
        <input type="text" id="telegramUser" placeholder="t.me/bunyimyoem" />
        <button id="saveTelegramBtn">រក្សាទុក</button>
        <span id="telegramStatus"></span>
    </div>

    <!-- ====== 2. Video Player ====== -->
    <div class="video-section">
        <video id="videoPlayer" controls playsinline>
            <source src="" type="video/mp4" />
        </video>
    </div>

    <!-- ====== 3. Video Controls ====== -->
    <div class="video-controls">
        <input type="file" id="videoUpload" accept="video/*" />
        <input type="text" id="videoUrl" placeholder="បិទភ្ជាប់ URL វីដេអូ" />
        <button id="loadVideoBtn">📥 ដាក់វីដេអូ</button>
    </div>

    <!-- ====== 4. Translate Area ====== -->
    <div class="translate-area">
        <textarea id="textInput" placeholder="សរសេរអត្ថបទខ្មែរនៅទីនេះ">សួស្តី! នេះជាការសាកល្បងបកប្រែវីដេអូ។ សូមស្តាប់សំឡេងអានប្រយោគនេះ។</textarea>
    </div>

    <!-- ====== 5. Action Buttons ====== -->
    <div class="action-row">
        <button class="btn btn-primary" id="speakBtn">🔊 អានអត្ថបទ</button>
        <button class="btn btn-danger" id="stopBtn">⏹ បញ្ឈប់</button>
        <button class="btn btn-success" id="clearBtn">🗑 សម្អាត</button>
    </div>

    <!-- ====== 6. Settings (Voice, Rate, Volume) ====== -->
    <div class="settings">
        <label>🗣 សំឡេង:
            <select id="voiceSelect"></select>
        </label>
        <label>🐢 ល្បឿន:
            <input type="range" id="rateSlider" min="0.5" max="2" step="0.1" value="1.0" />
            <span id="rateValue">1.0</span>
        </label>
        <label>🔊 កម្រិត:
            <input type="range" id="volumeSlider" min="0" max="1" step="0.05" value="1.0" />
            <span id="volumeValue">100%</span>
        </label>
    </div>

    <!-- ====== 7. VIP Info (បង្ហាញចំនួនដង និងតំណទិញ VIP) ====== -->
    <div class="vip-info">
        <p>📊 អ្នកបានប្រើប្រាស់ <span id="usageCount">0</span> / 3 ដងឥតគិតថ្លៃ។</p>
        <p>💎 ចុច <a href="#" id="buyVipLink">ទីនេះ</a> ដើម្បីទិញ VIP ប្រើមិនកំណត់។</p>
    </div>

    <!-- ====== 8. Status Bar ====== -->
    <div class="status" id="statusBar">
        <span>⏳ ត្រៀមខ្លួនជាស្រេច</span>
    </div>

    <div class="footer">បង្កើតដោយស្មារតីស្រឡាញ់ភាសាខ្មែរ 🇰🇭</div>
</div>

<script>
    (function() {
        // ---------- DOM references ----------
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
        const telegramUserInput = document.getElementById('telegramUser');
        const saveTelegramBtn = document.getElementById('saveTelegramBtn');
        const telegramStatus = document.getElementById('telegramStatus');
        const usageCountSpan = document.getElementById('usageCount');
        const buyVipLink = document.getElementById('buyVipLink');

        // ---------- Speech Synthesis ----------
        const synth = window.speechSynthesis;
        let currentUtterance = null;
        let isSpeaking = false;
        let queue = [];

        // ---------- Voice List ----------
        function populateVoiceList() {
            const voices = synth.getVoices();
            voiceSelect.innerHTML = '';
            let khmerVoices = voices.filter(v => v.lang.startsWith('km'));
            let list = khmerVoices.length > 0 ? khmerVoices : voices;
            if (list.length === 0) {
                let opt = document.createElement('option');
                opt.value = '';
                opt.textContent = 'គ្មានសំឡេង';
                voiceSelect.appendChild(opt);
                return;
            }
            list.forEach(voice => {
                let opt = document.createElement('option');
                opt.value = voice.name;
                opt.textContent = voice.name + ' (' + voice.lang + ')';
                if (voice.lang.startsWith('km')) opt.selected = true;
                voiceSelect.appendChild(opt);
            });
        }
        if (synth) {
            synth.onvoiceschanged = populateVoiceList;
            setTimeout(populateVoiceList, 200);
        }

        // ---------- LocalStorage Utils (សម្រាប់រាប់ចំនួនដង និងឈ្មោះ Telegram) ----------
        function getUsageCount() {
            return parseInt(localStorage.getItem('video_usage_count') || '0');
        }
        function setUsageCount(val) {
            localStorage.setItem('video_usage_count', val.toString());
        }
        function incrementUsage() {
            let c = getUsageCount();
            c++;
            setUsageCount(c);
            return c;
        }
        function updateUsageDisplay() {
            let count = getUsageCount();
            usageCountSpan.innerText = count;
        }
        function checkVideoLimit() {
            let count = getUsageCount();
            if (count >= 3) {
                alert('⚠️ អ្នកបានប្រើប្រាស់វីដេអូឥតគិតថ្លៃចំនួន ៣ ដងរួចហើយ។ សូមបង់លុយដើម្បីប្រើ VIP (ចុចតំណ "ទីនេះ" ខាងក្រោម)');
                return false;
            }
            return true;
        }

        // ---------- Telegram ----------
        function loadTelegramUser() {
            let saved = localStorage.getItem('telegram_user');
            if (saved) {
                telegramUserInput.value = saved;
                telegramStatus.innerText = '✅ បានរក្សាទុក';
            }
        }
        saveTelegramBtn.addEventListener('click', function() {
            let name = telegramUserInput.value.trim();
            if (name) {
                localStorage.setItem('telegram_user', name);
                telegramStatus.innerText = '✅ បានរក្សាទុក ' + name;
            } else {
                alert('សូមបញ្ចូលឈ្មោះ Telegram');
            }
        });
        loadTelegramUser();

        // ---------- VIP Buy Link ----------
        buyVipLink.addEventListener('click', function(e) {
            e.preventDefault();
            alert('💎 សូមទាក់ទងមកកាន់ Telegram: @your_support ដើម្បីទិញ VIP (ប្រើមិនកំណត់)');
        });

        // ---------- Set Status ----------
        function setStatus(text, isLoading = false) {
            statusBar.innerHTML = isLoading ? <span class="spinner"></span> ${text} : <span>${text}</span>;
        }

        // ---------- Load Video (រាប់ចំនួនដង) ----------
        function loadVideo(src) {
            if (!checkVideoLimit()) return; // បើលើស 3 ដង បញ្ឈប់
            if (!src) return;
            video.src = src;
            video.load();
            video.play().catch(() => {});
            let newCount = incrementUsage();
            updateUsageDisplay();
            setStatus('📹 វីដេអូចាក់រួច (បានប្រើ ' + newCount + '/3 ដង)');
        }

        videoUpload.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const url = URL.createObjectURL(file);
                loadVideo(url);
                videoUrl.value = url;
            }
        });

        loadVideoBtn.addEventListener('click', function() {
            let url = videoUrl.value.trim();
            if (url) {
                loadVideo(url);
            } else {
                setStatus('⚠️ សូមបញ្ចូល URL');
            }
        });

        // ---------- Speak (រាប់ចំនួនដងផងដែរ) ----------
        function splitIntoSentences(text) {
            let sentences = text.match(/[^.!?]+[.!?]+|[^.!?]+$/g);
            if (!sentences) return [text];
            return sentences.map(s => s.trim()).filter(s => s.length > 0);
        }

        function stopSpeaking() {
            if (synth) synth.cancel();
            isSpeaking = false;
            queue = [];
            currentUtterance = null;
            setStatus('⏹ បានបញ្ឈប់');
        }

        function speakSentences(sentences, rate, volume, voiceName) {
            if (!synth) {
                setStatus('❌ មិនគាំទ្រ Speech');
                return;
            }
            if (isSpeaking) stopSpeaking();
            if (sentences.length === 0) {
                setStatus('⚠️ គ្មានអត្ថបទ');
                return;
            }
            isSpeaking = true;
            queue = [...sentences];
            let index = 0;

            function speakNext() {
                if (!isSpeaking || index >= queue.length) {
                    isSpeaking = false;
                    setStatus('✅ អានចប់');
                    return;
                }
                let sentence = queue[index];
                if (sentence.trim().length === 0) {
                    index++;
                    speakNext();
                    return;
                }
                let utterance = new SpeechSynthesisUtterance(sentence);
                utterance.lang = 'km-KH';
                let voices = synth.getVoices();
                let selected = voices.find(v => v.name === voiceName);
                if (selected) utterance.voice = selected;
                else {
                    let khmer = voices.find(v => v.lang.startsWith('km'));
                    if (khmer) utterance.voice = khmer;
                }
                utterance.rate = rate;
                utterance.volume = volume;
                utterance.pitch = 1.0;
                utterance.onend = function() {
                    index++;
                    setTimeout(() => speakNext(), 450); // ផ្អាកដូចមនុស្សនិយាយ
                };
                utterance.onerror = function() {
                    index++;
                    setTimeout(() => speakNext(), 300);
                };
                currentUtterance = utterance;
                setStatus🔊 កំពុងនិយាយ (${index+1}/${queue.length})...`, true);
                synth.speak(utterance);
            }
            speakNext();
        }

        function handleSpeak() {
            if (!checkVideoLimit()) return; // ពិនិត្យចំនួនដង
            let text = textInput.value.trim();
            if (!text) {
                setStatus('⚠️ សូមបញ្ចូលអត្ថបទ');
                return;
            }
            let voices = synth.getVoices();
            if (voices.length === 0) {
                setStatus('⏳ កំពុងផ្ទុកសំឡេង...');
                setTimeout(() => handleSpeak(), 500);
                return;
            }
            let rate = parseFloat(rateSlider.value);
            let volume = parseFloat(volumeSlider.value);
            let voiceName = voiceSelect.value;
            let sentences = splitIntoSentences(text);
            speakSentences(sentences, rate, volume, voiceName);
            let newCount = incrementUsage();
            updateUsageDisplay();
        }

        // ---------- Event Listeners ----------
        speakBtn.addEventListener('click', handleSpeak);
        stopBtn.addEventListener('click', function() {
            stopSpeaking();
            video.pause();
        });
        clearBtn.addEventListener('click', function() {
            textInput.value = '';
            setStatus('🗑 សម្អាតរួច');
        });

        // Range sliders display
        rateSlider.addEventListener('input', function() {
            rateValue.textContent = parseFloat(this.value).toFixed(1);
        });
        volumeSlider.addEventListener('input', function() {
            volumeValue.textContent = Math.round(parseFloat(this.value) * 100) + '%';
        });

        // ---------- Init ----------
        updateUsageDisplay();
        setStatus('🎤 ត្រៀមខ្លួន');
    })();
</script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(html_content)

if _name_ == '_main_':
    app.run(debug=True, host='0.0.0.0', port=5000)
