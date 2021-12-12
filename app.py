from flask import Flask , render_template
from flask_socketio import SocketIO , emit
from threading import Lock
from pymongo import MongoClient
from datetime import datetime

from requests import get 
from bs4 import BeautifulSoup
from logging import basicConfig , getLogger , INFO , info , FileHandler
from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')

basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level = INFO,
            handlers=[FileHandler('basic.log','w','utf-8')])
logger = getLogger(__name__)

async_mode = None
app = Flask(__name__ , template_folder='./template/')
app.config["DEBUG"] = True
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app , async_mode=async_mode)
thread = None
thread_lock = Lock()

def background_thread():
    

    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
    }

    def upload(name , num):
        current_time = datetime.today().strftime("%Y/%m/%d-%H:%M:%S")
        data = [current_time , num]
        myquery = {"_id" : name}
        info(f" data get : {name}  {num}")
        # init 
        if collection.count_documents(myquery) == 0:
            add = {"_id" : name , "view":[data]}
            collection.insert_one(add)
            info(f"data create : {name} - {num}")
            with app.test_request_context():
                    socketio.emit('data_update' ,{'date' : current_time , 'name' : name , 'view' : num} )
        else:
            user = collection.find_one(myquery)
            view_list = user["view"]
            if view_list[-1][1] != num or view_list[-1][0][:10] != current_time[:10]:
                view_list.append(data)
                collection.update_one({
                "_id" : name
                },{"$set" : {
                    "view" : view_list
                }}
                )
                info(f"data update : {name} - {num}")
                with app.test_request_context():
                    socketio.emit('data_update' ,{'date' : current_time , 'name' : name , 'view' : num} )
    
    def main():
        r = get("https://ani.gamer.com.tw" , "html.parser" , headers= header)
        soup = BeautifulSoup(r.text , 'lxml')
        datas = soup.find_all("a", {"class": "anime-card-block"})

        for data in datas:
            details = data.find_all("p",{"class":""})
            info(f"data scrap : {details}")

            if len(list(details)) == 3:
                if "萬" in list(details)[2].string:
                    num = int(float(list(details)[2].string.replace("萬",""))*10000)
                    upload(list(details)[1].string,num)
                elif "統計中" in list(details)[2].string:
                    num = 0
                    upload(list(details)[1].string,num) 
                else:
                    num = int(list(details)[2].string)
                    upload(list(details)[1].string,num)
             

            if len(list(details)) == 2:
                if "萬" in list(details)[1].string:
                    num = int(float(list(details)[1].string.replace("萬",""))*10000)
                    upload(list(details)[0].string,num)
                elif "統計中" in list(details)[1].string:
                    num = 0 
                    upload(list(details)[0].string,num)
                else:
                    num = int(list(details)[1].string)
                    upload(list(details)[0].string,num)

    while True:
        socketio.sleep(300)
        info("run web scraping")
        main()
        
        


@app.route('/')
def index():
    return render_template('index.html' , async_mode = socketio.async_mode)

@socketio.on('connect')
def test_connect():
    global thread 
    with thread_lock:
        if thread is None:
            info("thread start")
            thread = socketio.start_background_task(target=background_thread)

@socketio.on('client_event')
def client_msg(msg):
    info(f"message receive : {msg}")

@socketio.on('connect_event')
def connected_msg(msg):
    info("connection receive : {msg}")
    emit('server_response' , {'data': msg['data']})

@socketio.on('client_event_search')
def client_msg(msg):
    info(f"data request received : {msg}")
    myquery = {"_id" : msg['data']}
        
       
    if collection.count_documents(myquery) == 0:
        info(f"data request result : {msg} - fail")
        with app.test_request_context():
            socketio.emit('data_search' ,{'type' : "0"} )
    else:
        user = collection.find_one(myquery)
        view_list = user["view"]    
        info(f"data request result : {msg} - success")
        with app.test_request_context():
            socketio.emit('data_search' ,{'type' : "1" , 'data' :view_list} )


if __name__ == '__main__':
    cluster = MongoClient(
        config['MONGODB']['CLIENT']
    )
    info(cluster.server_info())
    db = cluster["anime_view"]
    collection = db["anime_view"]

    socketio.run(app ,  host='127.0.0.1' , port=5000)
