import socketio
from io import BytesIO
from PIL import Image
from time import sleep
import requests
import ast

server_url = 'http://127.0.0.1:8002'

sio = socketio.SimpleClient()
sio.connect(server_url)

print("Client connected to server.")
sleep(1)

while True:
    raw_image = requests.get(f'{server_url}/send_chunk')
    image = Image.open(BytesIO(ast.literal_eval(raw_image.json()['image'])))
    image.save('./Facenet_Facial_Recognition/frames/frame.jpeg')
    response = requests.get('http://visage-hub.local:8001/facial_recognition/classify')

    for indentity in response.json()['identities']:
            print(indentity)
            if indentity == 'No Faces Detected':
                print('No Faces Detected')
            elif indentity == 'Unknwon':
                print('Unfriendly Face Detected')
            elif indentity != 'Unknwon':
                door_status = {"lock": "unlock"}
                r = requests.post('http://visage-lock.local:80/lock_door', json=door_status, headers={'Content-Type': 'application/json'})
                print(f'{indentity[0]} unlocked door')
                sleep(10)
                door_status = {"lock": "lock"}
                r = requests.post('http://visage-lock.local:80/lock_door', json=door_status, headers={'Content-Type': 'application/json'})
                print(f'{indentity[0]} locked door')
