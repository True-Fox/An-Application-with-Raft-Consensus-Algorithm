from sqlite3 import Cursor
from flask import Flask, render_template
import mysql.connector

connection = mysql.connector.connect(
    host="localhost",
    user="ambhi",
    password="ambhi",
    database="task_mgmt"
)
app = Flask(__name__)

cursor = connection.cursor()

if(cursor):
    print("Connection successful")

@app.route('/')
def hello():
    return "Hello, world"

@app.route('/home')
def home():
    cursor.execute("SELECT * FROM Tasks")
    rows = cursor.fetchall()
    return render_template("index.html", tasks= rows)


if __name__ == "__main__":
    app.run(debug=True)