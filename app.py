from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from datetime import datetime
import MySQLdb.cursors
import re, random
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.secret_key = "s3cr34_14_5335MS"
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')

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
            return redirect(url_for('home'))
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
    if session.get('loggedin'):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM Projects")
        projects = cursor.fetchall()
        return render_template("index.html", username=session['username'], projects=projects)
    else:
        return url_for('login')

@app.route("/tasks/<int:project_id>")
def tasks(project_id):
    if session.get('loggedin'):
        # To be filled
        return render_template("tasks.html")
    else:
        return render_template("login.html")
    
@app.route("/add_project", methods=["POST", "GET"])
def add_project():
    msg = ''
    if session.get('loggedin'):
        if request.method == "POST":
            project_name = request.form["project_name"]
            project_description = request.form["project_description"]
            start_date = request.form["start_date"]
            end_date = request.form["end_date"]
            status = request.form["status"]
            
            # Convert start_date and end_date strings to datetime objects
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
            current_date = datetime.now()
            
            # Check if start date is not equal to current date and start date is greater than end date
            if start_date_obj <= end_date_obj:
                id = random.randint(1, 100)
                cursor = mysql.connection.cursor()
                cursor.execute("INSERT INTO Projects (project_id, project_name, project_description, start_date, end_date, status) VALUES (%s, %s, %s, %s, %s, %s)", (id, project_name, project_description, start_date, end_date, status))
                mysql.connection.commit()
                return redirect(url_for("home"))
            else:
                msg = "Invalid end date"
                return render_template("add_project.html", msg = msg)
        else:
            return render_template("add_project.html", msg = '')
    else:
        return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)