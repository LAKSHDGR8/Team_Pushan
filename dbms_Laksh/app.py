from flask import Flask, render_template, redirect, url_for, request
import sqlite3

conn = sqlite3.connect('canteen.db')
print ("Created database succesfuly")

conn.execute('CREATE TABLE IF NOT EXISTS users(Username varchar(20),Email varchar(20),Password varchar(20),Confirmation varchar(20))')
print("Table created succesfully")

app = Flask(__name__)

@app.route('/')
def hello():
    return render_template('dbms.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        try:
            usr = request.form['usr']
            email = request.form['email']
            pwd = request.form['pwd']
            cpwd = request.form['cpwd']

            with sqlite3.connect("canteen.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO users (Username, Email, Password, Confirmation) VALUES (?, ?, ?, ?)", (usr, email, pwd, cpwd))
                con.commit()
                msg = "You have signed up successfully"
        except:
            con.rollback()
            msg = "error in last operation"
        finally:
            con.close()

            # Redirect to a new route after successful signup
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
        
        conn = sqlite3.connect('canteen.db')
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE Username = ? AND Password = ?', (usr, pwd))
        user = cur.fetchone()
        conn.close()

        if user:
            return "User successfully signed in"
        else:
            return "Wrong username/password"

    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True)