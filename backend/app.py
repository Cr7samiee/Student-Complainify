import os, hashlib
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
app.secret_key = os.urandom(24).hex()

# Mock in-memory storage (no DB needed for now)
users = {}
complaints = {}
ticket_counter = 1000

def hash_pw(password):
    return hashlib.sha256(password.encode()).hexdigest()

def gen_ticket():
    global ticket_counter
    ticket_counter += 1
    return f"CMP-{ticket_counter}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = hash_pw(request.form.get('password', ''))
        user = users.get(email)
        if user and user['password'] == password and user['role'] == 'student':
            session['user'] = {'email': email, 'name': user['name'], 'role': 'student'}
            return redirect(url_for('student_dashboard'))
        return render_template('student/login.html', error='Invalid credentials')
    return render_template('student/login.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = hash_pw(request.form.get('password', ''))
        user = users.get(email)
        if user and user['password'] == password and user['role'] == 'admin':
            session['user'] = {'email': email, 'name': user['name'], 'role': 'admin'}
            return redirect(url_for('admin_dashboard'))
        return render_template('admin/login.html', error='Invalid credentials')
    return render_template('admin/login.html')

@app.route('/student/register', methods=['GET', 'POST'])
def student_register():
    if request.method == 'POST':
        email = request.form.get('email')
        if email in users:
            return render_template('student/register.html', error='Email already registered')
        users[email] = {
            'name': request.form.get('fullname'),
            'email': email,
            'phone': request.form.get('phone'),
            'password': hash_pw(request.form.get('password', '')),
            'role': 'student'
        }
        session['user'] = {'email': email, 'name': users[email]['name'], 'role': 'student'}
        return redirect(url_for('student_dashboard'))
    return render_template('student/register.html')

@app.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        email = request.form.get('email')
        if email in users:
            return render_template('admin/register.html', error='Email already registered')
        users[email] = {
            'name': request.form.get('fullname'),
            'email': email,
            'phone': request.form.get('phone'),
            'password': hash_pw(request.form.get('password', '')),
            'role': 'admin'
        }
        session['user'] = {'email': email, 'name': users[email]['name'], 'role': 'admin'}
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/register.html')

@app.route('/submit', methods=['GET', 'POST'])
def submit_complaint():
    if request.method == 'POST':
        ticket = gen_ticket()
        complaints[ticket] = {
            'ticket': ticket,
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'category': request.form.get('category'),
            'priority': request.form.get('priority'),
            'subject': request.form.get('subject'),
            'description': request.form.get('description'),
            'status': 'Submitted'
        }
        return render_template('submit_complaint.html', success=f'Complaint submitted! Ticket: {ticket}')
    return render_template('submit_complaint.html')

@app.route('/track', methods=['GET', 'POST'])
def track():
    result = None
    if request.method == 'POST':
        ticket = request.form.get('ticket', '').strip().upper()
        result = complaints.get(ticket)
        if not result:
            result = {'error': 'No complaint found with that ticket number'}
    return render_template('track.html', result=result)

@app.route('/student/dashboard')
def student_dashboard():
    if 'user' not in session or session['user']['role'] != 'student':
        return redirect(url_for('student_login'))
    user_complaints = [c for c in complaints.values() if c['email'] == session['user']['email']]
    return render_template('student/dashboard.html', user=session['user'], complaints=user_complaints)

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user' not in session or session['user']['role'] != 'admin':
        return redirect(url_for('admin_login'))
    return render_template('admin/dashboard.html', user=session['user'], complaints=list(complaints.values()))

@app.route('/forgot-password')
def forgot_password():
    return render_template('forgot_password.html')

@app.route('/reset-password')
def reset_password():
    return render_template('reset_password.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
