import cv2
import os
#import face_recognition
import numpy as np

def selection_persons(path, output_path):
    # Загружаем предобученную модель Haar Cascade Classifier
    #face_cascade = cv2.CascadeClassifier('C:/Users/Asus/Desktop/HSE/course_work3/code/haarcascade_frontalface_default.xml')
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    # Загружаем изображение
    img = cv2.imread(path)

    # Обнаруживаем лица на изображении
    faces = face_cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=5)

    photo_name = os.path.splitext(os.path.basename(path))[0]
    output = os.path.join(output_path, photo_name)
    if not os.path.exists(output):
        os.makedirs(output)

    desired_size = (800, 800)
    detected_faces = []

    # Сохраняем каждое обнаруженное лицо в отдельный файл
    for i, (x, y, w, h) in enumerate(faces):
        # Извлекаем область изображения, соответствующую лицу
        face_img = img[y:y + h, x:x + w]
        resized_face_img = cv2.resize(face_img, desired_size, interpolation=cv2.INTER_LINEAR)

        detected_faces.append(resized_face_img)

        # Сохраняем изображение лица в отдельный файл
        face_filename = f'face_{i + 1}.jpg'
        face_path = os.path.join(output, face_filename)
        cv2.imwrite(face_path, resized_face_img)

        # Отмечаем обнаруженные лица на исходном изображении
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

    # Сохраняем изображение с отмеченными лицами
    cv2.imwrite(os.path.join(output, 'faces.jpg'), img)
    return os.path.join(output, 'faces.jpg'), detected_faces
