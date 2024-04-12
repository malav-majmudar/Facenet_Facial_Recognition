import os
import json
import pickle
import numpy as np
from keras import models
from helpers import face_detection
from collections import defaultdict
from flask import Blueprint, request
from PIL import Image
import io
import base64

model = models.load_model('./models/facenet_keras.h5')

face_recognition = Blueprint('face_recognition', __name__)

@face_recognition.route('/get_users', methods = ['GET'])
def get_users():
    try:
        with open('./data/registered_faces.pkl', 'rb') as f:
            registered_faces = pickle.load(f)
        f.close()
    except:
        return {'message': 'No Users Found'}, 404
    
    users = {}
    for name in registered_faces:
        users[name] = registered_faces[name]['face_pixels']
    
    return users, 200

@face_recognition.route('/add_user', methods = ['POST'])
def add_face():

    name = json.loads(request.form['json'])['name']
    image = request.files['image']

    name_dir = f'./train_raw/{name}/'

    if not os.path.exists(name_dir):
        os.makedirs(name_dir)

    if not os.path.exists('./data'):
        os.makedirs('./data')

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
        face_embedding = face_detection.get_embedding(model, face)
        registered_faces[name]['face_embedding'] = face_embedding

        face = Image.fromarray(face)
        binary_stream = io.BytesIO()
        face.save(binary_stream, format='JPEG')
        byte_data = binary_stream.getvalue()
        base64_encoded_string = base64.b64encode(byte_data).decode('utf-8')
        registered_faces[name]['face_pixels'] = base64_encoded_string

    else:
        return f"{name} NOT Added", 400
    
    with open('./data/registered_faces.pkl', 'wb') as f:
        pickle.dump(registered_faces, f)
    f.close()


    return f"{name} Added", 201


@face_recognition.route('/remove_user', methods = ['POST'])
def remove_user():
    name = request.json['name']
    with open('./data/registered_faces.pkl', 'rb') as f:
        registered_faces = pickle.load(f)
    f.close()

    del registered_faces[name]

    with open('./data/registered_faces.pkl', 'wb') as f:
        pickle.dump(registered_faces, f)
    f.close()

    return f'{name} Removed', 200


@face_recognition.route('/classify', methods = ['GET'])
def classify_face():

    faces = face_detection.extract_faces('./frames/frame.jpeg')

    if faces is None:
        return {'identities': [('No Faces Detected')]}
    
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
        
        if min_distance < 12:
            prob = round((np.exp(-min_distance) /  np.exp(distances).sum(axis=0)) * 100, 4)
            identity = (identity, prob)
            print(identity)
        else:
            identity = ('Unknown')
            print(identity)

        identities.append(identity)

    return {'identities': identities}