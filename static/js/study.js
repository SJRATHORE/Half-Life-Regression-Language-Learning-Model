/**
 * study.js — Farsi HLR Study Session
 *
 * Two independent Fisher-Yates shuffles:
 *   1. SESSION_WORDS  — which words appear and in what order
 *   2. SESSION_TYPES  — what question type each slot gets
 *
 * Type pool is built as equal thirds (MCQ / Flashcard / Typing),
 * then shuffled completely independently from the word order.
 * FORCE_MODE overrides all type assignment for dev testing.
 */

/* ══════════════════════════════════════════════════════════════════════
   UTILITIES
   ══════════════════════════════════════════════════════════════════════ */

/** Fisher-Yates shuffle — returns a new array, never mutates */
function shuffle(arr) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function normalise(s) {
  return String(s).trim().toLowerCase().replace(/[^\w\s]/g, '');
}

function levenshtein(a, b) {
  const m = a.length, n = b.length;
  const dp = Array.from({length: m + 1}, (_, i) =>
    Array.from({length: n + 1}, (_, j) => i || j));
  for (let i = 1; i <= m; i++)
    for (let j = 1; j <= n; j++)
      dp[i][j] = a[i-1] === b[j-1]
        ? dp[i-1][j-1]
        : 1 + Math.min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1]);
  return dp[m][n];
}

/** HTML-escape for safe innerHTML insertion */
function esc(str) {
  return String(str ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

/* ══════════════════════════════════════════════════════════════════════
   QUESTION-TYPE ASSIGNMENT
   Two completely independent Fisher-Yates shuffles.
   ══════════════════════════════════════════════════════════════════════ */

/**
 * Build a type array of length n with equal thirds:
 *   ['mcq', 'mcq', ..., 'flashcard', ..., 'typing', ...]
 * then run a SEPARATE Fisher-Yates shuffle on it.
 *
 * Remainder slots (when n % 3 != 0) cycle through the three types.
 */
function buildTypePool(n) {
  if (FORCE_MODE) return Array(n).fill(FORCE_MODE);

  const types = ['mcq', 'flashcard', 'typing'];
  const pool  = [];
  const base  = Math.floor(n / 3);
  const rem   = n % 3;

  // Fill equal thirds
  types.forEach(t => { for (let i = 0; i < base; i++) pool.push(t); });
  // Distribute remainder evenly
  for (let i = 0; i < rem; i++) pool.push(types[i]);

  // ── Second independent Fisher-Yates (different call = different RNG state) ──
  return shuffle(pool);
}

/* ══════════════════════════════════════════════════════════════════════
   VOICE  (Web Speech API — fa-IR, zero dependencies)
   ══════════════════════════════════════════════════════════════════════ */

let ttsVoice = null;

function loadFarsiVoice() {
  const voices = window.speechSynthesis?.getVoices() ?? [];
  ttsVoice = voices.find(v => v.lang === 'fa-IR')
          || voices.find(v => v.lang.startsWith('fa'))
          || null;
}

if (window.speechSynthesis) {
  loadFarsiVoice();
  window.speechSynthesis.onvoiceschanged = loadFarsiVoice;
}

function speakFarsi(text) {
  if (!window.speechSynthesis || !text) return;
  window.speechSynthesis.cancel();
  const utt = new SpeechSynthesisUtterance(text);
  utt.lang  = 'fa-IR';
  utt.rate  = 0.85;
  if (ttsVoice) utt.voice = ttsVoice;
  window.speechSynthesis.speak(utt);
}

/**
 * Voice button HTML — NO Farsi text inside the HTML attribute.
 * Event listener is attached via wireVoice() after innerHTML is set.
 */
function voiceBtnHTML() {
  return `<button class="voice-btn js-speak" title="Hear pronunciation">🔊</button>`;
}

function wireVoice(farsiText) {
  cardInner.querySelectorAll('.js-speak').forEach(btn => {
    btn.addEventListener('click', () => speakFarsi(farsiText));
  });
}

/* ══════════════════════════════════════════════════════════════════════
   SESSION STATE
   ══════════════════════════════════════════════════════════════════════ */

// Shuffle 1: word order
const SESSION_WORDS = shuffle(WORDS);
const total         = SESSION_WORDS.length;

// Shuffle 2: question types (completely independent call)
const SESSION_TYPES = buildTypePool(total);

let idx     = 0;
let results = [];

/* ══════════════════════════════════════════════════════════════════════
   DOM REFS
   ══════════════════════════════════════════════════════════════════════ */

const studyBar    = document.getElementById('study-bar');
const cardIndex   = document.getElementById('card-index');
const cardTotal   = document.getElementById('card-total');
const typeBadge   = document.getElementById('type-badge');
const sessionDone = document.getElementById('session-done');
const cardInner   = document.getElementById('card-inner');

cardTotal.textContent = total;

/* ══════════════════════════════════════════════════════════════════════
   RENDER DISPATCHER
   ══════════════════════════════════════════════════════════════════════ */

renderCard();

function renderCard() {
  if (idx >= total) { finishSession(); return; }

  const word = SESSION_WORDS[idx];
  const type = SESSION_TYPES[idx];       // ← from the TYPE shuffle, not half-life

  cardIndex.textContent = idx + 1;
  studyBar.style.width  = `${(idx / total) * 100}%`;

  const labels  = { mcq: '⚡ MCQ', flashcard: '🃏 Flashcard', typing: '✍️ Typing' };
  const classes = { mcq: 'type-mcq', flashcard: 'type-flashcard', typing: 'type-typing' };
  typeBadge.textContent = labels[type];
  typeBadge.className   = `study-type-badge ${classes[type]}`;

  // Fade out
  cardInner.style.transition = 'none';
  cardInner.style.opacity    = '0';
  cardInner.style.transform  = 'translateY(10px)';

  setTimeout(() => {
    try {
      if      (type === 'mcq')    renderMCQ(word);
      else if (type === 'typing') renderTyping(word);
      else                        renderFlashcard(word);
    } catch (err) {
      console.error('[study] renderCard error:', err, word);
    }

    cardInner.style.transition = 'opacity 0.22s, transform 0.22s';
    cardInner.style.opacity    = '1';
    cardInner.style.transform  = 'translateY(0)';

    speakFarsi(word.farsi);
  }, 120);
}

/* ══════════════════════════════════════════════════════════════════════
   🃏  FLASHCARD
   ══════════════════════════════════════════════════════════════════════ */

function renderFlashcard(word) {
  cardInner.innerHTML = `
    <div class="flashcard">
      <div class="card-front" id="card-front">
        <div class="card-category">${esc(word.category)}</div>
        <div class="card-farsi-row">
          <div class="farsi-word">${esc(word.farsi)}</div>
          ${voiceBtnHTML()}
        </div>
        <div class="translit">${esc(word.transliteration)}</div>
        <button class="btn btn-primary btn-large" id="show-ans-btn">Show Answer</button>
      </div>
      <div class="card-back hidden" id="card-back">
        <div class="card-farsi-row">
          <div class="farsi-word">${esc(word.farsi)}</div>
          ${voiceBtnHTML()}
        </div>
        <div class="translit">${esc(word.transliteration)}</div>
        <div class="english-word">${esc(word.english)}</div>
        <div class="answer-btns">
          <button class="btn-incorrect" id="btn-wrong">✗ &nbsp;Incorrect</button>
          <button class="btn-correct"   id="btn-right">✓ &nbsp;Correct</button>
        </div>
      </div>
    </div>`;

  wireVoice(word.farsi);
  document.getElementById('show-ans-btn').addEventListener('click', () => {
    document.getElementById('card-front').classList.add('hidden');
    document.getElementById('card-back').classList.remove('hidden');
  });
  document.getElementById('btn-wrong').addEventListener('click', () => recordAnswer(false));
  document.getElementById('btn-right').addEventListener('click', () => recordAnswer(true));
}

/* ══════════════════════════════════════════════════════════════════════
   ⚡  MCQ
   ══════════════════════════════════════════════════════════════════════ */

function renderMCQ(word) {
  const wrong   = shuffle(ALL_WORDS.filter(w => w.id !== word.id)).slice(0, 3).map(w => w.english);
  const options = shuffle([word.english, ...wrong]);

  cardInner.innerHTML = `
    <div class="flashcard">
      <div class="card-category">${esc(word.category)}</div>
      <div class="card-farsi-row">
        <div class="farsi-word">${esc(word.farsi)}</div>
        ${voiceBtnHTML()}
      </div>
      <div class="translit">${esc(word.transliteration)}</div>
      <p class="mcq-question">What does this word mean?</p>
      <div class="mcq-grid">
        ${options.map((opt, i) =>
          `<button class="mcq-btn" id="mcq-opt-${i}">${esc(opt)}</button>`
        ).join('')}
      </div>
      <div class="hidden" id="mcq-next">
        <button class="btn btn-primary mcq-next-btn" id="mcq-next-btn">Next →</button>
      </div>
    </div>`;

  wireVoice(word.farsi);

  let answered = false;
  options.forEach((opt, i) => {
    document.getElementById(`mcq-opt-${i}`).addEventListener('click', () => {
      if (answered) return;
      answered = true;

      const isCorrect = normalise(opt) === normalise(word.english);

      options.forEach((o, j) => {
        const btn = document.getElementById(`mcq-opt-${j}`);
        btn.disabled = true;
        if (normalise(o) === normalise(word.english))  btn.classList.add('correct-choice');
        else if (j === i && !isCorrect)                btn.classList.add('wrong-choice');
      });

      document.getElementById('mcq-next').classList.remove('hidden');
      document.getElementById('mcq-next-btn')
        .addEventListener('click', () => recordAnswer(isCorrect), { once: true });
    });
  });
}

/* ══════════════════════════════════════════════════════════════════════
   ✍️  TYPING
   ══════════════════════════════════════════════════════════════════════ */

function renderTyping(word) {
  cardInner.innerHTML = `
    <div class="flashcard">
      <div class="card-category">${esc(word.category)}</div>
      <div class="card-farsi-row">
        <div class="farsi-word">${esc(word.farsi)}</div>
        ${voiceBtnHTML()}
      </div>
      <div class="translit">${esc(word.transliteration)}</div>
      <p class="typing-question">Type the English meaning:</p>
      <input class="typing-input" id="typing-input" type="text"
             placeholder="Type your answer…"
             autocomplete="off" autocorrect="off" spellcheck="false"/>
      <p   class="typing-hint"   id="typing-hint"></p>
      <div class="typing-reveal hidden" id="typing-reveal"></div>
      <div class="answer-btns" style="margin-top:0.5rem">
        <button class="btn btn-primary"            id="check-btn">Check</button>
        <button class="btn btn-secondary hidden"   id="next-btn">Next →</button>
      </div>
    </div>`;

  wireVoice(word.farsi);

  const input    = document.getElementById('typing-input');
  const hint     = document.getElementById('typing-hint');
  const reveal   = document.getElementById('typing-reveal');
  const checkBtn = document.getElementById('check-btn');
  const nextBtn  = document.getElementById('next-btn');

  input.focus();

  function checkTyping() {
    const userAns = input.value.trim();
    if (!userAns) return;

    const isCorrect = normalise(userAns) === normalise(word.english)
                   || levenshtein(normalise(userAns), normalise(word.english)) <= 1;

    input.disabled = true;
    checkBtn.classList.add('hidden');
    nextBtn.classList.remove('hidden');

    if (isCorrect) {
      input.classList.add('correct-ans');
      hint.textContent = '✓ Correct!';
      hint.style.color = 'var(--correct)';
    } else {
      input.classList.add('wrong-ans');
      hint.textContent        = '✗ Not quite.';
      hint.style.color        = 'var(--incorrect)';
      reveal.textContent      = `Answer: ${word.english}`;
      reveal.classList.remove('hidden');
    }
    nextBtn.addEventListener('click', () => recordAnswer(isCorrect), { once: true });
  }

  checkBtn.addEventListener('click', checkTyping);
  input.addEventListener('keydown', e => { if (e.key === 'Enter') checkTyping(); });
}

/* ══════════════════════════════════════════════════════════════════════
   RECORD + ADVANCE
   ══════════════════════════════════════════════════════════════════════ */

function recordAnswer(correct) {
  results.push({
    word_id:  SESSION_WORDS[idx].id,
    correct:  !!correct,
    q_type:   SESSION_TYPES[idx],
  });
  idx++;
  renderCard();
}

/* ══════════════════════════════════════════════════════════════════════
   FINISH SESSION
   ══════════════════════════════════════════════════════════════════════ */

function finishSession() {
  studyBar.style.width = '100%';
  sessionDone.classList.remove('hidden');
  fetch('/submit_session', {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify({ results }),
  })
    .then(r => r.json())
    .then(() => { window.location.href = '/results'; })
    .catch(() => { window.location.href = '/results'; });
}
