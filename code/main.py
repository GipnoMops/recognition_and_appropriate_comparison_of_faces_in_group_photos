from PyQt5.QtWidgets import QMainWindow, QLabel, QApplication, QFileDialog, QTableWidgetItem, QWidget, QVBoxLayout, QInputDialog
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtCore import QThread, QCoreApplication
from PyQt5.QtGui import QPixmap
from PyQt5 import QtCore
from openpyxl import Workbook
from interface9 import Ui_MainWindow
from selection_persons import selection_persons
from face_comparison import face_comparison2
import threading
import sys
import os
import copy
import sqlite3
import numpy as np
import face_recognition

import time
from time import sleep

class Worker2(QObject):
    def __init__(self, path, output_path):
        super().__init__()
        self.path = path
        self.output_path = output_path
    finished = pyqtSignal()
    progressChanged = pyqtSignal(int)
    for_faces_dict = pyqtSignal(str, list)
    for_QStackedWidget = pyqtSignal(str)
    encoding = pyqtSignal()
    #progress = pyqtSignal(int)

    def run(self):
        self.progressChanged.emit(0)
        num_of_files = len(os.listdir(self.path))
        for i, file_name in enumerate(os.listdir(self.path)):

            # Устанавливаем значение прогресс-бара
            #self.progressChanged.emit(int(((i + 1) / num_of_files) * 100))

            # формируем полный путь к файлу
            full_path = os.path.normpath(os.path.join(self.path, file_name))
            """
                Функция cv2.imread() из библиотеки OpenCV может считывать изображения в различных форматах. Вот некоторые из наиболее распространенных форматов, которые cv2.imread() может обрабатывать:

                JPEG/JPG: Файлы с расширением .jpeg или .jpg в формате Joint Photographic Experts Group (JPEG).

                PNG: Файлы с расширением .png в формате Portable Network Graphics (PNG).

                BMP: Файлы с расширением .bmp в формате Bitmap (BMP).

                TIFF/TIF: Файлы с расширением .tiff или .tif в формате Tagged Image File Format (TIFF).

                GIF: Файлы с расширением .gif в формате Graphics Interchange Format (GIF). Однако cv2.imread() обычно считывает только первый кадр из анимированных GIF-изображений.

                PSD: Файлы с расширением .psd в формате Adobe Photoshop Document (PSD).

                HDR: Файлы с расширением .hdr в формате High Dynamic Range (HDR).

                WEBP: Файлы с расширением .webp в формате WebP, разработанном Google.

                PBM, PGM, PPM: Файлы с расширениями .pbm, .pgm или .ppm в форматах Portable Bitmap, Portable Graymap или Portable Pixmap соответственно.

                И другие: OpenCV также поддерживает считывание изображений в других форматах, таких как EXR (OpenEXR), DNG (Digital Negative), и т. д.

                Важно отметить, что в зависимости от установленных библиотек и конфигурации OpenCV, поддерживаемые форматы могут варьироваться.
            """
            # проверяем, является ли файл файлом
            list_of_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.psd']
            if os.path.isfile(full_path) and (os.path.splitext(full_path)[1] in list_of_formats): #добавить и протестить другие форматы
                # делаем что-то с файлом
                faces_path, faces = selection_persons(full_path, self.output_path)

                encoding_faces = []
                for face in faces:
                    encoding_faces.append(np.array(face_recognition.face_encodings(face)))
                    self.encoding.emit()

                self.for_faces_dict.emit(file_name, encoding_faces)
                self.for_QStackedWidget.emit(faces_path)

            # Устанавливаем значение прогресс-бара
            self.progressChanged.emit(int(((i + 1) / num_of_files) * 100))
        self.finished.emit()
""""
                # Создаем новую страницу
                new_page = QWidget()

                # Создаем новый компонент QLabel и загружаем в него изображение
                label = QLabel(new_page)
                pixmap = QPixmap(faces_path)
                #уменьшаем размер картинки
                scaled_pixmap = pixmap.scaled(pixmap.width() // 2, pixmap.height() // 2, QtCore.Qt.KeepAspectRatio)
                label.setPixmap(scaled_pixmap)
                label.setAlignment(QtCore.Qt.AlignCenter)

                # Создаем компоновщик QVBoxLayout и добавляем QLabel в него
                layout = QVBoxLayout(new_page)
                layout.addWidget(label)

                # Устанавливаем компоновщик для новой страницы
                new_page.setLayout(layout)

                # Добавляем новую страницу в QStackedWidget
                self.ui.stackedWidget_2.addWidget(new_page)

                # Отображаем новую страницу
                #self.ui.stackedWidget_2.setCurrentWidget(new_page)

                self.list_of_photo.append(new_page)
                self.counter[1] += 1
            #print("обработка фото", time.time() - start_time)
"""""


class Worker(QObject):
    def __init__(self, faces_dict):
        super().__init__()
        self.faces_dict = faces_dict
    finished = pyqtSignal(list)
    #progress = pyqtSignal(int)

    def run(self):
        """Long-running task."""
        prob = face_comparison2(self.faces_dict)
        self.finished.emit(prob)


class MainWindow:
    def __init__(self):
        self.main_win = QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.main_win)
        self.list_of_photo = [] #можно поменять немного функции и удалить это, к тому же память меньше буду юзать
        self.counter = [0, 0]
        self.output_path = ""

        self.ui.pushButton_5.clicked.connect(self.showR)
        self.ui.pushButton_2.clicked.connect(self.showR2)
        self.ui.pushButton_3.clicked.connect(self.showTable)
        self.ui.pushButton.clicked.connect(self.open_file2)
        self.ui.pushButton_4.clicked.connect(self.showPhotos)
        self.ui.pushButton_7.clicked.connect(self.showPrev)
        self.ui.pushButton_6.clicked.connect(self.showNext)
        self.ui.comboBox.currentIndexChanged.connect(self.show_selected_photo)

        self.ui.progressBar.setMinimum(0)
        self.ui.progressBar.setMaximum(100)

        self.probabilitie = []
        self.faces_dict = {}
        self.thread1 = QThread()



    def open_file2(self):
        self.data_cleaner()
        self.ui.stackedWidget_2.setCurrentWidget(self.ui.page_3)
        path = QFileDialog.getExistingDirectory(self.ui.frame_2, 'Open file', 'C:/Users/Asus/Desktop/HSE/course_work3/code/photos')#"/User")#, 'Data File (*.dat *.asc *.txt)')
        if path:
            self.output_path = QFileDialog.getExistingDirectory(self.ui.frame_2, 'Сhoose a place to save output data')
            if self.output_path:
                self.output_path += "/output"
                self.output_folder()

                self.ui.pushButton.setEnabled(False)  # не позволяет нажать снова кнопку
                self.ui.pushButton_7.setEnabled(False)
                self.ui.pushButton_6.setEnabled(False)
                #self.way = path # нигде не используется
                self.thread = QThread()
                self.worker = Worker2(path, self.output_path)
                self.worker.moveToThread(self.thread)
                # Step 5: Connect signals and slots
                self.thread.started.connect(self.worker.run)
                self.worker.progressChanged.connect(self.update_progress_bar)
                self.worker.for_faces_dict.connect(self.update_faces_dict)
                self.worker.encoding.connect(self.upd_interface)
                self.worker.for_QStackedWidget.connect(self.update_QStackedWidget)

                #self.worker.progress.connect(self.reportProgress)
                self.thread.start()

                # Дождаться окончания работы потока
                self.worker.finished.connect(self.when_finished)
                self.worker.finished.connect(self.thread.quit)
                self.worker.finished.connect(self.worker.deleteLater)
                self.thread.finished.connect(self.thread.deleteLater)
                # self.worker1.finished.connect(self.update_cur_photo)

            #self.ui.pushButton.setEnabled(True) # нужно будет обработать это

    def output_folder(self):
        if os.path.exists(self.output_path):
            i = 1
            while os.path.exists(self.output_path + '_' + str(i)):
                i += 1
            self.output_path = self.output_path + '_' + str(i)


    def when_finished(self):
        self.ui.pushButton_7.setEnabled(True)
        self.ui.pushButton_6.setEnabled(True)
        if self.counter[1] != 0:
            self.update_cur_photo()
            self.ComboBox()
            self.start2()
        else:
            self.ui.pushButton.setEnabled(True)
            #можно добавить вывод окна "ни одной фотки не нашлось"


    def check_tread(self):
        current_thread = QThread.currentThread()
        main_thread = QCoreApplication.instance().thread()
        if current_thread == main_thread:
            print("Основной поток активен")
        else:
            print("Основной поток неактивен")


    def start2(self):
        #self.ui.stackedWidget_2.setCurrentWidget(self.list_of_photo[0])
        self.thread = QThread()
        self.worker = Worker(copy.deepcopy(self.faces_dict))
        self.worker.moveToThread(self.thread)
        # Step 5: Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.table)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        # self.worker.progress.connect(self.reportProgress)
        # Step 6: Start the thread
        #print("start2")
        self.thread.start()

        # Final resets

        self.thread.finished.connect(
            lambda: self.ui.pushButton.setEnabled(True)
        )
        self.thread.finished.connect(
            lambda: self.create_data_base()
        )
        self.thread.finished.connect(
            lambda: self.create_exel_file()
        )


    def data_cleaner(self):
        for qw in self.list_of_photo:
            qw.deleteLater()
        self.ui.tableWidget.clear()
        self.list_of_photo.clear()
        self.probabilitie.clear()
        self.ui.comboBox.clear()
        self.faces_dict.clear()
        self.counter = [0, 0]
        self.output_path = ""


    def show_selected_photo(self):
        if self.ui.comboBox.currentIndex() != -1:
            self.counter[0] = self.ui.comboBox.currentIndex()
            page = self.list_of_photo[self.counter[0]]
            self.ui.stackedWidget_2.setCurrentWidget(page)


    def ComboBox(self):
        names = list(self.faces_dict.keys())
        for name in names:
            self.ui.comboBox.addItem(name)


    def update_cur_photo(self):
        #if len(self.list_of_photo) != 0:
        self.ui.stackedWidget_2.setCurrentWidget(self.list_of_photo[0])
        QApplication.processEvents()


    def upd_interface(self):
        # Принудительно обновляем интерфейс, чтобы прогресс-бар обновлялся
        QApplication.processEvents()

    def update_progress_bar(self, value):
        self.ui.progressBar.setValue(value)
        # Принудительно обновляем интерфейс, чтобы прогресс-бар обновлялся
        QApplication.processEvents()

    def update_faces_dict(self, file_name, faces):
        self.faces_dict[file_name] = faces


    def update_QStackedWidget(self, faces_path):
        # Создаем новую страницу
        new_page = QWidget()

        # Создаем новый компонент QLabel и загружаем в него изображение
        label = QLabel(new_page)
        pixmap = QPixmap(faces_path)
        # корректируем размер картинки
        height = round(pixmap.height() * (550 / pixmap.width()))
        #scaled_pixmap = pixmap.scaled(pixmap.width() // 2, pixmap.height() // 2, QtCore.Qt.KeepAspectRatio)
        scaled_pixmap = pixmap.scaled(550, height, QtCore.Qt.KeepAspectRatio)
        label.setPixmap(scaled_pixmap)
        label.setAlignment(QtCore.Qt.AlignCenter)

        # Создаем компоновщик QVBoxLayout и добавляем QLabel в него
        layout = QVBoxLayout(new_page)
        layout.addWidget(label)

        # Устанавливаем компоновщик для новой страницы
        new_page.setLayout(layout)

        # Добавляем новую страницу в QStackedWidget
        self.ui.stackedWidget_2.addWidget(new_page)

        # Отображаем новую страницу
        # self.ui.stackedWidget_2.setCurrentWidget(new_page)

        self.list_of_photo.append(new_page)
        self.counter[1] += 1


    def create_data_base(self):
        database_path = os.path.join(self.output_path, 'database.db')
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS data (
            folder1 TEXT,
            folder2 TEXT,
            image_name1 TEXT,
            image_name2 TEXT,
            similarity REAL
        )''')
        cursor.executemany('INSERT INTO data VALUES (?, ?, ?, ?, ?)', self.probabilitie)
        conn.commit()
        conn.close()


    def create_exel_file(self):
        database_path = os.path.join(self.output_path, 'output.xlsx')

        # Создание нового файла Excel
        workbook = Workbook()
        sheet = workbook.active

        # Заполнение заголовков столбцов
        headers = ['Folder 1', 'Folder 2', 'Image Name 1', 'Image Name 2', 'Similarity']
        sheet.append(headers)

        # Заполнение данных из списка
        for row_data in self.probabilitie:
            sheet.append(row_data)

        # Сохранение файла
        workbook.save(database_path)


    def table(self, prob):
        self.probabilitie = prob
        #self.ui.tableWidget.clear()
        self.ui.tableWidget.setRowCount(len(self.probabilitie))
        self.ui.tableWidget.setColumnCount(5)

        for i in range(len(self.probabilitie)):
            self.ui.tableWidget.setItem(i, 0, QTableWidgetItem(self.probabilitie[i][0]))
            self.ui.tableWidget.setItem(i, 1, QTableWidgetItem(self.probabilitie[i][1]))
            self.ui.tableWidget.setItem(i, 2, QTableWidgetItem(self.probabilitie[i][2]))
            self.ui.tableWidget.setItem(i, 3, QTableWidgetItem(self.probabilitie[i][3]))
            self.ui.tableWidget.setItem(i, 4, QTableWidgetItem(str("{:.2f}".format(self.probabilitie[i][4]))))


    def showPrev(self):
        if self.counter[1] != 0:
            self.counter[0] = (self.counter[0] - 1) % self.counter[1]
            page = self.list_of_photo[self.counter[0]]
            self.ui.stackedWidget_2.setCurrentWidget(page)
            self.ui.comboBox.setCurrentIndex(self.counter[0])


    def showNext(self):
        if self.counter[1] != 0:
            self.counter[0] = (self.counter[0] + 1) % self.counter[1]
            page = self.list_of_photo[self.counter[0]]
            self.ui.stackedWidget_2.setCurrentWidget(page)
            self.ui.comboBox.setCurrentIndex(self.counter[0])


    def showPhotos(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_2)

    def showTable(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.table)

    def showR(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.rules_page)

    def showR2(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.page)

    def show(self):
        self.main_win.show()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())


#pyuic5 interface.py -o interface.ui -x

#pip install dlib-19.19.0-cp38-cp38-win_amd64.whl
#pyinstaller -F --noconsole main.py
#pyinstaller main.spec