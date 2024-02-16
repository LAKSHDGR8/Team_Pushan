from flask import Flask, render_template, redirect, url_for,request,session,jsonify
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
    conn.execute('CREATE TABLE IF NOT EXISTS users (Username varchar(20) PRIMARY KEY, Email varchar(20), Password varchar(20), Confirmation varchar(20))')
    print("Table users created successfully")
    conn.close()

create_users_table()

def create_orders_table():
    conn = get_db_connection()
    conn.execute('CREATE TABLE IF NOT EXISTS orders (bill_no INTEGER PRIMARY KEY AUTOINCREMENT,bill_amount REAL NOT NULL,username TEXT NOT NULL,FOREIGN KEY (username) REFERENCES users(Username))')
    print("Table orders created successfully")
    conn.close()

create_orders_table()

def create_wallet_table():
    conn = get_db_connection()
    conn.execute('CREATE TABLE IF NOT EXISTS wallet (username TEXT PRIMARY KEY,balance REAL DEFAULT 0,FOREIGN KEY (username) REFERENCES users(Username))')
    print("Table wallet created successfully")
    conn.close()

create_wallet_table()

def create_notifications_table():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (username) REFERENCES users(Username))''')
    print("Table notifications created successfully")
    conn.close()

create_notifications_table()


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

@app.route('/wallet', methods=['POST', 'GET'])
def wallet():
    return render_template('wallet.html')

@app.route('/notifications')
def notifications():
    if 'username' not in session:
        return redirect(url_for('signin'))

    username = session['username']
    conn = get_db_connection()
    notifications = conn.execute('SELECT message, timestamp FROM notifications WHERE username = ? ORDER BY timestamp DESC', (username,)).fetchall()
    conn.close()
    return render_template('notifications.html', notifications=notifications)

@app.route('/order_history')
def order_history():
    if 'username' not in session:
        return redirect(url_for('signin'))  # Ensure user is logged in

    username = session['username']
    conn = get_db_connection()
    
    # This is a conceptual query; you'll need to adjust it to correctly match orders with their notifications
    order_history = conn.execute('''
        SELECT o.bill_no, o.bill_amount, MAX(n.timestamp) as timestamp
        FROM orders o
        JOIN notifications n ON o.username = n.username AND n.message LIKE '%' || o.bill_amount || '%'
        WHERE o.username = ?
        GROUP BY o.bill_no
        ORDER BY o.bill_no DESC;

    ''', (username,)).fetchall()
    
    conn.close()

    # Assuming you have a method to accurately match orders with notifications
    return render_template('order_history.html', order_history=order_history)


@app.route('/generate_bill', methods=['POST'])
def generate_bill():
    if 'username' not in session:
        return jsonify({'message': 'User not logged in'}), 403

    username = session['username']
    bill_amount = request.form.get('billAmount', type=float)

    conn = get_db_connection()
    cur = conn.execute('SELECT balance FROM wallet WHERE username = ?', (username,))
    wallet_row = cur.fetchone()

    if wallet_row is None or wallet_row['balance'] < bill_amount:
        return jsonify({'message': 'Insufficient funds in the wallet'}), 400

    try:
        # Deduct the bill amount from the wallet
        conn.execute('UPDATE wallet SET balance = balance - ? WHERE username = ?', (bill_amount, username))
        # Insert the bill into orders
        conn.execute('INSERT INTO orders (bill_amount, username) VALUES (?, ?)', (bill_amount, username))
        # Add a notification for the user
        notification_message = f"Your order for ${bill_amount} has been placed"
        conn.execute('INSERT INTO notifications (username, message) VALUES (?, ?)', (username, notification_message))
        conn.commit()
        return jsonify({'message': 'Bill generated and amount deducted from wallet'})
    except Exception as e:
        conn.rollback()
        return jsonify({'message': 'Error in generating bill: ' + str(e)}), 500
    finally:
        conn.close()


@app.route('/get_balance', methods=['GET'])
def get_balance():
    if 'username' not in session:
        return jsonify({'message': 'User not logged in'}), 403

    username = session['username']
    conn = get_db_connection()
    cur = conn.execute('SELECT balance FROM wallet WHERE username = ?', (username,))
    wallet_row = cur.fetchone()
    conn.close()

    if wallet_row:
        return jsonify({'balance': wallet_row['balance']})
    else:
        # Assuming zero balance if the wallet entry doesn't exist
        return jsonify({'balance': 0.0})


@app.route('/add_funds', methods=['POST'])
def add_funds():
    if 'username' not in session:
        return jsonify({'message': 'User not logged in'}), 403

    amount = request.form.get('amount', type=float)
    if amount is None or amount <= 0:
        return jsonify({'message': 'Invalid amount'}), 400

    username = session['username']
    conn = get_db_connection()
    try:
        # Check if the user already has a wallet entry
        cur = conn.execute('SELECT balance FROM wallet WHERE username = ?', (username,))
        wallet_row = cur.fetchone()

        if wallet_row:
            # Update balance if wallet exists
            conn.execute('UPDATE wallet SET balance = balance + ? WHERE username = ?', (amount, username))
        else:
            # Create a new wallet entry if it doesn't exist
            conn.execute('INSERT INTO wallet (username, balance) VALUES (?, ?)', (username, amount))
        
        conn.commit()
        return jsonify({'message': 'Funds added successfully'})
    except Exception as e:
        conn.rollback()
        return jsonify({'message': str(e)}), 500
    finally:
        conn.close()


@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove the username from the session
    return render_template('dbms.html')


if __name__ == '__main__':
    threading.Thread(target=check_for_updates, daemon=True).start()
    socketio.run(app, debug=True)
