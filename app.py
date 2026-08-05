1  from flask import Flask, render_template_string
  2  
  3  app = Flask(_name_)
  4  
  5  html_content = """
  6  <!DOCTYPE html>
  7  <html lang="km">
  8  <head>
  9      <meta charset="UTF-8" />
 10      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
 11      <title>អ្នកបកប្រែវីដេអូខ្មែរ - VIP</title>
 12      <style>
 13          /* ===== CSS ===== */
 14          * { box-sizing: border-box; margin: 0; padding: 0; }
 15          body {
 16              font-family: 'Khmer OS', 'Noto Sans Khmer', sans-serif;
 17              background: linear-gradient(145deg, #f5f3f8 0%, #e8e4de 100%);
 18              min-height: 100vh;
 19              display: flex;
 20              justify-content: center;
 21              align-items: center;
 22              padding: 20px;
 23          }
 24          .container {
 25              max-width: 850px;
 26              width: 100%;
 27              background: rgba(255,255,255,0.9);
 28              backdrop-filter: blur(12px);
 29              border-radius: 40px;
 30              padding: 30px 28px;
 31              box-shadow: 0 25px 50px -12px rgba(0,0,0,0.3);
 32              border: 1px solid rgba(255,255,255,0.5);
 33          }
 34          h1 {
 35              font-size: 2.2rem;
 36              color: #2d2a24;
 37              text-align: center;
 38          }
 39          .sub {
 40              text-align: center;
 41              color: #6b6258;
 42              margin-bottom: 20px;
 43              border-bottom: 2px dashed #d6cec4;
 44              padding-bottom: 12px;
 45          }
 46  
 47          /* ============================================================
 48             ផ្នែកទី 1: TELEGRAM + VIP CODE (ដាក់នៅបន្ទាត់លើៗ)
 49             ============================================================ */
 50          .info-section {
 51              background: #f3efe9;
 52              padding: 16px 20px;
 53              border-radius: 30px;
 54              display: flex;
 55              flex-wrap: wrap;
 56              gap: 16px;
 57              align-items: center;
 58              margin-bottom: 20px;
 59              border-left: 6px solid #b48b6e;
 60          }
 61          .info-section label {
 62              font-weight: 600;
 63              color: #3d352c;
 64              min-width: 80px;
 65          }
 66          .info-section input {
 67              flex: 1;
 68              min-width: 140px;
 69              padding: 10px 16px;
 70              border-radius: 40px;
 71              border: 1px solid #ccc;
 72              font-size: 0.95rem;
 73          }
 74          .info-section button {
 75              padding: 10px 24px;
 76              background: #2d2a24;
 77              color: white;
 78              border: none;
 79              border-radius: 40px;
 80              font-weight: 600;
 81              cursor: pointer;
 82              white-space: nowrap;
 83          }
 84          .info-section button:hover {
 85              background: #4a3f36;
 86          }
 87          .info-section .status-text {
 88              font-size: 0.9rem;
 89              color: #3a7d5c;
 90          }
 91          .info-section .vip-badge {
 92              background: #b48b6e;
 93              color: white;
 94              padding: 4px 16px;
 95              border-radius: 40px;
 96              font-weight: 600;
 97              font-size: 0.85rem;
 98              display: inline-block;
 99          }
100  
101          /* ===== ផ្នែកវីដេអូ ===== */
102          .video-section {
103              background: #1e1b17;
104              border-radius: 28px;
105              overflow: hidden;
106              margin-bottom: 20px;
107          }
108          #videoPlayer {
109              width: 100%;
110              display: block;
111              aspect-ratio: 16/9;
112              background: #000;
113          }
114          .video-controls {
115              display: flex;
116              gap: 12px;
117              flex-wrap: wrap;
118              margin: 12px 0 18px;
119          }
120          .video-controls input[type="file"] {
121              flex: 1;
122              min-width: 140px;
123              padding: 8px 14px;
124              border-radius: 60px;
125              border: 1px solid #ccc;
126              background: white;
127          }
128          .video-controls input[type="text"] {
129              flex: 2;
130              min-width: 180px;
131              padding: 10px 18px;
132              border-radius: 60px;
133              border: 1px solid #ccc;
134          }
135          .video-controls button {
136              padding: 10px 24px;
137              background: #b48b6e;
138              color: white;
139              border: none;
140              border-radius: 60px;
141              font-weight: 600;
142              cursor: pointer;
143          }
144  
145          /* ===== ផ្នែកអត្ថបទ ===== */
146          .translate-area textarea {
147              width: 100%;
148              min-height: 100px;
149              padding: 16px;
150              border-radius: 24px;
151              border: 1px solid #ddd;
152              font-family: inherit;
153              font-size: 1rem;
154              background: #fefcf9;
155              resize: vertical;
156          }
157  
158          /* ===== ប៊ូតុង ===== */
159          .action-row {
160              display: flex;
161              flex-wrap: wrap;
162              gap: 12px;
163              margin: 16px 0 12px;
164          }
165          .action-row .btn {
166              padding: 12px 28px;
167              border: none;
168              border-radius: 60px;
169              font-weight: 600;
170              background: #e4ddd4;
171              cursor: pointer;
172          }
173          .btn-primary { background: #b48b6e !important; color: white !important; }
174          .btn-danger  { background: #c73b3b !important; color: white !important; }
175          .btn-success { background: #3a7d5c !important; color: white !important; }
176  
177          /* ===== ការកំណត់ ===== */
178          .settings {
179              background: #f3efe9;
180              padding: 16px 22px;
181              border-radius: 40px;
182              display: flex;
183              flex-wrap: wrap;
184              gap: 20px;
185              align-items: center;
186              margin: 12px 0;
187          }
188          .settings label {
189              display: flex;
190              align-items: center;
191              gap: 8px;
192              font-weight: 500;
193          }
194          .settings select, .settings input[type="range"] {
195              padding: 6px 12px;
196              border-radius: 40px;
197              border: 1px solid #ccc;
198          }
199  
200          /* ===== VIP Info (បង្ហាញចំនួនដង) ===== */
201          .vip-info {
202              background: #fff3e0;
203              padding: 14px 20px;
204              border-radius: 30px;
205              margin: 14px 0;
206              border-left: 6px solid #b48b6e;
207              font-size: 0.95rem;
208          }
209          .vip-info a {
210              color: #b48b6e;
211              font-weight: bold;
212              text-decoration: none;
213          }
214  
215          /* ===== Status ===== */
216          .status {
217              padding: 14px 18px;
218              border-radius: 30px;
219              background: #ede8e1;
220              min-height: 50px;
221              display: flex;
222              align-items: center;
223              gap: 10px;
224              border-left: 5px solid #b48b6e;
225          }
226          .footer {
227              text-align: center;
228              font-size: 0.8rem;
229              color: #8a7e72;
230              margin-top: 18px;
231          }
232          @media (max-width: 600px) {
233              .container { padding: 18px; }
234              h1 { font-size: 1.6rem; }
235              .settings { flex-direction: column; align-items: stretch; }
236              .info-section { flex-direction: column; align-items: stretch; }
237          }
238      </style>
239  </head>
240  <body>
241  <div class="container">
242      <h1>🎬 អ្នកបកប្រែវីដេអូខ្មែរ</h1>
243      <div class="sub">បញ្ចូលអត្ថបទ ជ្រើសសំឡេង និងទទួលបានសំឡេងដូចមនុស្ស</div>
244  
245      <!-- ============================================================
246           ផ្នែកទី 1: TELEGRAM + VIP CODE (បន្ទាត់ ២៤៦–២៧៤)
247           ============================================================ -->
248      <div class="info-section">
249          <label>📱 Telegram៖</label>
250          <input type="text" id="telegramUser" placeholder="បញ្ចូលឈ្មោះ @username" />
251          <button id="saveTelegramBtn">រក្សាទុក</button>
252          <span id="telegramStatus" class="status-text"></span>
253      </div>
254  
255      <div class="info-section" style="border-left-color: #c73b3b;">
256          <label>🔑 លេខកូដ VIP៖</label>
257          <input type="text" id="vipCodeInput" placeholder="បញ្ចូលលេខកូដ VIP" />
258          <button id="verifyVipBtn">ផ្ទៀងផ្ទាត់</button>
259          <span id="vipStatus" class="status-text"></span>
260          <span id="vipBadge" class="vip-badge" style="display:none;">⭐ VIP</span>
261      </div>
262  
263      <!-- ===== 2. Video Player ===== -->
264      <div class="video-section">
265          <video id="videoPlayer" controls playsinline>
266              <source src="" type="video/mp4" />
267          </video>
268      </div>
269  
270      <!-- ===== 3. Video Controls ===== -->
271      <div class="video-controls">
272          <input type="file" id="videoUpload" accept="video/*" />
273          <input type="text" id="videoUrl" placeholder="បិទភ្ជាប់ URL វីដេអូ" />
274          <button id="loadVideoBtn">📥 ដាក់វីដេអូ</button>
275      </div>
276  
277      <!-- ===== 4. Translate Area ===== -->
278      <div class="translate-area">
279          <textarea id="textInput" placeholder="សរសេរអត្ថបទខ្មែរនៅទីនេះ">សួស្តី! នេះជាការសាកល្បងបកប្រែវីដេអូ។</textarea>
280      </div>
281  
282      <!-- ===== 5. Action Buttons ===== -->
283      <div class="action-row">
284          <button class="btn btn-primary" id="speakBtn">🔊 អានអត្ថបទ</button>
285          <button class="btn btn-danger" id="stopBtn">⏹ បញ្ឈប់</button>
286          <button class="btn btn-success" id="clearBtn">🗑 សម្អាត</button>
287      </div>
288  
289      <!-- ===== 6. Settings ===== -->
290      <div class="settings">
291          <label>🗣 សំឡេង:
292              <select id="voiceSelect"></select>
293          </label>
294          <label>🐢 ល្បឿន:
295              <input type="range" id="rateSlider" min="0.5" max="2" step="0.1" value="1.0" />
296              <span id="rateValue">1.0</span>
297          </label>
298          <label>🔊 កម្រិត:
299              <input type="range" id="volumeSlider" min="0" max="1" step="0.05" value="1.0" />
300              <span id="volumeValue">100%</span>
301          </label>
302      </div>
303  
304      <!-- ===== 7. VIP Info ===== -->
305      <div class="vip-info">
306          <p>📊 អ្នកបានប្រើប្រាស់ <span id="usageCount">0</span> / 3 ដងឥតគិតថ្លៃ។</p>
307          <p>💎 បើអ្នកមានលេខកូដ VIP សូមបញ្ចូលក្នុងប្រអប់ខាងលើ។</p>
308      </div>
309  
310      <!-- ===== 8. Status Bar ===== -->
311      <div class="status" id="statusBar">
312          <span>⏳ ត្រៀមខ្លួនជាស្រេច</span>
313      </div>
314  
315      <div class="footer">បង្កើតដោយស្មារតីស្រឡាញ់ភាសាខ្មែរ 🇰🇭</div>
316  </div>
317  
318  <script>
319      (function() {
320          // ---------- DOM references ----------
321          const video = document.getElementById('videoPlayer');
322          const videoUpload = document.getElementById('videoUpload');
323          const videoUrl = document.getElementById('videoUrl');
324          const loadVideoBtn = document.getElementById('loadVideoBtn');
325          const textInput = document.getElementById('textInput');
326          const speakBtn = document.getElementById('speakBtn');
327          const stopBtn = document.getElementById('stopBtn');
328          const clearBtn = document.getElementById('clearBtn');
329          const voiceSelect = document.getElementById('voiceSelect');
330          const rateSlider = document.getElementById('rateSlider');
331          const rateValue = document.getElementById('rateValue');
332          const volumeSlider = document.getElementById('volumeSlider');
333          const volumeValue = document.getElementById('volumeValue');
334          const statusBar = document.getElementById('statusBar');
335          const telegramUserInput = document.getElementById('telegramUser');
336          const saveTelegramBtn = document.getElementById('saveTelegramBtn');
337          const telegramStatus = document.getElementById('telegramStatus');
338          const vipCodeInput = document.getElementById('vipCodeInput');
339          const verifyVipBtn = document.getElementById('verifyVipBtn');
340          const vipStatus = document.getElementById('vipStatus');
341          const vipBadge = document.getElementById('vipBadge');
342          const usageCountSpan = document.getElementById('usageCount');
343  
344          // ---------- Speech Synthesis ----------
345          const synth = window.speechSynthesis;
346          let currentUtterance = null;
347          let isSpeaking = false;
348          let queue = [];
349  
350          // ---------- Voice List ----------
351          function populateVoiceList() {
352              const voices = synth.getVoices();
353              voiceSelect.innerHTML = '';
354              let khmerVoices = voices.filter(v => v.lang.startsWith('km'));
355              let list = khmerVoices.length > 0 ? khmerVoices : voices;
356              if (list.length === 0) {
357                  let opt = document.createElement('option');
358                  opt.value = '';
359                  opt.textContent = 'គ្មានសំឡេង';
360                  voiceSelect.appendChild(opt);
361                  return;
362              }
363              list.forEach(voice => {
364                  let opt = document.createElement('option');
365                  opt.value = voice.name;
366                  opt.textContent = voice.name + ' (' + voice.lang + ')';
367                  if (voice.lang.startsWith('km')) opt.selected = true;
368                  voiceSelect.appendChild(opt);
369              });
370          }
371          if (synth) {
372              synth.onvoiceschanged = populateVoiceList;
373              setTimeout(populateVoiceList, 200);
374          }
375  
376          // =============================================================
377          //  មុខងារ VIP និងការរាប់ចំនួនដង
378          // =============================================================
379  
380          // ----- VIP status -----
381          function isVip() {
382              return localStorage.getItem('vip_active') === 'true';
383          }
384          function setVip(status) {
385              localStorage.setItem('vip_active', status ? 'true' : 'false');
386          }
387  
388          // ----- Usage count -----
389          function getUsageCount() {
390              return parseInt(localStorage.getItem('video_usage_count') || '0');
391          }
392          function setUsageCount(val) {
393              localStorage.setItem('video_usage_count', val.toString());
394          }
395          function incrementUsage() {
396              let c = getUsageCount();
397              c++;
398              setUsageCount(c);
399              return c;
400          }
401          function updateUsageDisplay() {
402              let count = getUsageCount();
403              usageCountSpan.innerText = count;
404          }
405  
406          // ----- ពិនិត្យការកំណត់ (បើ VIP មិនដាក់កំណត់) -----
407          function checkLimit() {
408              if (isVip()) return true; // VIP ប្រើមិនកំណត់
409              let count = getUsageCount();
410              if (count >= 3) {
411                  alert('⚠️ អ្នកបានប្រើប្រាស់ឥតគិតថ្លៃចំនួន ៣ ដងរួចហើយ។ សូមបញ្ចូលលេខកូដ VIP ដើម្បីប្រើបន្ត។');
412                  return false;
413              }
414              return true;
415          }
416  
417          // ----- ផ្ទៀងផ្ទាត់លេខកូដ VIP -----
418          function verifyVipCode(code) {
419              // លេខកូដសាកល្បង (អ្នកអាចប្ដូរតាមចិត្ត)
420              const validCodes = ['VIP2025', 'FREE2026', 'KHMER123'];
421              return validCodes.includes(code.trim());
422          }
423  
424          verifyVipBtn.addEventListener('click', function() {
425              let code = vipCodeInput.value.trim();
426              if (!code) {
427                  vipStatus.innerText = '⚠️ សូមបញ្ចូលលេខកូដ';
428                  return;
429              }
430              if (verifyVipCode(code)) {
431                  setVip(true);
432                  vipStatus.innerText = '✅ VIP បានដំណើរការ!';
433                  vipBadge.style.display = 'inline-block';
434                  // កំណត់ចំនួនដងឡើងវិញជា 0 (ស្រេចចិត្ត)
435                  setUsageCount(0);
436                  updateUsageDisplay();
437                  alert('🎉 សូមអបអរសាទរ! អ្នកបានក្លាយជា VIP ប្រើមិនកំណត់ហើយ។');
438              } else {
439                  vipStatus.innerText = '❌ លេខកូដមិនត្រឹមត្រូវ';
440              }
441          });
442  
443          // ----- ផ្ទុកស្ថានភាព VIP ពេលចូលទំព័រ -----
444          function loadVipStatus() {
445              if (isVip()) {
446                  vipBadge.style.display = 'inline-block';
447                  vipStatus.innerText = '✅ VIP កំពុងដំណើរការ';
448              }
449          }
450          loadVipStatus();
451  
452          // =============================================================
453          //  មុខងារ Telegram
454          // =============================================================
455          function loadTelegramUser() {
456              let saved = localStorage.getItem('telegram_user');
457              if (saved) {
458                  telegramUserInput.value = saved;
459                  telegramStatus.innerText = '✅ បានរក្សាទុក';
460              }
461          }
462          saveTelegramBtn.addEventListener('click', function() {
463              let name = telegramUserInput.value.trim();
464              if (name) {
465                  localStorage.setItem('telegram_user', name);
466                  telegramStatus.innerText = '✅ បានរក្សាទុក ' + name;
467              } else {
468                  alert('សូមបញ្ចូលឈ្មោះ Telegram');
469              }
470          });
471          loadTelegramUser();
472  
473          // =============================================================
474          //  មុខងារ Status
475          // =============================================================
476          function setStatus(text, isLoading = false) {
477              statusBar.innerHTML = isLoading ? <span class="spinner"></span> ${text} : <span>${text}</span>;
478          }
479  
480          // =============================================================
481          //  ដាក់វីដេអូ
482          // =============================================================
483          function loadVideo(src) {
484              if (!checkLimit()) return;
485              if (!src) return;
486              video.src = src;
487              video.load();
488              video.play().catch(() => {});
489              if (!isVip()) {
490                  let newCount = incrementUsage();
491                  updateUsageDisplay();
492                  setStatus('📹 វីដេអូចាក់រួច (បានប្រើ ' + newCount + '/3 ដង)');
493              } else {
494                  setStatus('📹 វីដេអូចាក់រួច (VIP ប្រើមិនកំណត់)');
495              }
496          }
497  
498          videoUpload.addEventListener('change', function(e) {
499              const file = e.target.files[0];
500              if (file) {
501                  const url = URL.createObjectURL(file);
502                  loadVideo(url);
503                  videoUrl.value = url;
504              }
505          });
506  
507          loadVideoBtn.addEventListener('click', function() {
508              let url = videoUrl.value.trim();
509              if (url) {
510                  loadVideo(url);
511              } else {
512                  setStatus('⚠️ សូមបញ្ចូល URL');
513              }
514          });
515  
516          // =============================================================
517          //  អានអត្ថបទ
518          // =============================================================
519          function splitIntoSentences(text) {
520              let sentences = text.match(/[^.!?]+[.!?]+|[^.!?]+$/g);
521              if (!sentences) return [text];
522              return sentences.map(s => s.trim()).filter(s => s.length > 0);
523          }
524  
525          function stopSpeaking() {
526              if (synth) synth.cancel();
527              isSpeaking = false;
528              queue = [];
529              currentUtterance = null;
530              setStatus('⏹ បានបញ្ឈប់');
531          }
532  
533          function speakSentences(sentences, rate, volume, voiceName) {
534              if (!synth) {
535                  setStatus('❌ មិនគាំទ្រ Speech');
536                  return;
537              }
538              if (isSpeaking) stopSpeaking();
539              if (sentences.length === 0) {
540                  setStatus('⚠️ គ្មានអត្ថបទ');
541                  return;
542              }
543              isSpeaking = true;
544              queue = [...sentences];
545              let index = 0;
546  
547              function speakNext() {
548                  if (!isSpeaking || index >= queue.length) {
549                      isSpeaking = false;
550                      setStatus('✅ អានចប់');
551                      return;
552                  }
553                  let sentence = queue[index];
554                  if (sentence.trim().length === 0) {
555                      index++;
556                      speakNext();
557                      return;
558                  }
559                  let utterance = new SpeechSynthesisUtterance(sentence);
560                  utterance.lang = 'km-KH';
561                  let voices = synth.getVoices();
562                  let selected = voices.find(v => v.name === voiceName);
563                  if (selected) utterance.voice = selected;
564                  else {
565                      let khmer = voices.find(v => v.lang.startsWith('km'));
566                      if (khmer) utterance.voice = khmer;
567                  }
568                  utterance.rate = rate;
569                  utterance.volume = volume;
570                  utterance.pitch = 1.0;
571                  utterance.onend = function() {
572                      index++;
573                      setTimeout(() => speakNext(), 450);
574                  };
575                  utterance.onerror = function() {
576                      index++;
577                      setTimeout(() => speakNext(), 300);
578                  };
579                  currentUtterance = utterance;
580                  setStatus🔊 កំពុងនិយាយ (${index+1}/${queue.length})...`, true);
581                  synth.speak(utterance);
582              }
583              speakNext();
584          }
585  
586          function handleSpeak() {
587              if (!checkLimit()) return;
588              let text = textInput.value.trim();
589              if (!text) {
590                  setStatus('⚠️ សូមបញ្ចូលអត្ថបទ');
591                  return;
592              }
593              let voices = synth.getVoices();
594              if (voices.length === 0) {
595                  setStatus('⏳ កំពុងផ្ទុកសំឡេង...');
596                  setTimeout(() => handleSpeak(), 500);
597                  return;
598              }
599              let rate = parseFloat(rateSlider.value);
600              let volume = parseFloat(volumeSlider.value);
601              let voiceName = voiceSelect.value;
602              let sentences = splitIntoSentences(text);
603              speakSentences(sentences, rate, volume, voiceName);
604              if (!isVip()) {
605                  let newCount = incrementUsage();
606                  updateUsageDisplay();
607              }
608          }
609  
610          // =============================================================
611          //  Event Listeners
612          // =============================================================
613          speakBtn.addEventListener('click', handleSpeak);
614          stopBtn.addEventListener('click', function() {
615              stopSpeaking();
616              video.pause();
617          });
618          clearBtn.addEventListener('click', function() {
619              textInput.value = '';
620              setStatus('🗑 សម្អាតរួច');
621          });
622  
623          rateSlider.addEventListener('input', function() {
624              rateValue.textContent = parseFloat(this.value).toFixed(1);
625          });
626          volumeSlider.addEventListener('input', function() {
627              volumeValue.textContent = Math.round(parseFloat(this.value) * 100) + '%';
628          });
629  
630          // =============================================================
631          //  Init
632          // =============================================================
633          updateUsageDisplay();
634          setStatus('🎤 ត្រៀមខ្លួន');
635      })();
636  </script>
637  </body>
638  </html>
639  """
640  
641  @app.route('/')
642  def home():
643      return render_template_string(html_content)
644  
645  if _name_ == '_main_':
646      app.run(debug=True, host='0.0.0.0', port=5000)
