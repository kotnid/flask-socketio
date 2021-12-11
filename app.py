from flask import Flask , render_template
from flask_socketio import SocketIO , emit
import socketio

app = Flask(__name__ , template_folder='./')
app.config["DEBUG"] = True
app.config['SECRET_KEY'] = 'secret!'

socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('client_event')
def client_msg(msg):
    print(msg)

@socketio.on('connect_event')
def connected_msg(msg):
    print("hi")
    emit('server_response' , {'data': msg['data']})

if __name__ == '__main__':
    socketio.run(app , debug=True , host='127.0.0.1' , port=5000)
