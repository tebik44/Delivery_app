import sqlite3
import sys

from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QPixmap, QIcon, QStandardItem, QStandardItemModel
from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import QMainWindow, QMessageBox, QVBoxLayout

import Category_view
import Delivery_view
import Products_view
import Store_view
import Suppliers_view
from model.model import Model


class Login(QMainWindow):
    def __init__(self):
        super(Login, self).__init__()
        uic.loadUi('Screens/login.ui', self)
        self.setWindowTitle('Авторизация')
        self.label_2.hide()
        self.pushButton = self.findChild(QtWidgets.QPushButton, 'pushButton')

        self.pushButton.clicked.connect(self.log)

    def log(self):
        login = self.lineEdit.text()
        password = self.lineEdit_2.text()
        self.label_2.hide()
        conn = Model().conn
        cur = conn.cursor()
        cur.execute("select UserID, Login from User where Login = ? and Password = ?",
                    (login, password))
        respoune = cur.fetchone()
        if login == '' or password == '':
            self.label_2.setText('* Все поля должны быть заполнены')
            self.label_2.show()
            return
        elif respoune:
            QMessageBox.information(self, "Успех", f"Здравствуйте {respoune[1]},", QMessageBox.Ok)
            self.profile = Profile(respoune[1])
            self.profile.show()
            self.hide()

        else:
            self.label_2.setText("Пользователь не найден")
            self.label_2.show()


class Profile(QMainWindow):
    def __init__(self, *args):
        super(Profile, self).__init__()
        self.args = args
        uic.loadUi('Screens/profile.ui', self)
        self.setWindowTitle('Профиль')
        self.label_2.setAlignment(Qt.AlignCenter)
        self.label_2.setText(f'Профиль \n {args[0]}')


        self.pushButton_5.clicked.connect(self.exit)
        self.pushButton.clicked.connect(self.products)
        self.pushButton_2.clicked.connect(self.suppliers)
        self.pushButton_3.clicked.connect(self.category)
        self.pushButton_4.clicked.connect(self.devivery)
        self.pushButton_6.clicked.connect(self.store)


    def store(self):
        self.store = Store_view.StoreData(self.args[0])
        self.store.show()
        self.hide()

    def devivery(self):
        self.devivery = Delivery_view.DeliveryData(self.args[0])
        self.devivery.show()
        self.hide()

    def category(self):
        self.category = Category_view.CategoryData(self.args[0])
        self.category.show()
        self.hide()

    def suppliers(self):
        self.suppliers = Suppliers_view.SupplierData(self.args[0])
        self.suppliers.show()
        self.hide()
    def products(self):
        self.data = Products_view.ProductData(self.args[0])
        self.data.show()
        self.hide()


    def exit(self):
        self.login = Login()
        self.login.show()
        self.hide()




if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    # login = Products_view.ProductData()
    login = Login()
    login.show()
    sys.exit(app.exec_())