// ── Questions data ──
const PAGES = [
  {
    trait: 'Openness', color: '#a78bfa',
    questions: [
      'I have a vivid imagination.',
      'I enjoy exploring new ideas and concepts.',
      'I am interested in abstract or philosophical topics.',
      'I enjoy artistic, creative, or expressive activities.',
      'I prefer variety and new experiences over routine.',
    ]
  },
  {
    trait: 'Conscientiousness', color: '#34d399',
    questions: [
      'I am always prepared and organized before starting tasks.',
      'I pay close attention to details.',
      'I follow a schedule and stick to plans.',
      'I complete work right away rather than leaving it for later.',
      'I like to keep things tidy and in order.',
    ]
  },
  {
    trait: 'Extraversion', color: '#fbbf24',
    questions: [
      'I feel comfortable and energized around other people.',
      'I talk a lot and enjoy conversations.',
      'I consider myself the life of the party.',
      'I start conversations easily with strangers.',
      'I enjoy being the center of attention.',
    ]
  },
  {
    trait: 'Agreeableness', color: '#f472b6',
    questions: [
      'I take time to listen to others and show interest in their lives.',
      'I sympathize easily with others\' feelings.',
      'I make people feel welcome and at ease.',
      'I try to be kind and considerate to everyone I meet.',
      'I believe most people have good intentions.',
    ]
  },
  {
    trait: 'Neuroticism', color: '#60a5fa',
    questions: [
      'I get stressed out easily.',
      'I worry about things more than I should.',
      'I get upset or irritated without a strong reason.',
      'My mood changes frequently throughout the day.',
      'I feel anxious or uneasy in new or unfamiliar situations.',
    ]
  },
];

const LABELS = ['Strongly Disagree', 'Disagree', 'Neutral', 'Agree', 'Strongly Agree'];
const TRAIT_KEYS = ['O', 'C', 'E', 'A', 'N'];

// ── State ──
let currentPage = 0;
let answers = Array(25).fill(3); // default neutral
let radarChart = null;

// ── Screen switching ──
function showScreen(id) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
}

// ── Welcome → Quiz ──
function startQuiz() {
  currentPage = 0;
  answers = Array(25).fill(3);
  renderPage();
  showScreen('quiz-screen');
}

// ── Render quiz page ──
function renderPage() {
  const { trait, color, questions } = PAGES[currentPage];
  const pageOffset = currentPage * 5;

  // Header
  document.getElementById('page-label').textContent = `Page ${currentPage + 1} of 5`;
  document.getElementById('trait-label').textContent = trait;
  document.getElementById('trait-label').style.setProperty('--c', color);

  // Progress bar
  const pct = ((currentPage) / 5) * 100;
  document.getElementById('progress-bar').style.width = pct + '%';

  // Questions
  const container = document.getElementById('questions-container');
  const page = document.createElement('div');
  page.className = 'question-page';

  questions.forEach((qText, qi) => {
    const globalIdx = pageOffset + qi;
    const answered  = answers[globalIdx] !== undefined;

    const card = document.createElement('div');
    card.className = 'question-card' + (answered && answers[globalIdx] !== 3 ? ' answered' : '');
    card.id = `qcard-${globalIdx}`;

    const num = document.createElement('div');
    num.className = 'question-num';
    num.textContent = `Q${globalIdx + 1} · ${trait}`;

    const text = document.createElement('div');
    text.className = 'question-text';
    text.textContent = qText;

    const row = document.createElement('div');
    row.className = 'likert-row';

    for (let v = 1; v <= 5; v++) {
      const btn = document.createElement('button');
      btn.className = 'likert-btn' + (answers[globalIdx] === v ? ' selected' : '');
      btn.textContent = v;
      btn.title = LABELS[v - 1];
      btn.dataset.idx = globalIdx;
      btn.dataset.val = v;
      btn.onclick = () => selectAnswer(globalIdx, v, color);
      row.appendChild(btn);
    }

    const lblRow = document.createElement('div');
    lblRow.className = 'likert-labels';
    lblRow.innerHTML = '<span>Strongly Disagree</span><span>Strongly Agree</span>';

    card.appendChild(num);
    card.appendChild(text);
    card.appendChild(row);
    card.appendChild(lblRow);
    page.appendChild(card);
  });

  container.innerHTML = '';
  container.appendChild(page);

  // Dots
  renderDots();

  // Nav buttons
  document.getElementById('prev-btn').disabled = currentPage === 0;
  const isLast = currentPage === PAGES.length - 1;
  const nextBtn = document.getElementById('next-btn');
  nextBtn.textContent = isLast ? 'Submit ✓' : 'Next →';
  nextBtn.style.background = isLast
    ? 'linear-gradient(135deg, #059669, #047857)'
    : '';
  nextBtn.style.boxShadow = isLast
    ? '0 4px 20px rgba(5,150,105,0.35)'
    : '';
}

function selectAnswer(idx, val, color) {
  answers[idx] = val;

  // Update buttons
  const card = document.getElementById(`qcard-${idx}`);
  if (card) {
    card.classList.add('answered');
    card.querySelectorAll('.likert-btn').forEach(btn => {
      btn.classList.toggle('selected', parseInt(btn.dataset.val) === val);
    });
  }
}

function renderDots() {
  const container = document.getElementById('dots-container');
  container.innerHTML = '';
  PAGES.forEach((_, i) => {
    const dot = document.createElement('div');
    dot.className = 'dot' + (i === currentPage ? ' active' : i < currentPage ? ' done' : '');
    dot.onclick = () => goToPage(i);
    container.appendChild(dot);
  });
}

function goToPage(i) {
  currentPage = i;
  renderPage();
}

function prevPage() {
  if (currentPage > 0) { currentPage--; renderPage(); }
}

function nextPage() {
  if (currentPage < PAGES.length - 1) {
    currentPage++;
    renderPage();
  } else {
    submitQuiz();
  }
}

// ── Submit ──
async function submitQuiz() {
  showScreen('loading-screen');

  // Animated loading trait dots
  const keys = ['O', 'C', 'E', 'A', 'N'];
  for (let i = 0; i < keys.length; i++) {
    await delay(320);
    document.getElementById(`load-${keys[i]}`).classList.add('done');
  }

  try {
    const res = await fetch('/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ answers }),
    });
    const data = await res.json();
    await delay(300);
    renderResults(data);
    showScreen('results-screen');
  } catch (err) {
    alert('Prediction failed. Make sure the Flask server is running.');
    showScreen('quiz-screen');
  }
}

// ── Results ──
function renderResults(data) {
  const traitOrder = ['O', 'C', 'E', 'A', 'N'];
  const scores = traitOrder.map(k => data[k]?.score ?? 50);
  const labels = traitOrder.map(k => data[k]?.name ?? k);
  const colors = traitOrder.map(k => data[k]?.color ?? '#7c3aed');

  // Radar chart
  const ctx = document.getElementById('radar-chart').getContext('2d');
  if (radarChart) radarChart.destroy();

  radarChart = new Chart(ctx, {
    type: 'radar',
    data: {
      labels,
      datasets: [{
        label: 'Your Score',
        data: scores,
        fill: true,
        backgroundColor: 'rgba(124,58,237,0.18)',
        borderColor: '#a78bfa',
        pointBackgroundColor: colors,
        pointBorderColor: '#fff',
        pointRadius: 5,
        pointHoverRadius: 7,
        borderWidth: 2,
      }]
    },
    options: {
      animation: { duration: 900, easing: 'easeInOutQuart' },
      scales: {
        r: {
          min: 0, max: 100,
          ticks: {
            stepSize: 25,
            color: 'rgba(148,163,184,0.6)',
            font: { size: 10 },
            backdropColor: 'transparent',
          },
          grid:        { color: 'rgba(255,255,255,0.07)' },
          angleLines:  { color: 'rgba(255,255,255,0.07)' },
          pointLabels: { color: '#e2e8f0', font: { size: 11, weight: '600' } },
        }
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => ` ${ctx.raw.toFixed(1)}%`
          }
        }
      }
    }
  });

  // Trait cards
  const cardsEl = document.getElementById('trait-cards');
  cardsEl.innerHTML = '';

  traitOrder.forEach((key, i) => {
    const t = data[key];
    if (!t) return;

    const card = document.createElement('div');
    card.className = 'trait-card';
    card.style.setProperty('--tc', t.color);
    card.style.animationDelay = `${i * 0.1}s`;

    const isHigh = t.label === 'High';

    card.innerHTML = `
      <div class="tc-header">
        <div class="tc-name">${t.icon} ${t.name}</div>
        <span class="tc-badge ${isHigh ? 'high' : 'low'}">${t.label}</span>
      </div>
      <div class="tc-bar-track">
        <div class="tc-bar-fill" style="width:0%;background:${t.color}" data-target="${t.score}"></div>
      </div>
      <div class="tc-score">${t.score}%</div>
      <div class="tc-desc">${t.description}</div>
    `;

    cardsEl.appendChild(card);

    // Animate bar fill
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        card.querySelector('.tc-bar-fill').style.width = t.score + '%';
      });
    });
  });
}

function resetQuiz() {
  document.querySelectorAll('.load-trait').forEach(el => el.classList.remove('done'));
  startQuiz();
}

function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
