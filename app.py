"""
app.py — Farsi HLR Flask application
"""
import json
import time
import math

from flask import (Flask, render_template, request,
                   jsonify, session, redirect, url_for)

import database as db
import hlr
from seed_words import seed

app = Flask(__name__)
app.secret_key = 'farsi-hlr-secret-2024'


# ── Bootstrap ─────────────────────────────────────────────────────────────────
@app.before_request
def bootstrap():
    db.init_db()


# ── Dashboard ─────────────────────────────────────────────────────────────────
@app.route('/')
def dashboard():
    stats = db.get_dashboard_stats()
    return render_template('dashboard.html', stats=stats)


# ── Study session ─────────────────────────────────────────────────────────────
@app.route('/study')
def study():
    # Developer override: ?force=mcq | flashcard | typing
    force_mode = request.args.get('force', '').lower()
    if force_mode not in ('mcq', 'flashcard', 'typing'):
        force_mode = ''

    due  = db.get_due_words(limit=15)
    need = max(0, 10 - len(due))
    new  = db.get_new_words(limit=need) if need else []
    words = due + new

    # In force-mode, grab a sample of all words so every type is testable
    if force_mode and not words:
        all_w = db.get_all_words()
        import random
        words = random.sample(all_w, min(10, len(all_w)))

    if not words:
        return render_template('dashboard.html',
                               stats=db.get_dashboard_stats(),
                               message="Nothing due right now — great job! 🎉")

    all_words = db.get_all_words()

    return render_template('study.html',
                           words_json=json.dumps(words),
                           all_words_json=json.dumps(all_words),
                           force_mode=force_mode)


# ── Session submission (called by JS at end of study) ─────────────────────────
@app.route('/submit_session', methods=['POST'])
def submit_session():
    data    = request.get_json(silent=True) or {}
    results = data.get('results', [])

    theta, accum = db.get_weights()
    now          = time.time()
    output       = []

    for item in results:
        word_id     = item.get('word_id')
        was_correct = bool(item.get('correct'))

        word = db.get_word_by_id(word_id)
        if not word:
            continue

        # ── Lag time ──────────────────────────────────────────────────────
        last_seen = word['last_seen_ts']
        if last_seen == 0:                     # first ever exposure
            delta = 0.0
        else:
            delta = max((now - last_seen) / 86400.0, 1 / 1440)  # ≥ 1 min

        # ── Update counters ───────────────────────────────────────────────
        n_seen      = word['n_seen']      + 1
        n_correct   = word['n_correct']   + (1 if was_correct else 0)
        n_incorrect = word['n_incorrect'] + (0 if was_correct else 1)

        # ── Feature vector ────────────────────────────────────────────────
        x = hlr.feature_vector(n_seen, n_correct, n_incorrect)

        # ── Recall rate (binary, smoothed for log safety) ─────────────────
        p        = 1.0 if was_correct else 0.0
        p_smooth = 0.9 if was_correct else 0.1   # smoothed for gradient math

        # ── Model predictions ─────────────────────────────────────────────
        h_hat = hlr.estimate_half_life(theta, x)
        p_hat = hlr.recall_probability(delta, h_hat) if delta > 0 else 1.0

        # ── AdaGrad update (only if we have a real lag) ───────────────────
        if delta > 0:
            theta, accum = hlr.adagrad_update(
                theta, accum, x, p_smooth, delta, h_hat, p_hat
            )
            h_hat = hlr.estimate_half_life(theta, x)  # recompute post-update

        # ── Schedule next review ──────────────────────────────────────────
        review_in_days = hlr.days_until_next_review(h_hat)
        next_review_ts = now + review_in_days * 86400.0

        # ── Persist ───────────────────────────────────────────────────────
        db.update_word_stats(word_id, n_seen, n_correct, n_incorrect,
                             now, h_hat, next_review_ts)
        db.insert_review(word_id, now, delta, p, p_hat, h_hat,
                         1 if was_correct else 0)

        output.append({
            'word_id':          word_id,
            'farsi':            word['farsi'],
            'english':          word['english'],
            'transliteration':  word['transliteration'],
            'was_correct':      was_correct,
            'h_hat':            round(h_hat, 2),
            'p_hat':            round(p_hat, 3),
            'review_in_days':   round(review_in_days, 1),
            'q_type':           item.get('q_type', 'flashcard'),
        })

    db.save_weights(theta, accum)
    session['last_results'] = output
    return jsonify({'status': 'ok', 'count': len(output)})


# ── Results ───────────────────────────────────────────────────────────────────
@app.route('/results')
def results():
    last = session.get('last_results', [])
    if not last:
        return redirect(url_for('dashboard'))
    correct = sum(1 for r in last if r['was_correct'])
    return render_template('results.html',
                           results=last,
                           correct=correct,
                           total=len(last))


# ── Progress ──────────────────────────────────────────────────────────────────
@app.route('/progress')
def progress():
    return render_template('progress.html')


@app.route('/api/progress_data')
def api_progress_data():
    return jsonify(db.get_progress_data())


# ── Word list ─────────────────────────────────────────────────────────────────
@app.route('/words')
def word_list():
    words = db.get_all_words()
    return render_template('word_list.html', words=words, now=time.time())


# ── Dev: time warp ────────────────────────────────────────────────────────────
@app.route('/dev/warp', methods=['POST'])
def dev_warp():
    """
    Shift ALL timestamps backward by N days:
      - word_stats.next_review_ts  → makes words due again
      - word_stats.last_seen_ts    → makes lag time realistic
      - reviews.session_ts         → spreads review history on progress graphs

    Without shifting reviews.session_ts the graphs never change because
    every session appears on the same calendar day.
    """
    days    = float(request.json.get('days', 1))
    seconds = days * 86400.0
    conn    = db.get_conn()

    # Shift word scheduling timestamps
    conn.execute('''
        UPDATE word_stats
        SET next_review_ts = next_review_ts - ?,
            last_seen_ts   = CASE WHEN last_seen_ts > 0
                                  THEN last_seen_ts - ?
                                  ELSE 0 END
        WHERE n_seen > 0
    ''', (seconds, seconds))

    # ── KEY FIX: also shift all review history so graphs spread over time ──
    conn.execute('''
        UPDATE reviews
        SET session_ts = session_ts - ?
    ''', (seconds,))

    conn.commit()

    now = time.time()
    due = conn.execute(
        'SELECT COUNT(*) FROM word_stats WHERE next_review_ts <= ? AND n_seen > 0',
        (now,)
    ).fetchone()[0]
    total_reviews = conn.execute('SELECT COUNT(*) FROM reviews').fetchone()[0]
    conn.close()

    return jsonify({
        'status':        'ok',
        'days_shifted':  days,
        'now_due':       due,
        'reviews_aged':  total_reviews,
    })


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    db.init_db()
    seed()          # seeds DB silently if already populated
    print("\n  🌙  Farsi HLR running at  http://localhost:5000\n")
    app.run(debug=True, port=5000, use_reloader=False)
