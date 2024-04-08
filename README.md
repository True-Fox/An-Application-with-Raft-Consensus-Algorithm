# Task Management Application with Raft Consensus Algorithm and MySQL

## Overview
- The objective of this project is to develop a task management application that utilises the Raft consensus algorithm to ensure consistency and fault tolerance across multiple nodes. 
-  MySQL will be employed as the backend database to store task data. The application will enable users to create, update, delete, and manage tasks across the distributed system.

---

### Installation
1) Create a virtual environment using venv and activate the environment.
    ```sh
    > python -m venv task-mgmt
    > ./task-mgmt/Scripts/activate
    ```
    To deactivate the environment
    ```sh
    > deactivate
    ```
2) Install the dependencies.
    ```sh
    > pip install -r requirements.txt
    ```
3) Create a new database in MySQL and make sure you change the values in the app.py file.
    ```py
    connection = mysql.connector.connect(
    host="localhost",
    user=<Username>,
    password=<Password>,
    database=<database_name>
    )
    ```
4) To set up the database, please use the source sql file from docs folder.

5) Start the developement server and go to http://localhost:5000/home.
    ```sh
    > flask run
    ```

6) Have fun!