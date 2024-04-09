from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re, random


app = Flask(__name__)
app.secret_key = "s3cr34_14_5335MS"
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'ambhi'
app.config['MYSQL_PASSWORD'] = 'ambhi'
app.config['MYSQL_DB'] = 'task_mgmt'

mysql = MySQL(app=app)


@app.route('/login/', methods=['GET','POST'])
def login():
    msg=''
    if request.method=='POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s",(username,password))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id']=account['user_id']
            session['username']=account['username']
            return render_template('index.html',username=session['username'])
        else:
            msg = 'Incorrect username/password'
            print(msg)
    return render_template('login.html', msg='')

@app.route('/register/',  methods=['GET','POST'])
def register():
    msg=''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE username=%s",(username,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            id = random.randint(1, 100)
            role = "user"
            cursor.execute('INSERT INTO users VALUES (%s, %s, %s, %s, %s)', (id,username, password, email, role))
            mysql.connection.commit()
            return render_template("login.html")
    return render_template('register.html', msg='')

@app.route('/login/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/home')
def home():
    if session['username']:
        return render_template("index.html", username=session['username'])
    else:
        return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True)