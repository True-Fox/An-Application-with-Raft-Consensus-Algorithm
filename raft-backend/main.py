# Write the log
# handle post for nodes other than leader

from pyraft import raft
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
    cursor = conn.cursor()
    cursor.execute(query,args)
    
    conn.commit()
    cursor.close()

def doGet(query:str, args:tuple):
    cursor = conn.cursor()
    cursor.execute(query, args)
    return cursor.fetchone()
    

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

@app.route('/api/post', methods=['POST'])
def post():
    data = request.get_json()
    query = data['query']
    data = tuple(data.values())
    print("Query: ", query)
    print("Data:",data[1:] )
    if node.state == 'l':
        doPost(query,data[1:])
        return "Success"
    else:
        print(node.get_peers())
        return "Node is not a leader, forward the request to leader"

@app.route('/api/get', methods=['GET'])
def get():
    data = request.get_json()
    query = data['query']
    data_t = tuple(data.values())
    print(f"Query: {query} \n Data: {data_t[1:]}")
    if node.state == "l":
        res = doGet(query, data_t[1:])
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
                print("Response from leader: ",response.text)
                
        return "This node is not a leader.. forwarding request to leader node"

node.worker.handler['on_leader'] = check_lead
node.worker.handler['on_canditate'] = check_cand
node.worker.handler['on_follower'] = check_foll
node.worker.handler['on_start'] = start_server

node.start()
node.join()