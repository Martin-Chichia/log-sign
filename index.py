from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import bcrypt

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

# Connect to database
def connect_db():
    return sqlite3.connect('users.db')

# Create tables if not existing
def setup_database():
    conn = connect_db()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            second_name TEXT NOT NULL,
            third_name TEXT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            location TEXT NOT NULL,
            age INTEGER NOT NULL,
            best_books_category TEXT NOT NULL
        )
    ''')
    
    # Create books table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            is_borrowed INTEGER DEFAULT 0
        )
    ''')
    
    # Create borrow records table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS borrow_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            borrow_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            return_date TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(book_id) REFERENCES books(id)
        )
    ''')
    conn.commit()
    conn.close()

# Hash the password
def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)

# Insert a new user
def insert_user(first_name, second_name, third_name, username, password, location, age, best_books_category):
    conn = connect_db()
    cursor = conn.cursor()
    hashed_password = hash_password(password)

    try:
        cursor.execute('''
            INSERT INTO users (first_name, second_name, third_name, username, password, location, age, best_books_category)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (first_name, second_name, third_name, username, hashed_password, location, age, best_books_category))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return False  # Username already exists
    conn.close()
    return True

# Routes
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form['first_name']
        second_name = request.form['second_name']
        third_name = request.form['third_name']
        username = request.form['username']
        password = request.form['password']
        location = request.form['location']
        age = request.form['age']
        best_books_category = request.form['best_books_category']

        if insert_user(first_name, second_name, third_name, username, password, location, age, best_books_category):
            flash('User created successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Username already exists. Try another one.', 'danger')

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[4].encode('utf-8')):
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash('You must log in to access the dashboard.', 'danger')
        return redirect(url_for('index'))
    
    username = session['username']
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()

    return render_template('dashboard.html', user=user)

@app.route('/borrow', methods=['GET', 'POST'])
def borrow():
    if 'username' not in session:
        flash('You must log in to borrow a book.', 'danger')
        return redirect(url_for('index'))
    # Borrow logic here
    return render_template('borrow.html')

@app.route('/return', methods=['GET', 'POST'])
def return_book():
    if 'username' not in session:
        flash('You must log in to return a book.', 'danger')
        return redirect(url_for('index'))
    # Return logic here
    return render_template('return.html')

@app.route('/membership', methods=['GET', 'POST'])
def membership():
    if 'username' not in session:
        flash('You must log in to buy a membership.', 'danger')
        return redirect(url_for('index'))
    # Membership logic here
    return render_template('membership.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    setup_database()  # Ensure database tables exist
    app.run(debug=True)
