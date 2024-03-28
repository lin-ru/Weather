import sys

from PyQt5 import uic, QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QBrush, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QHeaderView, QDesktopWidget

import requests
import formui
from datetime import datetime

from child import MyThread


class App(QMainWindow,  formui.Ui_MainWindow):

    def __init__(self):
        super().__init__()
        try:
            open('saved.wp', 'x')
        except IOError:
            f = open('saved.wp')
            self.loadPropertieFromSavedFile = f.readlines()
        f.close()


        # uic.loadUi('form2+.ui', self)

        self.setupUi(self)


        self.buttonrequest.clicked.connect(self.requestWeather)
        self.input_city.returnPressed.connect(self.requestWeather)
        self.input_city.textChanged.connect(self.setDefaultStyle)
        self.input_city.setToolTip("Введите город")
        self.city_not_found.setHidden(True)
        self.setWindowIcon(QtGui.QIcon('logo.ico'))
        if not len(self.loadPropertieFromSavedFile)==0:
            self.city_name = self.loadPropertieFromSavedFile[0].strip('\n') #"Санкт-Петербург"
        else:
            self.city_name = 'Санкт-Петербург'

        self.x = 0
        self.title = ('О погоде')
        self.left = 0
        self.top = 0
        self.width = 750
        self.height = 460
        self.setWindowTitle(self.title)
        self.table_cast.setGeometry(QtCore.QRect(5, 301, 740, 155))
        self.setGeometry(self.left, self.top, self.width, self.height)
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        #запуск потока для вывода времени и запроса погоды
        self.my_thread = MyThread()
        self.my_thread.my_signal.connect(self.showtime)  # count_timer()
        self.count_timer()

    def count_timer(self):
        self.my_thread.start()

    def showtime(self, num):
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        # print("Current Time =", current_time)
        self.cur_time.setText(str(current_time))
        if num == 0:
            self.requestWeather()
    def setDefaultStyle(self):
        self.input_city.setStyleSheet("QLineEdit {}")
        self.input_city.setToolTip("Введите город")
        self.city_not_found.setHidden(True)


    def fillTable(self, tableAr):
        self.table_cast.setColumnCount(4)  # We install 4 columns
        self.table_cast.setRowCount(4)  # and 4 row in the table
        header = self.table_cast.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
# Set table headers

        tableAr[4].insert(0,"")
        self.table_cast.setHorizontalHeaderLabels(tableAr[4])
        header.setStyleSheet("::section{font: bold 12pt 'Open Sans';}")

# Set the alignment to the headers
        self.table_cast.horizontalHeaderItem(0).setTextAlignment(Qt.AlignHCenter)
        self.table_cast.horizontalHeaderItem(1).setTextAlignment(Qt.AlignHCenter)
        self.table_cast.horizontalHeaderItem(2).setTextAlignment(Qt.AlignHCenter)

# fill the first line
        self.table_cast.setItem(0, 0, self.createItemDescription("Температура", Qt.ItemIsSelectable | Qt.ItemIsEnabled))
        self.table_cast.setItem(1, 0, self.createItemDescription("Давление", Qt.ItemIsSelectable | Qt.ItemIsEnabled))
        self.table_cast.setItem(2, 0, self.createItemDescription("Скорость ветра", Qt.ItemIsSelectable | Qt.ItemIsEnabled))
        self.table_cast.setItem(3, 0, self.createItemDescription("Погода", Qt.ItemIsSelectable | Qt.ItemIsEnabled))
        for y in range(3):
            self.table_cast.setItem(0, y+1, self.createItem(tableAr[0][y], Qt.ItemIsSelectable | Qt.ItemIsEnabled))
            self.table_cast.setItem(1, y+1, self.createItem(tableAr[1][y], Qt.ItemIsSelectable | Qt.ItemIsEnabled))
            self.table_cast.setItem(2, y + 1, self.createItem(tableAr[2][y], Qt.ItemIsSelectable | Qt.ItemIsEnabled))
            self.table_cast.setItem(3, y + 1, self.createItem(tableAr[3][y], Qt.ItemIsSelectable | Qt.ItemIsEnabled))
            self.table_cast.setItem(4, y + 1, self.createItem(tableAr[3][y], Qt.ItemIsSelectable | Qt.ItemIsEnabled))

# do column resizing by content
        self.table_cast.resizeColumnsToContents()
        self.table_cast.resizeRowsToContents()

    def createItem(self, text, flags):
        tableWidgetItem = QTableWidgetItem(text)
        font = QFont("Arial", 11, QFont.Bold)
        tableWidgetItem.setFont(font)
        # tableWidgetItem.setFlags(flags)
        tableWidgetItem.setTextAlignment(Qt.AlignCenter)
        return tableWidgetItem

    def createItemDescription(self, text, flags):
        tableWidgetItem = QTableWidgetItem(text)
        font = QFont("Arial", 11, QFont.Bold)
        tableWidgetItem.setFont(font)
        tableWidgetItem.setForeground(QBrush(QColor(60,60,60)))

        tableWidgetItem.setTextAlignment(Qt.AlignLeft)
        return tableWidgetItem

    def requestWeather(self):
        API = '7b5e9d8d9e2c85dbb0409d501e397be5'
        city_name = self.input_city.text().strip()
        if len(city_name) < 1: #check when input field is empty
            city_name =  self.city_name
        URL = f'https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API}&units=metric&lang=ru'
        result = requests.get(URL).json()
        if int(result['cod']) == 404: #check when name of city is not exist in db openweathermap.com service
            self.check_address()
            # print(result['cod'])
            return
        self.city_name=city_name
        self.saveCityToFile(self.city_name)

        temp = round(result['main']['temp'])
        wind_speed = result['wind']['speed']
        weather_summ = result['weather'][0]['description']
        pressuref = float(result['main']['pressure'])
        pressure = (pressuref / 1.333)
        pressureStr = round(pressure)
        # print(result)
        self.result_city.setText(' ' + city_name)
        self.result_temp.setText(' ' + str(temp) + ' °C')
        self.result_pressure.setText(' ' + str(pressureStr) + ' мм рт/ст')
        self.result_speed.setText(' ' + str( round(wind_speed, 1)) + ' м/с')
        self.result_city_summ.setText(str(weather_summ))
        lon = str(result['coord']['lon'])
        lat = str(result['coord']['lat'])
        self.request_forecast(lon, lat)

    def check_address(self):
        self.input_city.selectAll()
        self.input_city.setStyleSheet("QLineEdit {border-color: rgb(255, 10, 10); border-style: solid; border-width: 2px;}")
        self.input_city.setToolTip("Город не найден")
        self.city_not_found.setHidden(False)

    def saveCityToFile(self, saved_sity):
        f = open('saved.wp', 'w')
        f.write(saved_sity)
        f.close()

    def request_forecast(self, lon, lat):
        API = 'a3524510eee098b063777481b8c92139'

        URL = f'https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API}&units=metric&lang=ru&cnt=3'
        result = requests.get(URL).json()

        tableAr = [[] for i in range(5)]
        for y in range(3):
                tableAr[0].append(str((round(result['list'][y]['main']['temp']))) + ' °C')
                tableAr[1].append(str(round(float(result['list'][y]['main']['pressure'])/1.333)) + ' мм рт/ст')
                tableAr[2].append(str(round(result['list'][y]['wind']['speed'], 1)) + ' м/с')
                tableAr[3].append(str(result['list'][y]['weather'][0]['description']))
                tableAr[4].append(str(result['list'][y]['dt_txt']))
        self.fillTable(tableAr)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec())

