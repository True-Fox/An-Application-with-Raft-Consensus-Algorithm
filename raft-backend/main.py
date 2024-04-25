# Write the log
# handle post for nodes other than leader

from pyraft import raft
import logging
from logging.handlers import RotatingFileHandler
from time import sleep
from flask import Flask, jsonify, render_template, make_response
import os, json
from dotenv import load_dotenv
from flask import request
from mysql.connector import connection
import requests

load_dotenv()
node = raft.make_default_node()
app = Flask(__name__) 


conn = connection.MySQLConnection(
    host = os.getenv("MY_SQL_HOST"),
    user = os.getenv("MYSQL_USER"),
    password = os.getenv("MYSQL_PASSWORD"),
    database = "task_mgmt"+node.nid
)

def doPost(query:str, args:tuple):
    cursor = conn.cursor(buffered=True)
    cursor.execute(query,args)
    
    conn.commit()
    cursor.close()

def doGet(query:str, fetch_status: str, args:tuple):
    cursor = conn.cursor(buffered=True)
    cursor.execute(query, args)
    if (fetch_status == "one"):
        return cursor.fetchone()
    return cursor.fetchall()
    
logging.basicConfig(filename=f'logs/node_{node.nid}.log',
                format='%(message)s',
                level=logging.INFO,
                filemode='w')
logger = logging.getLogger()

logs_folder = 'logs'

def log_file_traverse(logs_folder, conn):
    for log_file in os.listdir(logs_folder):
        if log_file.endswith(".log"):
            log_path = os.path.join(logs_folder, log_file)
            cursor = conn.cursor()
            with open(log_path, 'r') as log:
                queries = extract_queries_from_log(log)
                for query in queries:
                    try:
                        cursor.execute(query)
                    except Exception as e:
                        print(f"Error executing query: {query}\nError: {e}")
            conn.commit()
            cursor.close()

# def extract_queries_from_log(log_file):
#     queries = []
#     current_query = ''
#     for line in log_file:
#         if line.startswith("Query:"):
#             current_query = line.lstrip("Query:").strip()
#         elif line.strip(): 
#             current_query += line.strip()
#         else: 
#             if current_query:
#                 queries.append(current_query)
#                 current_query = ''
#     return queries

def extract_queries_from_log(log_file):
    queries = []
    current_query = ''
    # Read the file in reverse
    for line in reversed(list(log_file)):
        if line.startswith("Query:"):
            # Found a query line, set it as the current query
            current_query = line.lstrip("Query:").strip()
            # Stop reading further as we want the first query encountered from the back
            break
        elif line.strip():
            # Non-empty line, prepend it to the current query
            current_query = line.strip() + current_query
        else:
            # Empty line encountered, consider it as the end of a query
            if current_query:
                queries.append(current_query)
                current_query = ''
    return queries[::-1]  # Reverse the list to maintain original order


logs_folder = 'logs' 
log_file_traverse(logs_folder, conn) 



def start_server(node):
    app.run(host="localhost", port = 5000 + int(node.nid))

def check_cand(node):
    node.state = 'c'

def check_foll(node):
    node.state = 'f'

def check_lead(node):
    node.state = 'l'

@app.route('/api/getPeersInfo')
def index():
    peers = node.get_peers()
    peer_info = []
    for nid, peer in peers.items():
        peer_info.append({"id": nid, "state": peer.state})
        if peer.state == 'l':
            print(f"node {nid} is the leader")
    
    return render_template('peer_info.html', peers=peer_info, node=node)   

@app.route('/api/updateLogs', methods=['POST'])
def update_logs():
    data = request.get_json()
    query = data['query']
    data_t = tuple(data.values())
    logger.info("Query: %s, Data: %s", query, data_t[1:])
    return "Success"

@app.route('/api/updateDB', methods=['POST'])
def updateDB():
    data = request.get_json()
    print("This is the data recieved: ")
    print(data)
    query = data['query']
    data_t = tuple(data.values())
    print("Query: ", query)
    print("Data:",data_t[1:] )
    doPost(query, data_t[1:])
    return "Success"

@app.route('/api/post', methods=['POST'])
def post():
    data = request.get_json()
    print("This is the data recieved: ")
    print(data)
    query = data['query']
    data_t = tuple(data.values())
    print("Query: ", query)
    print("Data:",data_t[1:] )
    if node.state == 'l':
        doPost(query,data_t[1:])
        logger.info("Query: %s, Data: %s", query, data_t[1:])
        for id, raft_node in node.get_peers().items():
            if raft_node.state != 'l':
                url = "http://localhost:" + str(5000+int(id))+"/api/updateLogs"
                response = requests.post(url=url, json=data)
                url1 = "http://localhost:" + str(5000+int(id))+"/api/updateDB"
                response1 = requests.post(url=url1, json=data)
        return "Success"
    else:
        print(node.get_peers())
        for id, raft_node in node.get_peers().items():
            print("Id is {}, state: {}".format(id, raft_node.state))
            if raft_node.state == 'l':
                url = "http://localhost:" + str(5000+int(id))+"/api/post"
                print(data)
                response = requests.post(url=url, json=data)
                print("Response from leader: ", response)
                return "Success"
        return "Node is not a leader, forward the request to leader"

@app.route('/api/get', methods=['GET'])
def get():
    data = request.get_json()
    query = data['query']
    fetch_status = data['fetch_status']
    data_t = tuple(data.values())
    print(f"Query: {query} \n Data: {data_t[2:]}")
    if node.state == "l":
        res = doGet(query, fetch_status, data_t[2:])
        print(res)
        if res:
            return jsonify(res)
        return "No Data Available", 500
    else:
        print(node.get_peers())
        for id, raft_node in node.get_peers().items():
            print("Id is {}, state: {}".format(id, raft_node.state))
            if raft_node.state == 'l':
                url = "http://localhost:" + str(5000+int(id))+"/api/get"
                print(data)
                response = requests.get(url=url, json=data)
                print("Response from leader: ", response.text)
                return response.json()
        return "This node is not a leader.. forwarding request to leader node"

node.worker.handler['on_leader'] = check_lead
node.worker.handler['on_canditate'] = check_cand
node.worker.handler['on_follower'] = check_foll
node.worker.handler['on_start'] = start_server

node.start()
node.join()