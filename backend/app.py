import os, pymysql, hashlib
from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import timedelta

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', 'templates'),
    static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', 'static')
)
app.secret_key = 'supersecretkey'
app.permanent_session_lifetime = timedelta(days=1)

DB_CONFIG = dict(host='127.0.0.1', user='root', password='', database='complainify', port=3306, charset='utf8mb4')

def get_db():
    return pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def gen_ticket():
    return 'CMP-' + os.urandom(2).hex().upper()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit-complaint', methods=['GET', 'POST'])
def submit_complaint():
    if request.method == 'POST':
        conn = get_db(); cur = conn.cursor()
        try:
            tid = gen_ticket()
            uid = session.get('user_id')
            cur.execute("INSERT INTO complaints (ticket_id,user_id,fullname,email,category,priority,subject,description) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                (tid, uid, request.form.get('fullname'), request.form.get('email'), request.form.get('category'),
                 request.form.get('priority','Medium'), request.form.get('subject'), request.form.get('description')))
            conn.commit()
            flash(f'Complaint submitted! Ticket: {tid}', 'success')
        finally:
            cur.close(); conn.close()
        return redirect(url_for('track_complaint'))
    return render_template('submit_complaint.html')

@app.route('/track', methods=['GET', 'POST'])
def track_complaint():
    result = None
    if request.method == 'POST':
        tid = request.form.get('ticket_id')
        conn = get_db(); cur = conn.cursor()
        cur.execute("SELECT ticket_id,status,priority,category,date_format(created_at,'%%d %%b %%Y') date FROM complaints WHERE ticket_id=%s", (tid,))
        result = cur.fetchone()
        cur.close(); conn.close()
    return render_template('track.html', result=result)

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        flash('OTP has been sent to your phone number.', 'success')
    return render_template('forgot_password.html')

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        flash('Your password has been reset successfully. Please login.', 'success')
        return redirect(url_for('student_login'))
    return render_template('reset_password.html')

@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if 'user_id' in session and session.get('role') == 'student':
        return redirect(url_for('student_dashboard'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = hash_pw(request.form.get('password',''))
        conn = get_db(); cur = conn.cursor()
        cur.execute("SELECT id,fullname,email,password,role FROM users WHERE email=%s AND role='student'", (email,))
        user = cur.fetchone()
        if user:
            if user['password'] == password:
                session.permanent = True
                session['user_id'] = user['id']
                session['fullname'] = user['fullname']
                session['email'] = user['email']
                session['role'] = 'student'
                cur.close(); conn.close()
                return redirect(url_for('student_dashboard'))
            flash('Incorrect password. Please try again.', 'error')
        else:
            flash('Account not found with this email.', 'error')
        cur.close(); conn.close()
    return render_template('student/login.html')

@app.route('/student/register', methods=['GET', 'POST'])
def student_register():
    if request.method == 'POST':
        fullname = request.form.get('fullname', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        pw = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        if not fullname or not email or not phone or not pw:
            flash('All fields are required.', 'error')
            return render_template('student/register.html')
        if '@' not in email:
            flash('Please enter a valid email address.', 'error')
            return render_template('student/register.html')
        if len(pw) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return render_template('student/register.html')
        if pw != confirm:
            flash('Passwords do not match.', 'error')
            return render_template('student/register.html')

        conn = get_db(); cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users (fullname,email,phone,plain_password,password,role) VALUES (%s,%s,%s,%s,%s,'student')",
                (fullname, email, phone, pw, hash_pw(pw)))
            conn.commit()
            flash('Registration successful! Please login.', 'success')
        except pymysql.err.IntegrityError:
            flash('Email already registered.', 'error')
        finally:
            cur.close(); conn.close()
        return redirect(url_for('student_login'))
    return render_template('student/register.html')

@app.route('/student/dashboard')
def student_dashboard():
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('student_login'))
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT ticket_id,category,priority,status,date_format(created_at,'%%d %%b %%Y') date FROM complaints WHERE user_id=%s", (session['user_id'],))
    complaints = cur.fetchall()
    cur.close(); conn.close()
    total = len(complaints)
    resolved = sum(1 for c in complaints if c['status'] == 'Resolved')
    in_progress = sum(1 for c in complaints if c['status'] == 'In Progress')
    pending = total - resolved - in_progress
    return render_template('student/dashboard.html', student_name=session.get('fullname','Student').split('@')[0],
        total=total, resolved=resolved, in_progress=in_progress, pending=pending, complaints=complaints)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if 'user_id' in session and session.get('role') == 'admin':
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = hash_pw(request.form.get('password',''))
        conn = get_db(); cur = conn.cursor()
        cur.execute("SELECT id,fullname,email,password,role FROM users WHERE email=%s AND role='admin'", (email,))
        user = cur.fetchone()
        if user:
            if user['password'] == password:
                session.permanent = True
                session['user_id'] = user['id']
                session['fullname'] = user['fullname']
                session['email'] = user['email']
                session['role'] = 'admin'
                cur.close(); conn.close()
                return redirect(url_for('admin_dashboard'))
            flash('Incorrect password. Please try again.', 'error')
        else:
            flash('Admin account not found with this email.', 'error')
        cur.close(); conn.close()
    return render_template('admin/login.html')

@app.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        fullname = request.form.get('fullname', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        pw = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        if not fullname or not email or not phone or not pw:
            flash('All fields are required.', 'error')
            return render_template('admin/register.html')
        if '@' not in email:
            flash('Please enter a valid email address.', 'error')
            return render_template('admin/register.html')
        if len(pw) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return render_template('admin/register.html')
        if pw != confirm:
            flash('Passwords do not match.', 'error')
            return render_template('admin/register.html')

        conn = get_db(); cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users (fullname,email,phone,plain_password,password,role) VALUES (%s,%s,%s,%s,%s,'admin')",
                (fullname, email, phone, pw, hash_pw(pw)))
            conn.commit()
            flash('Admin registration successful! Please login.', 'success')
        except pymysql.err.IntegrityError:
            flash('Email already registered.', 'error')
        finally:
            cur.close(); conn.close()
        return redirect(url_for('admin_login'))
    return render_template('admin/register.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT ticket_id,fullname student,category,priority,status,date_format(created_at,'%%d %%b %%Y') date FROM complaints ORDER BY created_at DESC")
    complaints = cur.fetchall()
    cur.close(); conn.close()
    total = len(complaints)
    resolved = sum(1 for c in complaints if c['status'] == 'Resolved')
    in_progress = sum(1 for c in complaints if c['status'] == 'In Progress')
    pending = total - resolved - in_progress
    return render_template('admin/dashboard.html', total=total, resolved=resolved, in_progress=in_progress,
        pending=pending, complaints=complaints, admin_name=session.get('fullname','Admin'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
