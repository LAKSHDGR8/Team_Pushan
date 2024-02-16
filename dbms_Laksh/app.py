from flask import Flask, render_template, redirect, url_for, request,session
from flask_socketio import SocketIO
import threading
import time
import sqlite3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
socketio = SocketIO(app)

def get_db_connection():
    conn = sqlite3.connect('canteen.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def create_users_table():
    conn = get_db_connection()
    conn.execute('CREATE TABLE IF NOT EXISTS users (Username varchar(20), Email varchar(20), Password varchar(20), Confirmation varchar(20))')
    print("Table users created successfully")
    conn.close()

create_users_table()

def create_orders_table():
    conn = get_db_connection()
    conn.execute('CREATE TABLE IF NOT EXISTS orders (bill_no INTEGER PRIMARY KEY AUTOINCREMENT,bill_amount REAL,username TEXT)')
    print("Table orders created successfully")
    conn.close()

create_orders_table()

def check_for_updates():
    last_known_row_count = 0
    while True:
        conn = get_db_connection()
        cur = conn.execute('SELECT COUNT(*) AS count FROM orders')
        row_count = cur.fetchone()['count']
        if row_count != last_known_row_count:
            last_known_row_count = row_count
            socketio.emit('database_update', {'data': 'New user added'})
        conn.close()
        time.sleep(10)  # Poll every 10 seconds

@app.route('/')
def hello():
    return render_template('dbms.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        usr = request.form['usr']
        email = request.form['email']
        pwd = request.form['pwd']
        cpwd = request.form['cpwd']

        # Check if passwords match
        if pwd != cpwd:
            # If they do not match, return to the signup page with an error message
            return render_template('welcome.html', msg="Password does not match")

        try:
            conn = get_db_connection()
            conn.execute("INSERT INTO users (Username, Email, Password, Confirmation) VALUES (?, ?, ?, ?)", (usr, email, pwd, cpwd))
            conn.commit()
            msg = "You have signed up successfully"
        except:
            conn.rollback()
            msg = "Error in last operation"
        finally:
            conn.close()
            return redirect(url_for('welcome', msg=msg))

    return render_template('signup.html')

@app.route('/welcome')
def welcome():
    # Retrieve the message from query parameters
    msg = request.args['msg']
    return render_template('welcome.html', msg=msg)

@app.route('/signin', methods=['POST', 'GET'])
def signin():
    if request.method == 'POST':
        usr = request.form['usr']
        pwd = request.form['pwd']
        
        conn = get_db_connection()
        cur = conn.execute('SELECT * FROM users WHERE Username = ? AND Password = ?', (usr, pwd))
        user = cur.fetchone()
        conn.close()

        if user:
            session['username'] = user['Username']
            return render_template('home.html')
        #     return redirect(url_for('welcome', msg="User successfully signed in"))
        else:
            return render_template('welcome.html', msg="Wrong username/password")

    return render_template('home.html')

@app.route('/menu', methods=['POST', 'GET'])
def menu():
    return render_template('menu.html')

@app.route('/generate_bill', methods=['POST'])
def generate_bill():
    if request.method == 'POST':
        bill_amount = request.form['billAmount']
        username = session.get('username')  # Get the username from the session

        if not username:
            return {"message": "User is not logged in"}, 403

        try:
            conn = get_db_connection()
            conn.execute("INSERT INTO orders (bill_amount, username) VALUES (?, ?)", (bill_amount, username))
            conn.commit()
            msg = "Bill generated successfully"
        except Exception as e:
            conn.rollback()
            msg = f"Error in generating bill: {str(e)}"
        finally:
            conn.close()
            return {"message": msg}

@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove the username from the session
    return render_template('dbms.html')


if __name__ == '__main__':
    threading.Thread(target=check_for_updates, daemon=True).start()
    socketio.run(app, debug=True)
