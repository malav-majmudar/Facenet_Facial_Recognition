import socketio
from flask import Flask
from routes.auth.login import login
from routes.facial_recognition.face_recognition import face_recognition

app = Flask(__name__)

app.register_blueprint(login, url_prefix='/auth')
app.register_blueprint(face_recognition, url_prefix='/facial_recognition')


@app.route("/")
def hello_world():
    return "<h1>Hello, Malav!</h1>"


if __name__ == "__main__":
    app.run(port=8001, debug=True)