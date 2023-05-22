from PyQt5.QtCore import QRunnable, QThreadPool
import face_recognition
import pandas as pd
import numpy as np
import itertools
import cv2
import os


# 1. Subclass QRunnable
class Runnable(QRunnable):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.result = []

    def run(self):
        probabilities = []
        face1, face2, folder1, folder2, image_name1, image_name2 = self.data
        distance = face_recognition.face_distance(face1, face2)
        if len(distance) != 0:
            similarity = 1 - distance[0]
            probabilities.append([folder1, folder2, image_name1, image_name2, similarity])

        self.result = probabilities


class Runnable_folders(QRunnable):
    def __init__(self, folders, dict):
        super().__init__()
        self.folders = folders
        self.dict = dict
        self.result = []

    def run(self):
        for folder1, folder2 in self.folders:

            if len(self.dict[folder1]) != 0 and len(self.dict[folder2]) != 0:
                for name_ind1, face1 in enumerate(self.dict[folder1]):
                    for name_ind2, face2 in enumerate(self.dict[folder2]):
                        image_name1 = f'face_{name_ind1 + 1}'
                        image_name2 = f'face_{name_ind2 + 1}'
                        self.result.append([face1, face2, folder1, folder2, image_name1, image_name2])


from PyQt5.QtCore import QThread, QCoreApplication
def check_tread():
    current_thread = QThread.currentThread()
    main_thread = QCoreApplication.instance().thread()
    if current_thread == main_thread:
        print("Основной поток активен")
    else:
        print("Основной поток неактивен")


def face_comparison2(faces_dict):
    photos_names = list(faces_dict)

    # получаем все возможные комбинации папок
    photos_combinations = list(itertools.combinations(photos_names, 2))

    # итерируемся по всем комбинациям папок
    probabilities = []
    preprocessed_data = []

    # Создаем и запускаем потоки
    threadpool = QThreadPool.globalInstance()
    runnables = []
    iter = 0

    while iter < len(photos_combinations):
        iter_end = min(iter + 5, len(photos_combinations) - 1)
        runnable = Runnable_folders(photos_combinations[iter:iter_end], faces_dict)
        runnables.append(runnable)
        threadpool.start(runnable)
        iter += 5

    # Дожидаемся завершения всех потоков
    threadpool.waitForDone()

    # Собираем результаты из каждого потока
    for runnable in runnables:
        preprocessed_data.extend(runnable.result)

    # Создаем пул потоков
    threadpool = QThreadPool.globalInstance()

    # Создаем и запускаем потоки
    runnables = []
    #data_len = len(preprocessed_data)
    for item in preprocessed_data:
        runnable = Runnable(item)
        runnables.append(runnable)
        threadpool.start(runnable)

    # Дожидаемся завершения всех потоков
    threadpool.waitForDone()
    # Собираем результаты из каждого потока
    for runnable in runnables:
        probabilities.extend(runnable.result)
    return sorted(probabilities, key=lambda x: x[4], reverse=True)
