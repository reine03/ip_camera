from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Response
import sqlite3, hashlib, os, datetime, re, cv2
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'ipcam-secret-2024-xyz')

DB = 'ipcam.db'
CAMERA_URL = os.environ.get('CAMERA_URL', '0')  # '0' = webcam, or rtsp://...

# ── DB INIT ──────────────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'viewer',
        created_at TEXT,
        is_active INTEGER DEFAULT 1
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS login_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        ip TEXT,
        status TEXT,
        timestamp TEXT
    )''')
    # Seed demo users
    for uname, pwd, role in [('admin', 'Admin@1234', 'admin'), ('viewer', 'Viewer@1234', 'viewer')]:
        hashed = hashlib.sha256(pwd.encode()).hexdigest()
        try:
            c.execute("INSERT INTO users (username,password,role,created_at) VALUES (?,?,?,?)",
                      (uname, hashed, role, datetime.datetime.now().isoformat()))
        except:
            pass
    conn.commit()
    conn.close()

init_db()

# ── HELPERS ───────────────────────────────────────────────────────────────────

def hash_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()

def log_login(username, ip, status):
    conn = get_db()
    conn.execute("INSERT INTO login_logs (username,ip,status,timestamp) VALUES (?,?,?,?)",
                 (username, ip, status, datetime.datetime.now().isoformat()))
    conn.commit(); conn.close()

def validate_password(pw):
    if len(pw) < 8: return "Password must be at least 8 characters."
    if not re.search(r'[A-Z]', pw): return "Password must contain an uppercase letter."
    if not re.search(r'[0-9]', pw): return "Password must contain a number."
    if not re.search(r'[^A-Za-z0-9]', pw): return "Password must contain a special character."
    return None

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session: return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session: return redirect(url_for('login'))
        if session.get('role') != 'admin':
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated

# ── CAMERA STREAM ─────────────────────────────────────────────────────────────

def gen_frames():
    src = int(CAMERA_URL) if CAMERA_URL.isdigit() else CAMERA_URL
    cap = cv2.VideoCapture(src)
    while True:
        success, frame = cap.read()
        if not success:
            break
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
@login_required
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# ── ROUTES ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return redirect(url_for('dashboard') if 'user' in session else url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        uname = request.form.get('username', '').strip()
        pw = request.form.get('password', '')
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username=? AND is_active=1", (uname,)).fetchone()
        conn.close()
        ip = request.remote_addr
        if user and user['password'] == hash_pw(pw):
            session['user'] = uname
            session['role'] = user['role']
            log_login(uname, ip, 'success')
            return redirect(url_for('dashboard'))
        else:
            log_login(uname, ip, 'failed')
            error = "Invalid credentials or account disabled."
    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    success = None
    if request.method == 'POST':
        uname = request.form.get('username', '').strip()
        pw = request.form.get('password', '')
        pw2 = request.form.get('confirm_password', '')
        if not uname or len(uname) < 3:
            error = "Username must be at least 3 characters."
        elif pw != pw2:
            error = "Passwords do not match."
        else:
            err = validate_password(pw)
            if err:
                error = err
            else:
                try:
                    conn = get_db()
                    conn.execute("INSERT INTO users (username,password,role,created_at) VALUES (?,?,?,?)",
                                 (uname, hash_pw(pw), 'viewer', datetime.datetime.now().isoformat()))
                    conn.commit(); conn.close()
                    success = "Account created! You can now log in."
                except sqlite3.IntegrityError:
                    error = "Username already taken."
    return render_template('register.html', error=error, success=success)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=session['user'], role=session['role'])

@app.route('/admin')
@admin_required
def admin():
    conn = get_db()
    users = conn.execute("SELECT id,username,role,created_at,is_active FROM users ORDER BY id").fetchall()
    logs = conn.execute("SELECT * FROM login_logs ORDER BY id DESC LIMIT 50").fetchall()
    conn.close()
    return render_template('admin.html', users=users, logs=logs, user=session['user'])

@app.route('/admin/toggle/<int:uid>')
@admin_required
def toggle_user(uid):
    conn = get_db()
    u = conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    if u and u['username'] != 'admin':
        new_status = 0 if u['is_active'] else 1
        conn.execute("UPDATE users SET is_active=? WHERE id=?", (new_status, uid))
        conn.commit()
    conn.close()
    return redirect(url_for('admin'))

@app.route('/admin/delete/<int:uid>')
@admin_required
def delete_user(uid):
    conn = get_db()
    u = conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    if u and u['username'] != 'admin':
        conn.execute("DELETE FROM users WHERE id=?", (uid,))
        conn.commit()
    conn.close()
    return redirect(url_for('admin'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/api/status')
@login_required
def api_status():
    return jsonify({'user': session['user'], 'role': session['role'], 'time': datetime.datetime.now().isoformat()})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
