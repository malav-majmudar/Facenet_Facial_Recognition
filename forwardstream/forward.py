from flask import Flask, request
from flask_socketio import SocketIO, emit
import requests
import logging
import base64



class CameraStream:
    def init(self):
        self.app = None
        self.request = None

    def init_app(self, app):
        self.app = app
        self.request = requests.get("http://visage-cam.local/", stream=True)
        self.connect()

    def connect(self):
        return self.request.raw.read_chunked()

    def get_iter(self):
        if not self.request:
            return self.connect()
        return self.request

app = Flask(__name__)



socketio = SocketIO(app, cors_allowed_origins="*")
logging.basicConfig(level=logging.DEBUG)
last_chunk = ""


def sendframe():
    with requests.get("http://visage-cam.local/", stream=True) as r:
        for chunk in r.raw.read_chunked():
            if(len(chunk) > 100):
                global last_chunk
                last_chunk = chunk
                # socketio.emit('client', chunk)
                socketio.emit('client', str(base64.b64encode(chunk))[2:-1])

#routes
@app.route("/lock_door")
def handle_door():
    # r = requests.post('http://visage-lock.local/lock_door', json=request.json(), headers={'Content-Type': 'application/json'})
    print(request.get_json())
    return { 'lock' : 'unlock' }

@app.route("/send_chunk")
def send_chunk():
    return {'image': str(last_chunk) }

@app.route("/test")
def test():
    return {'message': "hello world!"}


#socket events
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    socketio.start_background_task(target=sendframe)

@socketio.on('test')
def test_event(data):
    socketio.emit('test', "test")
    print(data)


@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)