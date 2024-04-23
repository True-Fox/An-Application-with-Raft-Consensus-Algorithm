from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from datetime import datetime
import MySQLdb.cursors
import re, random, requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.secret_key = "s3cr34_14_5335MS"
# app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
# app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
# app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
# app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')

# mysql = MySQL(app=app)


@app.route('/login/', methods=['GET','POST'])
def login():
    msg=''
    if request.method=='POST':
        username = request.form['username']
        password = request.form['password']
        # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s",(username,password))
        # account = cursor.fetchone()
        data = dict()
        data['query'] = "SELECT * FROM users WHERE username=%s AND password=%s"
        data['fetch_status'] = "one"
        data['username'] = username
        data['password'] = password
        url = "http://localhost:5003/api/get"
        account = requests.get(url=url, json=data).json()
        # print("type: ", type(account), "Content:", account)
        if account:
            session['loggedin'] = True
            session['id']=account[0]
            session['username']=account[1]
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

@app.route('/logout', methods=['POST'])
def logout():
    if session.get('loggedin'):
        session.clear()
    return redirect(url_for('login'))

@app.route('/')
@app.route('/home')
def home():
    if session.get('loggedin'):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM Projects")
        projects = cursor.fetchall()    
        return render_template("index.html", username=session['username'], projects=projects)
    else:
        return redirect(url_for('login'))

@app.route("/tasks/<int:project_id>")
def tasks(project_id):
    if session.get('loggedin'):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM Tasks WHERE project_id = %s", (project_id,))
        tasks = cursor.fetchall()

        pending_tasks = [task for task in tasks if task['status'] == 'pending']
        in_progress_tasks = [task for task in tasks if task['status'] == 'in progress']
        in_review_tasks = [task for task in tasks if task['status'] == 'in review']
        completed_tasks = [task for task in tasks if task['status'] == 'completed']

        return render_template("tasks.html", project_id=project_id, pending_tasks=pending_tasks, in_progress_tasks=in_progress_tasks, in_review_tasks=in_review_tasks, completed_tasks=completed_tasks)
    else:
        return redirect(url_for('login'))
    
@app.route('/projects/<int:project_id>/add_task', methods=['GET', 'POST'])
def add_task(project_id):
    if session.get('loggedin'):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT user_id, username FROM Users")
        users = cursor.fetchall()

        if request.method == 'POST':
            task_name = request.form.get('task_name')
            task_description = request.form.get('task_description')
            due_date = request.form.get('due_date')
            priority = request.form.get('priority')
            status = request.form.get('status')
            assigned_to = request.form.get('assigned_to')

            cursor.execute("INSERT INTO Tasks (project_id, task_name, task_description, due_date, priority, status, assigned_to) VALUES (%s, %s, %s, %s, %s, %s, %s)", (project_id, task_name, task_description, due_date, priority, status, assigned_to))
            mysql.connection.commit()
            return redirect(url_for('tasks', project_id=project_id))

        return render_template('add_task.html', project_id=project_id, users=users)
    else:
        return redirect(url_for('login'))

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
            
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
            current_date = datetime.now()
            
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

@app.route('/delete_project/<int:project_id>', methods=['POST'])
def delete_project(project_id):
    if session.get('loggedin'):
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM Projects WHERE project_id = %s", (project_id,))
        mysql.connection.commit()
    else:
        return redirect(url_for('login'))
    return redirect(url_for('home'))

@app.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    if session.get('loggedin'):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM Tasks WHERE task_id = %s", (task_id,))
        task = cursor.fetchone()

        if request.method == 'POST':
            new_status = request.form.get('status')
            cursor.execute("UPDATE Tasks SET status = %s WHERE task_id = %s", (new_status, task_id))
            mysql.connection.commit()
            return redirect(url_for('tasks', project_id=task['project_id']))

        return render_template('edit_task.html', task=task)
    else:
        return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)