import os, csv, io, json, pymysql, hashlib, smtplib, ssl, sys, random, uuid
from email.message import EmailMessage
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from datetime import timedelta, datetime
from werkzeug.utils import secure_filename

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'train'))
from classifier import auto_categorize, categorize
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'train'))
from sentiment import analyze_sentiment, sentiment_priority_boost

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', 'templates'),
    static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', 'static')
)
app.secret_key = 'supersecretkey'
app.permanent_session_lifetime = timedelta(days=1)

SMTP_CONFIG = dict(
    host=os.environ.get('SMTP_HOST', 'smtp.gmail.com'),
    port=int(os.environ.get('SMTP_PORT', 587)),
    user=os.environ.get('SMTP_USER', 'brooskings661@gmail.com'),
    password=os.environ.get('SMTP_PASS', 'vksq mrdy qnqd zbut')
)

DB_CONFIG = dict(host='127.0.0.1', user='root', password='', database='complainify', port=3306, charset='utf8mb4')
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'svg', 'png', 'jpg', 'jpeg', 'doc', 'docx', 'xls', 'xlsx', 'csv', 'txt', 'zip'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db():
    return pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def gen_ticket():
    return 'CMP-' + os.urandom(2).hex().upper()

CATEGORIES = ['Academics', 'Hostels', 'IT Support', 'Infrastructure', 'Financial Services',
              'Administrative', 'Security', 'Maintenance', 'Transport', 'Canteen', 'Library', 'Other']

def create_notification(user_id, message, link=None):
    try:
        conn = get_db(); cur = conn.cursor()
        cur.execute("INSERT INTO notifications (user_id, message, link) VALUES (%s, %s, %s)", (user_id, message, link))
        conn.commit()
        cur.close(); conn.close()
    except: pass

def log_action(user_id, action, target_type=None, target_id=None, details=None):
    try:
        conn = get_db(); cur = conn.cursor()
        cur.execute("INSERT INTO audit_logs (user_id, action, target_type, target_id, details) VALUES (%s, %s, %s, %s, %s)",
            (user_id, action, target_type, target_id, details))
        conn.commit()
        cur.close(); conn.close()
    except: pass

def send_email_notification(to_email, subject, body):
    if not SMTP_CONFIG['user'] or not SMTP_CONFIG['password']:
        print(f"[EMAIL SKIPPED] No SMTP config: to={to_email}, subject={subject}")
        return False
    try:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = SMTP_CONFIG['user']
        msg['To'] = to_email
        msg.set_content(body)
        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_CONFIG['host'], SMTP_CONFIG['port']) as server:
            server.starttls(context=context)
            server.login(SMTP_CONFIG['user'], SMTP_CONFIG['password'])
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return False

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
            description = request.form.get('description', '')
            subject = request.form.get('subject', '')
            full_text = subject + ' ' + description
            manual_cat = request.form.get('category', '').strip()

            if manual_cat and manual_cat != 'auto':
                category = manual_cat
                confidence = 1.0
                tier = 'auto'
            else:
                result = categorize(full_text)
                category = result['category']
                confidence = result['confidence']
                tier = result['tier']
                if tier == 'auto':
                    flash(f'AI auto-categorized: {category} ({confidence*100:.1f}%)', 'success')
                elif tier == 'suggest':
                    flash(f'AI suggests: {category} ({confidence*100:.1f}%) — please review', 'warning')
                else:
                    flash(f'Unclear complaint ({confidence*100:.1f}%) — category set to Other', 'warning')
                    category = 'Other'

            sentiment_result = analyze_sentiment(full_text)
            sentiment = sentiment_result['label']
            sentiment_score = sentiment_result['score']

            priority = request.form.get('priority', 'Medium')
            boosted = sentiment_priority_boost(sentiment, priority)
            if boosted != priority:
                flash(f'Priority auto-boosted from {priority} to {boosted} due to {sentiment_result["sub_label"]} tone', 'warning')
                priority = boosted

            student_attachment = request.files.get('student_attachment')
            student_attachment_name = None
            if student_attachment and student_attachment.filename and '.' in student_attachment.filename:
                ext = student_attachment.filename.rsplit('.', 1)[1].lower()
                if ext in ALLOWED_EXTENSIONS:
                    unique_name = f"{tid}_{uuid.uuid4().hex[:8]}.{ext}"
                    student_attachment.save(os.path.join(UPLOAD_FOLDER, unique_name))
                    student_attachment_name = unique_name

            cur.execute("""INSERT INTO complaints
                (ticket_id,user_id,fullname,email,category,priority,subject,description,sentiment,sentiment_score,student_attachment)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (tid, uid, request.form.get('fullname'), request.form.get('email'),
                 category, priority, subject, description, sentiment, sentiment_score, student_attachment_name))
            conn.commit()

            conn2 = get_db(); cur2 = conn2.cursor()
            cur2.execute("SELECT id FROM users WHERE role='admin'")
            for admin in cur2.fetchall():
                create_notification(admin['id'], f'New complaint #{tid} ({category})', url_for('admin_complaint_detail', ticket_id=tid))
            cur2.close(); conn2.close()
            log_action(uid, 'submit_complaint', 'complaint', tid, f'Category: {category}, Priority: {priority}')

            if SMTP_CONFIG['user']:
                student_email = request.form.get('email')
                if student_email:
                    body = f"""Dear Student,

Your complaint (Ticket: {tid}) has been received successfully.

Category: {category}
Subject: {subject}
Status: Pending

We will review and assign it shortly.

Regards,
Complainify Team"""
                    send_email_notification(student_email,
                        f'Complaint Received: {tid}', body)
                    cur.execute("UPDATE complaints SET email_sent=1 WHERE ticket_id=%s", (tid,))
                    conn.commit()

            flash(f'Complaint submitted! Ticket: {tid} | Category: {category}', 'success')
        finally:
            cur.close(); conn.close()
        return redirect(url_for('track_complaint'))
    return render_template('submit_complaint.html', categories=CATEGORIES)

@app.route('/track', methods=['GET', 'POST'])
def track_complaint():
    result = None
    if request.method == 'POST':
        tid = request.form.get('ticket_id')
        conn = get_db(); cur = conn.cursor()
        cur.execute("""SELECT ticket_id,status,priority,category,subject,
            date_format(created_at,'%%d %%b %%Y') date,
            assigned_to,admin_notes,validated
            FROM complaints WHERE ticket_id=%s""", (tid,))
        result = cur.fetchone()
        cur.close(); conn.close()
    return render_template('track.html', result=result)

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        conn = get_db(); cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE email=%s", (email,))
        user = cur.fetchone()
        if not user:
            flash('No account found with this email.', 'error')
            cur.close(); conn.close()
            return render_template('forgot_password.html')
        otp = str(random.randint(100000, 999999))
        expires = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cur.execute("INSERT INTO otps (email, otp, expires_at) VALUES (%s, %s, DATE_ADD(NOW(), INTERVAL 10 MINUTE))",
            (email, otp))
        conn.commit()
        sent = False
        if SMTP_CONFIG['user'] and SMTP_CONFIG['password']:
            sent = send_email_notification(email, f'Your OTP for Complainify Password Reset',
                f'Your OTP is: {otp}\n\nThis code expires in 10 minutes.\n\nIf you did not request this, ignore this email.')
        cur.close(); conn.close()
        if sent:
            flash(f'OTP sent to {email}. Check your inbox.', 'success')
        else:
            flash(f'OTP: {otp} (Email not configured — use this code)', 'info')
        session['reset_email'] = email
        return redirect(url_for('reset_password'))
    return render_template('forgot_password.html')

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    email = session.get('reset_email')
    if not email:
        flash('Please request an OTP first.', 'error')
        return redirect(url_for('forgot_password'))
    if request.method == 'POST':
        otp = request.form.get('otp', '').strip()
        new_pw = request.form.get('new_password', '')
        confirm = request.form.get('confirm_password', '')
        if len(new_pw) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return render_template('reset_password.html')
        if new_pw != confirm:
            flash('Passwords do not match.', 'error')
            return render_template('reset_password.html')
        conn = get_db(); cur = conn.cursor()
        cur.execute("SELECT id FROM otps WHERE email=%s AND otp=%s AND used=0 AND expires_at > NOW() ORDER BY id DESC LIMIT 1",
            (email, otp))
        record = cur.fetchone()
        if not record:
            flash('Invalid or expired OTP. Please request a new one.', 'error')
            cur.close(); conn.close()
            return render_template('reset_password.html')
        cur.execute("UPDATE users SET password=%s, plain_password=%s WHERE email=%s",
            (hash_pw(new_pw), new_pw, email))
        cur.execute("UPDATE otps SET used=1 WHERE email=%s AND otp=%s", (email, otp))
        conn.commit()
        cur.close(); conn.close()
        session.pop('reset_email', None)
        flash('Password reset successful! Please login.', 'success')
        return redirect(url_for('student_login'))
    return render_template('reset_password.html')

def login_required(role=None):
    if 'user_id' not in session:
        return False
    if role and session.get('role') != role:
        return False
    return True

# ── STUDENT ROUTES ──

@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if 'user_id' in session and session.get('role') == 'student':
        return redirect(url_for('student_dashboard'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = hash_pw(request.form.get('password', ''))
        conn = get_db(); cur = conn.cursor()
        cur.execute("SELECT id,fullname,email,password,role,phone FROM users WHERE email=%s AND role='student'", (email,))
        user = cur.fetchone()
        if user:
            if user['password'] == password:
                session.permanent = True
                session['user_id'] = user['id']
                session['fullname'] = user['fullname']
                session['email'] = user['email']
                session['phone'] = user.get('phone', '')
                session['role'] = 'student'
                cur.close(); conn.close()
                log_action(user['id'], 'login', 'session', '', 'Student login')
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
    if not login_required('student'):
        return redirect(url_for('student_login'))
    conn = get_db(); cur = conn.cursor()
    cur.execute("""SELECT ticket_id,category,priority,status,subject,sentiment,
        date_format(created_at,'%%d %%b %%Y') date,
        assigned_to,validated
        FROM complaints WHERE user_id=%s ORDER BY created_at DESC""", (session['user_id'],))
    complaints = cur.fetchall()
    cur.close(); conn.close()
    total = len(complaints)
    resolved = sum(1 for c in complaints if c['status'] == 'Resolved')
    in_progress = sum(1 for c in complaints if c['status'] == 'In Progress')
    pending = total - resolved - in_progress

    cur.execute("""SELECT category, COUNT(*) cnt FROM complaints WHERE user_id=%s GROUP BY category ORDER BY cnt DESC""", (session['user_id'],))
    cat_rows = cur.fetchall()
    student_cat_labels = [r['category'] for r in cat_rows]
    student_cat_values = [r['cnt'] for r in cat_rows]

    cur.execute("""SELECT DATE_FORMAT(created_at, '%%Y-%%m') month, COUNT(*) cnt FROM complaints WHERE user_id=%s GROUP BY month ORDER BY month""", (session['user_id'],))
    trend_rows = cur.fetchall()
    trend_labels = [r['month'] for r in trend_rows]
    trend_values = [r['cnt'] for r in trend_rows]

    return render_template('student/dashboard.html',
        student_name=session.get('fullname', 'Student'),
        total=total, resolved=resolved, in_progress=in_progress, pending=pending, complaints=complaints,
        student_cat_labels=student_cat_labels, student_cat_values=student_cat_values,
        trend_labels=trend_labels, trend_values=trend_values)

@app.route('/student/complaint/<ticket_id>')
def student_complaint_detail(ticket_id):
    if not login_required('student'):
        return redirect(url_for('student_login'))
    conn = get_db(); cur = conn.cursor()
    cur.execute("""SELECT *,
        date_format(created_at,'%%d %%b %%Y %%h:%%i %%p') created,
        date_format(assigned_at,'%%d %%b %%Y %%h:%%i %%p') assigned_date,
        date_format(resolved_at,'%%d %%b %%Y %%h:%%i %%p') resolved_date
        FROM complaints WHERE ticket_id=%s AND user_id=%s""", (ticket_id, session['user_id']))
    complaint = cur.fetchone()
    cur.close(); conn.close()
    if not complaint:
        flash('Complaint not found.', 'error')
        return redirect(url_for('student_dashboard'))
    cur.execute("""SELECT complaint_comments.*, users.fullname, users.role FROM complaint_comments
        JOIN users ON complaint_comments.user_id=users.id
        WHERE complaint_id=%s ORDER BY complaint_comments.created_at ASC""", (complaint['id'],))
    comments = cur.fetchall()
    cur.close(); conn.close()
    return render_template('student/complaint_detail.html', c=complaint, comments=comments,
        student_name=session.get('fullname', 'Student'))

@app.route('/student/settings', methods=['GET', 'POST'])
def student_settings():
    if not login_required('student'):
        return redirect(url_for('student_login'))
    conn = get_db(); cur = conn.cursor()
    if request.method == 'POST':
        action = request.form.get('action', '')
        if action == 'profile':
            fullname = request.form.get('fullname', '').strip()
            phone = request.form.get('phone', '').strip()
            if fullname:
                cur.execute("UPDATE users SET fullname=%s, phone=%s WHERE id=%s",
                    (fullname, phone, session['user_id']))
                conn.commit()
                session['fullname'] = fullname
                session['phone'] = phone
                flash('Profile updated!', 'success')
        elif action == 'password':
            current = hash_pw(request.form.get('current_password', ''))
            new_pw = request.form.get('new_password', '')
            confirm = request.form.get('confirm_password', '')
            cur.execute("SELECT password FROM users WHERE id=%s", (session['user_id'],))
            user = cur.fetchone()
            if user and user['password'] != current:
                flash('Current password is incorrect.', 'error')
            elif len(new_pw) < 6:
                flash('New password must be at least 6 characters.', 'error')
            elif new_pw != confirm:
                flash('Passwords do not match.', 'error')
            else:
                cur.execute("UPDATE users SET password=%s, plain_password=%s WHERE id=%s",
                    (hash_pw(new_pw), new_pw, session['user_id']))
                conn.commit()
                flash('Password changed!', 'success')
    cur.execute("SELECT fullname,email,phone FROM users WHERE id=%s", (session['user_id'],))
    user = cur.fetchone()
    cur.close(); conn.close()
    return render_template('student/settings.html', user=user,
        student_name=session.get('fullname', 'Student'))

# ── ADMIN ROUTES ──

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if 'user_id' in session and session.get('role') == 'admin':
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = hash_pw(request.form.get('password', ''))
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
                log_action(user['id'], 'login', 'session', '', 'Admin login')
                return redirect(url_for('admin_dashboard'))
            flash('Incorrect password.', 'error')
        else:
            flash('Admin account not found.', 'error')
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
            flash('Valid email required.', 'error')
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
    if not login_required('admin'):
        return redirect(url_for('admin_login'))
    conn = get_db(); cur = conn.cursor()
    cur.execute("""SELECT ticket_id,fullname student,category,priority,status,subject,sentiment,
        date_format(created_at,'%%d %%b %%Y') date,
        assigned_to,validated
        FROM complaints ORDER BY created_at DESC""")
    complaints = cur.fetchall()
    total = len(complaints)
    resolved = sum(1 for c in complaints if c['status'] == 'Resolved')
    in_progress = sum(1 for c in complaints if c['status'] == 'In Progress')
    pending = total - resolved - in_progress

    cur.execute("SELECT COUNT(*) cnt FROM complaints WHERE status='Resolved' AND resolved_at IS NOT NULL AND TIMESTAMPDIFF(HOUR, created_at, resolved_at) IS NOT NULL")
    resolved_cnt_row = cur.fetchone()
    resolved_cnt = resolved_cnt_row['cnt'] if resolved_cnt_row else 0
    cur.execute("SELECT COALESCE(AVG(TIMESTAMPDIFF(HOUR, created_at, resolved_at)), 0) avg_hrs FROM complaints WHERE status='Resolved' AND resolved_at IS NOT NULL")
    avg_row = cur.fetchone()
    avg_resolution = round(float(avg_row['avg_hrs'])) if avg_row else 0

    cur.execute("SELECT COUNT(*) cnt FROM complaints WHERE priority='High' AND status!='Resolved'")
    critical_row = cur.fetchone()
    critical = critical_row['cnt'] if critical_row else 0

    cur.execute("""SELECT category, COUNT(*) cnt FROM complaints GROUP BY category ORDER BY cnt DESC""")
    cat_rows = cur.fetchall()
    cat_labels = [r['category'] for r in cat_rows]
    cat_values = [r['cnt'] for r in cat_rows]
    cat_total = sum(cat_values) or 1
    cat_pcts = [round(v / cat_total * 100) for v in cat_values]

    cur.execute("""SELECT sentiment, COUNT(*) cnt FROM complaints GROUP BY sentiment""")
    sent_rows = cur.fetchall()
    sent_map = {r['sentiment']: r['cnt'] for r in sent_rows}
    sent_pos = sent_map.get('Positive', 0)
    sent_neg = sent_map.get('Negative', 0)
    sent_neu = sent_map.get('Neutral', 0)

    cur.close(); conn.close()
    return render_template('admin/dashboard.html', total=total, resolved=resolved,
        in_progress=in_progress, pending=pending, critical=critical,
        avg_resolution=avg_resolution,
        cat_labels=cat_labels, cat_values=cat_values, cat_pcts=cat_pcts,
        sent_pos=sent_pos, sent_neg=sent_neg, sent_neu=sent_neu,
        complaints=complaints,
        admin_name=session.get('fullname', 'Admin'))

@app.route('/admin/complaints')
def admin_complaints():
    if not login_required('admin'):
        return redirect(url_for('admin_login'))
    conn = get_db(); cur = conn.cursor()
    status_filter = request.args.get('status', '')
    category_filter = request.args.get('category', '')
    priority_filter = request.args.get('priority', '')
    sentiment_filter = request.args.get('sentiment', '')
    page = int(request.args.get('page', 1))
    per_page = 20
    offset = (page - 1) * per_page
    base_query = "FROM complaints WHERE 1=1"
    params = []
    if status_filter:
        base_query += " AND status=%s"
        params.append(status_filter)
    if category_filter:
        base_query += " AND category=%s"
        params.append(category_filter)
    if priority_filter:
        base_query += " AND priority=%s"
        params.append(priority_filter)
    if sentiment_filter:
        base_query += " AND sentiment=%s"
        params.append(sentiment_filter)
    cur.execute(f"SELECT COUNT(*) cnt {base_query}", params)
    total_row = cur.fetchone()
    total_count = total_row['cnt'] if total_row else 0
    total_pages = max(1, (total_count + per_page - 1) // per_page)
    query = f"""SELECT ticket_id,fullname student,category,priority,status,subject,sentiment,
        date_format(created_at,'%%d %%b %%Y') date, assigned_to, validated
        {base_query} ORDER BY created_at DESC LIMIT %s OFFSET %s"""
    cur.execute(query, params + [per_page, offset])
    complaints = cur.fetchall()
    cur.close(); conn.close()
    return render_template('admin/complaints_list.html', complaints=complaints,
        admin_name=session.get('fullname', 'Admin'),
        status_filter=status_filter, category_filter=category_filter,
        priority_filter=priority_filter, sentiment_filter=sentiment_filter,
        page=page, total_pages=total_pages, total_count=total_count,
        categories=[c for c in CATEGORIES if c != 'Other'])

@app.route('/admin/complaint/<ticket_id>')
def admin_complaint_detail(ticket_id):
    if not login_required('admin'):
        return redirect(url_for('admin_login'))
    conn = get_db(); cur = conn.cursor()
    cur.execute("""SELECT *,
        date_format(created_at,'%%d %%b %%Y %%h:%%i %%p') created,
        date_format(assigned_at,'%%d %%b %%Y %%h:%%i %%p') assigned_date,
        date_format(resolved_at,'%%d %%b %%Y %%h:%%i %%p') resolved_date
        FROM complaints WHERE ticket_id=%s""", (ticket_id,))
    complaint = cur.fetchone()
    cur.close(); conn.close()
    if not complaint:
        flash('Complaint not found.', 'error')
        return redirect(url_for('admin_dashboard'))
    cur.execute("""SELECT complaint_comments.*, users.fullname, users.role FROM complaint_comments
        JOIN users ON complaint_comments.user_id=users.id
        WHERE complaint_id=%s ORDER BY complaint_comments.created_at ASC""", (complaint['id'],))
    comments = cur.fetchall()
    cur.close(); conn.close()
    return render_template('admin/complaint_detail.html', c=complaint, comments=comments,
        admin_name=session.get('fullname', 'Admin'))

@app.route('/admin/assign/<ticket_id>', methods=['POST'])
def admin_assign(ticket_id):
    if not login_required('admin'):
        return jsonify({'error': 'Unauthorized'}), 403
    assigned_to = request.form.get('assigned_to', '').strip()
    conn = get_db(); cur = conn.cursor()
    cur.execute("UPDATE complaints SET assigned_to=%s, assigned_at=NOW(), status='In Progress' WHERE ticket_id=%s",
        (assigned_to, ticket_id))
    conn.commit()
    cur.execute("SELECT email, subject, user_id FROM complaints WHERE ticket_id=%s", (ticket_id,))
    c = cur.fetchone()
    cur.close(); conn.close()
    if c and c['email'] and SMTP_CONFIG['user']:
        send_email_notification(c['email'],
            f'Complaint {ticket_id} - Assigned to {assigned_to}',
            f'Dear Student,\n\nYour complaint ({ticket_id}) has been assigned to {assigned_to}.\n\nWe will resolve it shortly.\n\nRegards,\nComplainify Team')
    if c and c['user_id']:
        create_notification(c['user_id'], f'Your complaint #{ticket_id} was assigned to {assigned_to}', url_for('student_complaint_detail', ticket_id=ticket_id))
    log_action(session['user_id'], 'assign_complaint', 'complaint', ticket_id, f'Assigned to {assigned_to}')
    flash(f'Assigned to {assigned_to}', 'success')
    return redirect(url_for('admin_complaint_detail', ticket_id=ticket_id))

@app.route('/admin/status/<ticket_id>', methods=['POST'])
def admin_update_status(ticket_id):
    if not login_required('admin'):
        return jsonify({'error': 'Unauthorized'}), 403
    status = request.form.get('status', '')
    admin_notes = request.form.get('admin_notes', '')
    valid_statuses = ['Pending', 'In Progress', 'Resolved']
    if status not in valid_statuses:
        flash('Invalid status.', 'error')
        return redirect(url_for('admin_complaint_detail', ticket_id=ticket_id))
    attachment = request.files.get('attachment')
    attachment_name = None
    if attachment and attachment.filename and '.' in attachment.filename:
        ext = attachment.filename.rsplit('.', 1)[1].lower()
        if ext in ALLOWED_EXTENSIONS:
            unique_name = f"{ticket_id}_{uuid.uuid4().hex[:8]}.{ext}"
            attachment.save(os.path.join(UPLOAD_FOLDER, unique_name))
            attachment_name = unique_name
    conn = get_db(); cur = conn.cursor()
    if attachment_name:
        if status == 'Resolved':
            cur.execute("UPDATE complaints SET status=%s, admin_notes=%s, resolved_at=NOW(), attachment=%s WHERE ticket_id=%s",
                (status, admin_notes, attachment_name, ticket_id))
        else:
            cur.execute("UPDATE complaints SET status=%s, admin_notes=%s, attachment=%s WHERE ticket_id=%s",
                (status, admin_notes, attachment_name, ticket_id))
    else:
        if status == 'Resolved':
            cur.execute("UPDATE complaints SET status=%s, admin_notes=%s, resolved_at=NOW() WHERE ticket_id=%s",
                (status, admin_notes, ticket_id))
        else:
            cur.execute("UPDATE complaints SET status=%s, admin_notes=%s WHERE ticket_id=%s",
                (status, admin_notes, ticket_id))
    conn.commit()
    cur.execute("SELECT email, subject, user_id FROM complaints WHERE ticket_id=%s", (ticket_id,))
    c = cur.fetchone()
    cur.close(); conn.close()
    if c and c['email'] and SMTP_CONFIG['user']:
        send_email_notification(c['email'],
            f'Complaint {ticket_id} - Status Updated to {status}',
            f'Dear Student,\n\nYour complaint ({ticket_id}) status has been updated to: {status}.\n\nNotes: {admin_notes or "N/A"}\n\nRegards,\nComplainify Team')
    if c and c['user_id']:
        create_notification(c['user_id'], f'Your complaint #{ticket_id} status: {status}', url_for('student_complaint_detail', ticket_id=ticket_id))
    log_action(session['user_id'], 'update_status', 'complaint', ticket_id, f'Status: {status}')
    flash(f'Status updated to {status}', 'success')
    return redirect(url_for('admin_complaint_detail', ticket_id=ticket_id))

@app.route('/admin/validate/<ticket_id>', methods=['POST'])
def admin_validate(ticket_id):
    if not login_required('admin'):
        return jsonify({'error': 'Unauthorized'}), 403
    conn = get_db(); cur = conn.cursor()
    cur.execute("UPDATE complaints SET validated=1 WHERE ticket_id=%s", (ticket_id,))
    conn.commit()
    cur.execute("SELECT user_id FROM complaints WHERE ticket_id=%s", (ticket_id,))
    c = cur.fetchone()
    cur.close(); conn.close()
    if c and c['user_id']:
        create_notification(c['user_id'], f'Your complaint #{ticket_id} was validated as legitimate', url_for('student_complaint_detail', ticket_id=ticket_id))
    log_action(session['user_id'], 'validate_complaint', 'complaint', ticket_id, '')
    flash('Complaint validated as legitimate.', 'success')
    return redirect(url_for('admin_complaint_detail', ticket_id=ticket_id))

@app.route('/admin/resend-email/<ticket_id>', methods=['POST'])
def admin_resend_email(ticket_id):
    if not login_required('admin'):
        return jsonify({'error': 'Unauthorized'}), 403
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT email, ticket_id, status, subject FROM complaints WHERE ticket_id=%s", (ticket_id,))
    c = cur.fetchone()
    if c and c['email'] and SMTP_CONFIG['user']:
        send_email_notification(c['email'],
            f'Complaint {ticket_id} - Status: {c["status"]}',
            f'Dear Student,\n\nYour complaint ({ticket_id}) is currently: {c["status"]}.\n\nRegards,\nComplainify Team')
        flash('Email resent.', 'success')
    else:
        flash('Email not sent (no recipient or no SMTP config).', 'warning')
    cur.close(); conn.close()
    return redirect(url_for('admin_complaint_detail', ticket_id=ticket_id))

@app.route('/admin/settings', methods=['GET', 'POST'])
def admin_settings():
    if not login_required('admin'):
        return redirect(url_for('admin_login'))
    conn = get_db(); cur = conn.cursor()
    if request.method == 'POST':
        action = request.form.get('action', '')
        if action == 'profile':
            fullname = request.form.get('fullname', '').strip()
            phone = request.form.get('phone', '').strip()
            if fullname:
                cur.execute("UPDATE users SET fullname=%s, phone=%s WHERE id=%s",
                    (fullname, phone, session['user_id']))
                conn.commit()
                session['fullname'] = fullname
                flash('Profile updated!', 'success')
        elif action == 'password':
            current = hash_pw(request.form.get('current_password', ''))
            new_pw = request.form.get('new_password', '')
            confirm = request.form.get('confirm_password', '')
            cur.execute("SELECT password FROM users WHERE id=%s", (session['user_id'],))
            user = cur.fetchone()
            if user and user['password'] != current:
                flash('Current password is incorrect.', 'error')
            elif len(new_pw) < 6:
                flash('New password must be at least 6 characters.', 'error')
            elif new_pw != confirm:
                flash('Passwords do not match.', 'error')
            else:
                cur.execute("UPDATE users SET password=%s, plain_password=%s WHERE id=%s",
                    (hash_pw(new_pw), new_pw, session['user_id']))
                conn.commit()
                flash('Password changed!', 'success')
    cur.execute("SELECT fullname,email,phone FROM users WHERE id=%s", (session['user_id'],))
    user = cur.fetchone()
    cur.close(); conn.close()
    return render_template('admin/settings.html', user=user,
        admin_name=session.get('fullname', 'Admin'))

# ── REPORT & CSV EXPORT ──

@app.route('/admin/report')
def admin_report():
    if not login_required('admin'):
        return redirect(url_for('admin_login'))
    conn = get_db(); cur = conn.cursor()
    cur.execute("""SELECT ticket_id,fullname student,category,priority,status,subject,
        date_format(created_at,'%%d %%b %%Y') date, assigned_to, validated
        FROM complaints ORDER BY created_at DESC""")
    complaints = cur.fetchall()
    total = len(complaints)
    resolved = sum(1 for c in complaints if c['status'] == 'Resolved')
    in_progress = sum(1 for c in complaints if c['status'] == 'In Progress')
    pending = total - resolved - in_progress
    validated = sum(1 for c in complaints if c['validated'])
    cat_counts = {}
    for c in complaints:
        cat_counts[c['category']] = cat_counts.get(c['category'], 0) + 1
    cat_labels = list(cat_counts.keys())
    cat_values = list(cat_counts.values())
    cur.close(); conn.close()

    # Training dataset analysis
    train_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'TrainDataset', 'processed_dataset_4500.csv')
    enc_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'TrainDataset', 'encoders', 'category_decoder.json')
    train_cats = {}
    train_total = 0
    train_lens = []
    train_unique = 0
    try:
        with open(train_path, encoding='utf-8') as f:
            rows = list(csv.DictReader(f))
        train_total = len(rows)
        unique_texts = set()
        for r in rows:
            c = r['category']
            train_cats[c] = train_cats.get(c, 0) + 1
            train_lens.append(len(r['text']))
            unique_texts.add(r['text'])
        train_unique = len(unique_texts)
    except: pass
    train_avg_len = round(sum(train_lens) / len(train_lens)) if train_lens else 0
    train_min_len = min(train_lens) if train_lens else 0
    train_max_len = max(train_lens) if train_lens else 0
    sorted_lens = sorted(train_lens)
    train_median_len = sorted_lens[len(sorted_lens)//2] if sorted_lens else 0
    train_cat_labels = list(train_cats.keys())
    train_cat_values = list(train_cats.values())

    return render_template('admin/report.html', complaints=complaints,
        total=total, resolved=resolved, in_progress=in_progress, pending=pending, validated=validated,
        cat_labels=cat_labels, cat_values=cat_values,
        train_total=train_total, train_unique=train_unique,
        train_avg_len=train_avg_len, train_min_len=train_min_len,
        train_max_len=train_max_len, train_median_len=train_median_len,
        train_cat_labels=train_cat_labels, train_cat_values=train_cat_values,
        admin_name=session.get('fullname', 'Admin'))

@app.route('/admin/export/csv')
def admin_export_csv():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
    conn = get_db(); cur = conn.cursor()
    cur.execute("""SELECT ticket_id,fullname,email,category,priority,status,subject,description,
        assigned_to,validated,date_format(created_at,'%%Y-%%m-%%d %%H:%%i:%%s') created_at,
        date_format(resolved_at,'%%Y-%%m-%%d %%H:%%i:%%s') resolved_at
        FROM complaints ORDER BY created_at DESC""")
    rows = cur.fetchall()
    cur.close(); conn.close()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Ticket ID', 'Student Name', 'Email', 'Category', 'Priority', 'Status',
        'Subject', 'Description', 'Assigned To', 'Validated', 'Submitted At', 'Resolved At'])
    for r in rows:
        writer.writerow([r['ticket_id'], r['fullname'], r['email'], r['category'], r['priority'],
            r['status'], r['subject'], r['description'], r['assigned_to'] or '',
            'Yes' if r['validated'] else 'No', r['created_at'], r['resolved_at'] or ''])
    response = app.response_class(
        response=output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=complainify_report.csv'}
    )
    return response

# ── API: Report data (for TrainDataset/report.html) ──

@app.route('/admin/report/data')
def admin_report_data():
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT COUNT(*) total, SUM(status='Resolved') resolved, SUM(status='In Progress') in_progress, SUM(status='Pending') pending FROM complaints")
    row = cur.fetchone()
    cur.close(); conn.close()
    return jsonify({'total': row['total'], 'resolved': row['resolved'], 'in_progress': row['in_progress'], 'pending': row['pending']})

# ── API: Auto-categorize ──

@app.route('/api/predict', methods=['POST'])
def api_predict():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400
    result = categorize(data['text'])
    return jsonify({
        'category': result['category'],
        'confidence': round(result['confidence'], 4),
        'tier': result['tier']
    })

# ── COMMENTS ──

@app.route('/complaint/<ticket_id>/comment', methods=['POST'])
def add_comment(ticket_id):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    message = request.form.get('message', '').strip()
    if not message:
        flash('Comment cannot be empty.', 'error')
        return redirect(request.referrer or url_for('index'))
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT id, user_id FROM complaints WHERE ticket_id=%s", (ticket_id,))
    complaint = cur.fetchone()
    if not complaint:
        cur.close(); conn.close()
        flash('Complaint not found.', 'error')
        return redirect(url_for('index'))
    cur.execute("INSERT INTO complaint_comments (complaint_id, user_id, message) VALUES (%s, %s, %s)",
        (complaint['id'], session['user_id'], message))
    conn.commit()
    # Notify the other party
    if session['user_id'] != complaint['user_id']:
        create_notification(complaint['user_id'], f'New comment on #{ticket_id}', url_for('student_complaint_detail', ticket_id=ticket_id))
    else:
        conn2 = get_db(); cur2 = conn2.cursor()
        cur2.execute("SELECT id FROM users WHERE role='admin'")
        for admin in cur2.fetchall():
            create_notification(admin['id'], f'New comment on #{ticket_id}', url_for('admin_complaint_detail', ticket_id=ticket_id))
        cur2.close(); conn2.close()
    log_action(session['user_id'], 'add_comment', 'complaint', ticket_id, message[:100])
    cur.close(); conn.close()
    flash('Comment added.', 'success')
    return redirect(request.referrer or url_for('index'))

# ── NOTIFICATIONS API ──

@app.route('/notifications/count')
def notifications_count():
    if 'user_id' not in session:
        return jsonify({'count': 0})
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT COUNT(*) cnt FROM notifications WHERE user_id=%s AND is_read=0", (session['user_id'],))
    row = cur.fetchone()
    cur.close(); conn.close()
    return jsonify({'count': row['cnt'] if row else 0})

@app.route('/notifications')
def notifications_list():
    if 'user_id' not in session:
        return jsonify({'notifications': []})
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT id, message, link, is_read, created_at FROM notifications WHERE user_id=%s ORDER BY created_at DESC LIMIT 20", (session['user_id'],))
    rows = cur.fetchall()
    cur.close(); conn.close()
    return jsonify({'notifications': [{
        'id': r['id'], 'message': r['message'], 'link': r['link'],
        'is_read': bool(r['is_read']),
        'created_at': r['created_at'].strftime('%d %b %Y %I:%M %p') if r['created_at'] else ''
    } for r in rows]})

@app.route('/notifications/mark-read/<int:nid>')
def notifications_mark_read(nid):
    if 'user_id' not in session:
        return jsonify({'ok': False})
    conn = get_db(); cur = conn.cursor()
    cur.execute("UPDATE notifications SET is_read=1 WHERE id=%s AND user_id=%s", (nid, session['user_id']))
    conn.commit(); cur.close(); conn.close()
    return jsonify({'ok': True})

@app.route('/notifications/mark-all-read')
def notifications_mark_all_read():
    if 'user_id' not in session:
        return jsonify({'ok': False})
    conn = get_db(); cur = conn.cursor()
    cur.execute("UPDATE notifications SET is_read=1 WHERE user_id=%s", (session['user_id'],))
    conn.commit(); cur.close(); conn.close()
    return jsonify({'ok': True})

# ── AUDIT LOGS (Admin) ──

@app.route('/admin/audit-logs')
def admin_audit_logs():
    if not login_required('admin'):
        return redirect(url_for('admin_login'))
    conn = get_db(); cur = conn.cursor()
    action_filter = request.args.get('action', '')
    page = int(request.args.get('page', 1))
    per_page = 50
    offset = (page - 1) * per_page
    base = "FROM audit_logs WHERE 1=1"
    params = []
    if action_filter:
        base += " AND action=%s"
        params.append(action_filter)
    cur.execute(f"SELECT COUNT(*) cnt {base}", params)
    total = cur.fetchone()['cnt']
    total_pages = max(1, (total + per_page - 1) // per_page)
    cur.execute(f"""SELECT audit_logs.*, users.fullname FROM audit_logs
        LEFT JOIN users ON audit_logs.user_id=users.id
        {base} ORDER BY created_at DESC LIMIT %s OFFSET %s""", params + [per_page, offset])
    logs = cur.fetchall()
    cur.execute("SELECT DISTINCT action FROM audit_logs ORDER BY action")
    actions = [r['action'] for r in cur.fetchall()]
    cur.close(); conn.close()
    return render_template('admin/audit_logs.html', logs=logs, actions=actions,
        action_filter=action_filter, page=page, total_pages=total_pages, total=total,
        admin_name=session.get('fullname', 'Admin'))

# ── USER MANAGEMENT (Admin) ──

@app.route('/admin/users')
def admin_users():
    if not login_required('admin'):
        return redirect(url_for('admin_login'))
    conn = get_db(); cur = conn.cursor()
    search = request.args.get('search', '')
    role_filter = request.args.get('role', '')
    query = "SELECT u.*, (SELECT COUNT(*) FROM complaints WHERE user_id=u.id) complaint_count FROM users u WHERE 1=1"
    params = []
    if search:
        query += " AND (u.fullname LIKE %s OR u.email LIKE %s OR u.phone LIKE %s)"
        s = f'%{search}%'
        params.extend([s, s, s])
    if role_filter:
        query += " AND u.role=%s"
        params.append(role_filter)
    query += " ORDER BY u.created_at DESC"
    cur.execute(query, params)
    users = cur.fetchall()
    cur.close(); conn.close()
    return render_template('admin/users.html', users=users, search=search, role_filter=role_filter,
        admin_name=session.get('fullname', 'Admin'))

@app.route('/admin/users/reset-password/<int:uid>', methods=['POST'])
def admin_reset_user_password(uid):
    if not login_required('admin'):
        return redirect(url_for('admin_login'))
    new_pw = request.form.get('new_password', '')
    if len(new_pw) < 6:
        flash('Password must be at least 6 characters.', 'error')
        return redirect(url_for('admin_users'))
    conn = get_db(); cur = conn.cursor()
    cur.execute("UPDATE users SET password=%s, plain_password=%s WHERE id=%s",
        (hash_pw(new_pw), new_pw, uid))
    conn.commit(); cur.close(); conn.close()
    log_action(session['user_id'], 'reset_user_password', 'user', str(uid), '')
    flash('Password reset successful.', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/users/delete/<int:uid>', methods=['POST'])
def admin_delete_user(uid):
    if not login_required('admin'):
        return redirect(url_for('admin_login'))
    if uid == session['user_id']:
        flash('Cannot delete yourself.', 'error')
        return redirect(url_for('admin_users'))
    conn = get_db(); cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id=%s", (uid,))
    conn.commit(); cur.close(); conn.close()
    log_action(session['user_id'], 'delete_user', 'user', str(uid), '')
    flash('User deleted.', 'success')
    return redirect(url_for('admin_users'))

# ── FILE SERVING ──

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/dashboard-redirect')
def dashboard_redirect():
    if session.get('role') == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif session.get('role') == 'student':
        return redirect(url_for('student_dashboard'))
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
