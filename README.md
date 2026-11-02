# یادگیری فارسی — Farsi HLR

> A spaced-repetition vocabulary learning system powered by **Half-Life Regression (HLR)**  
> *Settles & Meeder, ACL 2016*

**Sudheer Rathore** · ERP 31683 &nbsp;|&nbsp; **Anser Abbas** · ERP 31675  
Institute of Business Administration (IBA), Karachi · 2026

---

## Screenshots

<table>
  <tr>
    <td align="center">
      <img src="docs/screenshots/Main_Page.png" width="420" alt="Dashboard"/>
      <br/><sub><b>Dashboard</b> — Persian rug background, glassmorphic stat cards</sub>
    </td>
    <td align="center">
      <img src="docs/screenshots/Study.png" width="420" alt="Study Session"/>
      <br/><sub><b>Study Session</b> — Typing mode with TTS pronunciation</sub>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="docs/screenshots/ProgressBreakdown_Retention.png" width="420" alt="Progress Charts"/>
      <br/><sub><b>Progress</b> — Daily recall rate, half-life distribution, cumulative words</sub>
    </td>
    <td align="center">
      <img src="docs/screenshots/All_Word_Search.png" width="420" alt="Word List"/>
      <br/><sub><b>Word List</b> — All 200 words with HLR stats, colour-coded by half-life</sub>
    </td>
  </tr>
</table>

---

## What is this?

Farsi HLR teaches a **200-word Farsi (Persian) vocabulary** using a machine-learning-driven spaced repetition algorithm. Instead of fixed flashcard intervals, the system estimates the *half-life* of each word in your long-term memory and schedules its next review precisely when your predicted recall probability drops to 50%.

Three question modes keep practice varied:

| Mode | Icon | When it appears |
|---|---|---|
| Multiple Choice | ⚡ MCQ | Randomly assigned via Fisher-Yates shuffle |
| Flashcard | 🃏 Flashcard | Randomly assigned via Fisher-Yates shuffle |
| Free Typing | ✍️ Typing | Randomly assigned via Fisher-Yates shuffle |

Each session draws from an equal-thirds pool of all three types, independently shuffled from word order — so every session is different.

---

## The Algorithm: Half-Life Regression

Based on **Settles & Meeder (ACL 2016)**, HLR combines Ebbinghaus's forgetting curve with modern ML:

```
p = 2^(−Δ/h)          Forgetting curve: recall probability at lag Δ
ĥ = 2^(Θ·x)           Estimated half-life from feature vector x
x = [1, √n, √n₊, √n₋] Features: bias, total seen, correct, incorrect
```

**Loss function** (minimised via AdaGrad):
```
ℓ = (p − p̂)² + α(h − ĥ)² + λ‖Θ‖²
```

The global weight vector Θ is stored in SQLite and updated after **every review event**, making the model personalize to your individual forgetting rate over time.

| Hyperparameter | Value | Role |
|---|---|---|
| λ (L2 regularisation) | 0.1 | Prevents overfitting |
| α (half-life loss weight) | 0.01 | Balances recall vs ĥ terms |
| η (AdaGrad learning rate) | 0.001 | Weight update step size |
| ĥ bounds | [15 min, 9 months] | Overflow / underflow guard |

---

## Vocabulary: 200 Farsi Words

Organised into 13 semantic categories (Nation, 2001 — optimal group sizing for working memory):

| Category | Count | Category | Count |
|---|---|---|---|
| Verbs | 25 | Greetings | 15 |
| Adjectives | 20 | Body | 15 |
| Numbers | 20 | Time | 15 |
| Food & Drink | 20 | Places | 15 |
| Animals | 15 | Family | 10 |
| Colors | 10 | Pronouns | 10 |
| Clothes | 10 | **Total** | **200** |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3 · Flask |
| Database | SQLite (via Python `sqlite3`) |
| Frontend | Vanilla JS · CSS3 |
| Fonts | Vazirmatn (Farsi) · Cormorant Garamond · DM Sans |
| Charts | Chart.js 4.4 |
| Voice | Web Speech API (`fa-IR`) — zero dependencies |

---

## Quick Start

### Requirements
- Python 3.10+
- pip

### Setup

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/farsi-hlr.git
cd farsi-hlr

# 2. Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install flask

# 4. Run the app (seeds DB automatically on first launch)
python app.py
```

Open your browser at **http://localhost:5000**

### Windows shortcut
Double-click `start.bat` — it activates the venv, opens the browser, and starts the server.

---

## Project Structure

```
farsi-hlr/
│
├── app.py              # Flask routes
├── hlr.py              # HLR model: forgetting curve, AdaGrad, scheduling
├── database.py         # SQLite schema + all query helpers
├── seed_words.py       # 200 Farsi words (auto-runs on first launch)
├── requirements.txt
├── start.bat           # Windows one-click launcher
│
├── data/               # SQLite DB lives here (git-ignored)
│
├── static/
│   ├── css/style.css
│   ├── js/study.js     # Flashcard / MCQ / Typing logic + TTS
│   ├── js/progress.js  # Chart.js analytics
│   └── images/         # Persian rug background
│
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── study.html
│   ├── results.html
│   ├── progress.html
│   └── word_list.html
│
└── docs/
    ├── AI.pdf              # Full project report
    └── screenshots/        # UI screenshots
```

---

## Developer Tools

Press the **backtick key `` ` ``** on any study or dashboard page to reveal the dev toolbar:

- **Force mode** — lock all questions to MCQ / Flashcard / Typing for isolated testing
- **Time warp** — shift all timestamps backward (+1d / +3d / +1 week / +30 days) to simulate future review sessions and validate HLR scheduling and progress graphs

---

## Analytics

The Progress page provides three views:

1. **Daily Recall Rate** — line chart of average recall % per calendar day
2. **Half-Life Distribution** — histogram of how many words fall in each retention tier (`<1d` → fragile, up to `30d+` → strong)
3. **Cumulative Words Encountered** — vocabulary growth curve
4. **Category Breakdown table** — per-category: coverage %, average ĥ, retention bar

---

## Report

The full academic report (10 pages, IEEE-style LaTeX) is at [`docs/AI.pdf`](docs/AI.pdf).

It covers: choice of language justification, UI design rationale (HCI citations), word grouping literature, HLR algorithm derivation, analytics design, and proposed improvements — all mapped to the course rubric.

---

## References

- Settles, B. & Meeder, B. (2016). *A Trainable Spaced Repetition Model for Language Learning.* ACL 2016, Berlin.
- Ebbinghaus, H. (1885). *Memory: A Contribution to Experimental Psychology.*
- Duchi, J., Hazan, E. & Singer, Y. (2011). Adaptive subgradient methods. *JMLR*, 12.
- Nation, I.S.P. (2001). *Learning Vocabulary in Another Language.* Cambridge University Press.
- Sweller, J. (1988). Cognitive load during problem solving. *Cognitive Science*, 12(2).

---

## License

MIT License — © 2026 Sudheer Rathore & Anser Abbas, IBA Karachi
