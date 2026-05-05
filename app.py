from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
import hashlib

app = Flask(__name__)
app.secret_key = 'supersecretkey123'
DATABASE = 'students.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        roll_no TEXT UNIQUE NOT NULL,
        email TEXT NOT NULL,
        course TEXT NOT NULL,
        user_id INTEGER,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email    = request.form['email'].strip()
        password = request.form['password']
        confirm  = request.form['confirm_password']

        if not username or not email or not password:
            flash('All fields are required.', 'error')
            return render_template('register.html')

        if password != confirm:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')

        try:
            conn = get_db()
            conn.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                         (username, email, hash_password(password)))
            conn.commit()
            conn.close()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists.', 'error')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE username=? AND password=?',
                            (username, hash_password(password))).fetchone()
        conn.close()
        if user:
            session['user_id']  = user['id']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        flash('Invalid username or password.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    students = conn.execute('SELECT * FROM students WHERE user_id=?',
                            (session['user_id'],)).fetchall()
    conn.close()
    return render_template('dashboard.html', students=students)

@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        name    = request.form['name'].strip()
        roll_no = request.form['roll_no'].strip()
        email   = request.form['email'].strip()
        course  = request.form['course'].strip()
        if not name or not roll_no or not email or not course:
            flash('All fields are required.', 'error')
            return render_template('add_student.html')
        try:
            conn = get_db()
            conn.execute('INSERT INTO students (name, roll_no, email, course, user_id) VALUES (?,?,?,?,?)',
                         (name, roll_no, email, course, session['user_id']))
            conn.commit()
            conn.close()
            flash('Student added successfully!', 'success')
            return redirect(url_for('dashboard'))
        except sqlite3.IntegrityError:
            flash('Roll number already exists.', 'error')
    return render_template('add_student.html')

@app.route('/edit_student/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    student = conn.execute('SELECT * FROM students WHERE id=? AND user_id=?',
                           (student_id, session['user_id'])).fetchone()
    if not student:
        conn.close()
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        name   = request.form['name'].strip()
        email  = request.form['email'].strip()
        course = request.form['course'].strip()
        conn.execute('UPDATE students SET name=?, email=?, course=? WHERE id=?',
                     (name, email, course, student_id))
        conn.commit()
        conn.close()
        flash('Student updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    conn.close()
    return render_template('edit_student.html', student=student)

@app.route('/delete_student/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    conn.execute('DELETE FROM students WHERE id=? AND user_id=?',
                 (student_id, session['user_id']))
    conn.commit()
    conn.close()
    flash('Student deleted successfully.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/search')
def search():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    query = request.args.get('q', '').strip()
    conn  = get_db()
    students = conn.execute(
        'SELECT * FROM students WHERE user_id=? AND (name LIKE ? OR roll_no LIKE ? OR course LIKE ?)',
        (session['user_id'], f'%{query}%', f'%{query}%', f'%{query}%')
    ).fetchall()
    conn.close()
    return render_template('dashboard.html', students=students, search_query=query)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)