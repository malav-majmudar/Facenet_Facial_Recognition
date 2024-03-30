import numpy as np
import cv2
from PIL import Image
from mtcnn import MTCNN
from keras.models import load_model


def extract_face(file_name, required_size=(160, 160)):
    image = cv2.imread(file_name)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    pixels = np.asarray(image)

    detector = MTCNN()
    results = detector.detect_faces(pixels)

    if results:
        x1, y1, width, height = results[0]['box']
        x1, y1 = abs(x1), abs(y1)
        x2, y2 = x1 + width, y1 + height

        face = pixels[y1:y2, x1:x2]

        image = Image.fromarray(face)
        image = image.resize(required_size)

        return np.asarray(image)
    else:
        return None

def extract_faces(file_name, required_size=(160, 160)):
    image = cv2.imread(file_name)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    pixels = np.asarray(image)

    detector = MTCNN()
    detected_faces = detector.detect_faces(pixels)

    faces = []

    if not detected_faces:
        return None
    else:
        for face in detected_faces:
            if face['confidence'] >= 0.9:
                x1, y1, width, height = face['box']
                x1, y1 = abs(x1), abs(y1)
                x2, y2 = x1 + width, y1 + height

                face = pixels[y1:y2, x1:x2]

                image = Image.fromarray(face)
                image = image.resize(required_size)

                faces.append(np.asarray(image))
        return faces
    
def get_embedding(model, face_pixels):
    face_pixels = face_pixels.astype('float32')

    mean, std = face_pixels.mean(), face_pixels.std()
    face_pixels = (face_pixels - mean) / std
    
    samples = np.expand_dims(face_pixels, axis=0)

    return model.predict(samples)[0]

