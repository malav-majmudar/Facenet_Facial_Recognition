import os
import json
import pickle
import socketio
import numpy as np
from io import BytesIO
from PIL import Image
from time import sleep
from keras import models
from helpers import face_detection
from collections import defaultdict
from flask import Blueprint, request

model = models.load_model('./models/facenet_keras.h5')

face_recognition = Blueprint('face_recognition', __name__)

@face_recognition.route('/add_user', methods = ['POST'])
def add_face():

    name = json.loads(request.form['json'])['name']
    image = request.files['image']

    name_dir = f'./train_raw/{name}/'

    if not os.path.exists(name_dir):
        os.makedirs(name_dir)

    image_path = name_dir + image.filename
    image.save(image_path)

    try:
        with open('./data/registered_faces.pkl', 'rb') as f:
            registered_faces = pickle.load(f)
        f.close()
    except:
        registered_faces = defaultdict(dict)

    face = face_detection.extract_face(image_path)

    if face is not None:
        registered_faces[name]['face_pixels'] = face
        face_embedding = face_detection.get_embedding(model, face)
        registered_faces[name]['face_embedding'] = face_embedding
    else:
        return f"{name} NOT Added", 400
    
    with open('./data/registered_faces.pkl', 'wb') as f:
        pickle.dump(registered_faces, f)
    f.close()


    return f"{name} Added", 201


@face_recognition.route('/remove_user', methods = ['POST'])
def sign_out():
    name = request.json['name']
    with open('./data/registered_faces.pkl', 'rb') as f:
        registered_faces = pickle.load(f)
    f.close()

    del registered_faces[name]

    with open('./data/registered_faces.pkl', 'wb') as f:
        pickle.dump(registered_faces, f)
    f.close()

    return f'{name} Removed', 200


@face_recognition.route('/classify', methods = ['POST'])
def classify_face():
    image = request.files['image']

    image_path = './frames/' + image.filename
    image.save(image_path)

    faces = face_detection.extract_faces(image_path)

    if faces is None:
        return 'No Faces Detected'
    
    with open('./data/registered_faces.pkl', 'rb') as f:
        registered_faces = pickle.load(f)
    f.close()

    identities = []
    for face in faces:
        unknown_embedding = face_detection.get_embedding(model, face)
        print(len(unknown_embedding))

        identity = None
        distances = []
        min_distance = float('inf')

        for name, face_data in registered_faces.items():
            distance = np.linalg.norm(unknown_embedding - face_data['face_embedding'])
            print(distance)
            distances.append(-distance)
            if distance < min_distance:
                min_distance = distance
                identity = name
        
        if min_distance < 10:
            prob = round((np.exp(-min_distance) /  np.exp(distances).sum(axis=0)) * 100, 4)
            identity = (identity, prob)
            print(identity)
        else:
            identity = 'Unknown'
            print(identity)

        identities.append(identity)

    return identities

@face_recognition.route('get_frame')
def get_frame():

    sio = socketio.SimpleClient()
    sio.connect('https://low-issue-vocals-msgid.trycloudflare.com/')

    io = BytesIO()

    count = 150
    i = 0
    while(True):
        data = sio.receive()[1]
        if count == 0:
            io.write(data)
            image = Image.open(io)
            image.save(f'./dumbass/{i}.png')
            i += 1
            count = 150
            io = BytesIO()
        count -= 1
        