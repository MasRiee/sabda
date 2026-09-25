"""
server_gamifikasi.py — Web dashboard IoT (Versi Gamifikasi) untuk pendamping SABDA
"""

from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import datetime

app = Flask(__name__, template_folder='.')
app.config['SECRET_KEY'] = 'sabda-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# ── State real-time (prediksi terakhir) ────────────────────────────
latest_data = {
    "status": "idle",
    "target_word": "-",
    "predicted_word": "-",
    "confidence": 0,
    "correct": None,
    "timestamp": "-",
    # Variabel Gamifikasi
    "artikulasi": 0,
    "intonasi": 0,
    "bibir": 0,
    "total_nilai": 0,
    "mode": "-"
}

# ── Session tracking ───────────────────────────────────────────────
session_stats = {
    "total_attempts": 0,
    "total_correct": 0,
    "word_stats": {},      # {kata: {attempts, correct}}
    "history": [],         # [{time, target, predicted, correct, confidence, total_nilai, mode}]
    "daily_stats": {},     # {tanggal: {attempts, correct}}
}

def _update_session(data: dict):
    """Update statistik session setiap ada prediksi baru."""
    word = data.get("target_word", "-")
    correct = data.get("correct", False)
    confidence = data.get("confidence", 0)
    now = datetime.datetime.now()
    today = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    # Total
    session_stats["total_attempts"] += 1
    if correct:
        session_stats["total_correct"] += 1

    # Per kata
    if word not in session_stats["word_stats"]:
        session_stats["word_stats"][word] = {"attempts": 0, "correct": 0}
    session_stats["word_stats"][word]["attempts"] += 1
    if correct:
        session_stats["word_stats"][word]["correct"] += 1

    # Harian
    if today not in session_stats["daily_stats"]:
        session_stats["daily_stats"][today] = {"attempts": 0, "correct": 0}
    session_stats["daily_stats"][today]["attempts"] += 1
    if correct:
        session_stats["daily_stats"][today]["correct"] += 1

    # Riwayat (max 50 entri) beserta nilai gamifikasi
    session_stats["history"].insert(0, {
        "time": time_str,
        "target": word,
        "predicted": data.get("predicted_word", "-"),
        "correct": correct,
        "confidence": round(confidence * 100),
        "total_nilai": data.get("total_nilai", 0),
        "mode": data.get("mode", "Latihan")
    })
    if len(session_stats["history"]) > 50:
        session_stats["history"].pop()

def broadcast_update(data: dict):
    """Dipanggil dari AppController atau MainWindow saat ada prediksi baru."""
    latest_data.update(data)
    _update_session(data)
    socketio.emit('update', {
        "latest": latest_data,
        "stats": session_stats
    })

def inject_dummy_history():
    """
    Pre-fill data harian untuk keperluan demo video.
    Simulasikan 7 hari terakhir + beberapa prediksi hari ini.
    """
    import random
    today = datetime.datetime.now()
    words = ['maaf', 'tolong', 'halo', 'permisi', 'iya', 'engga', 'makasih', 'aku']

    # ── Data 7 hari terakhir ───────────────────────────────────────
    for days_ago in range(6, 0, -1):
        date = (today - datetime.timedelta(days=days_ago)).strftime("%Y-%m-%d")
        base_rate = 0.40 + (days_ago * -0.04)  
        attempts = random.randint(15, 30)
        correct  = int(attempts * (base_rate + random.uniform(-0.05, 0.05)))
        correct  = max(0, min(correct, attempts))

        session_stats["daily_stats"][date] = {
            "attempts": attempts,
            "correct":  correct
        }
        session_stats["total_attempts"] += attempts
        session_stats["total_correct"]  += correct

        for _ in range(attempts):
            word = random.choice(words)
            is_correct = random.random() < base_rate
            if word not in session_stats["word_stats"]:
                session_stats["word_stats"][word] = {"attempts": 0, "correct": 0}
            session_stats["word_stats"][word]["attempts"] += 1
            if is_correct:
                session_stats["word_stats"][word]["correct"] += 1

    # ── Data hari ini (beberapa prediksi awal) ────────────────────
    today_str = today.strftime("%Y-%m-%d")
    session_stats["daily_stats"][today_str] = {"attempts": 0, "correct": 0}

    sample_today = [
        ("halo",    "halo",    True,  0.91),
        ("maaf",    "maaf",    True,  0.87),
        ("tolong",  "engga",   False, 0.52),
        ("permisi", "permisi", True,  0.78),
        ("iya",     "iya",     True,  0.94),
        ("engga",   "tolong",  False, 0.44),
    ]

    for target, predicted, correct, conf in sample_today:
        _update_session({
            "target_word":    target,
            "predicted_word": predicted,
            "correct":        correct,
            "confidence":     conf,
            "total_nilai":    random.randint(60, 95) if correct else random.randint(40, 59),
            "mode":           random.choice(["Latihan", "Ujian"])
        })
        if session_stats["history"]:
            offset = random.randint(1, 59)
            session_stats["history"][0]["time"] = (
                today - datetime.timedelta(minutes=offset)
            ).strftime("%H:%M:%S")

inject_dummy_history()

@app.route('/')
def index():
    # Pastikan merender file HTML gamifikasi
    return render_template('index_gamifikasi.html')

@app.route('/api/stats')
def get_stats():
    return jsonify({"latest": latest_data, "stats": session_stats})

@socketio.on('connect')
def on_connect():
    emit('update', {"latest": latest_data, "stats": session_stats})

@socketio.on('reset_session')
def on_reset():
    session_stats["total_attempts"] = 0
    session_stats["total_correct"] = 0
    session_stats["word_stats"] = {}
    session_stats["history"] = []
    socketio.emit('update', {"latest": latest_data, "stats": session_stats})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)