import os
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__, template_folder='.')
app.secret_key = os.environ.get('SECRET_KEY', 'change-me')

USERS = {
    'admin': {'password': 'Admin@1234', 'role': 'admin'},
    'viewer': {'password': 'Viewer@1234', 'role': 'viewer'},
}

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = USERS.get(username)
        if user and user['password'] == password:
            session['username'] = username
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        error = 'Invalid credentials'
    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/admin')
def admin():
    if session.get('role') != 'admin':
        return redirect(url_for('dashboard'))
    return render_template('admin.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
