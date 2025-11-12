from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

# 定义数据库文件的路径 (这会让 income.db 文件创建在和 app.py 相同的位置)
DATABASE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'income.db')

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS income (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            amount REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add', methods=['POST'])
def add_income():
    date = request.form['date']
    amount = request.form['amount']
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("INSERT INTO income (date, amount) VALUES (?, ?)", (date, amount))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT date, amount FROM income ORDER BY date")
    data = c.fetchall()
    conn.close()
    labels = [row[0] for row in data]
    values = [row[1] for row in data]
    return render_template('dashboard.html', labels=labels, values=values)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', debug=True, use_reloader=False)