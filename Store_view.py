import sqlite3
import sys

from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QPixmap, QIcon, QStandardItem, QStandardItemModel
from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import QMainWindow, QMessageBox, QVBoxLayout

import Category_view
import Delivery_view
import Products_view
import Suppliers_view
import main
from model.model import Model


class StoreData(QMainWindow):
    def __init__(self, *args):
        super(StoreData, self).__init__()
        uic.loadUi('Screens/table_data.ui', self)
        self.setWindowTitle('Магазины')
        self.args = args
        self.setMinimumSize(1120, 800)
        self.label.setText('Магазины')
        self.tableView = self.findChild(QtWidgets.QTableView, 'tableView')
        self.table_model = QStandardItemModel()
        self.tableView.setModel(self.table_model)
        self.pushButton.clicked.connect(self.add_new_category)

        conn = Model().conn
        cur = conn.cursor()
        cur.execute("""
                    select * from Stores
                """)
        data = cur.fetchall()
        cur.execute("PRAGMA table_info(Stores)")
        column_data = cur.fetchall()
        self.load_data(data, column_data)

        self.pushButton_3.clicked.connect(self.exit)

        self.tableView.doubleClicked.connect(self.update_row)

    def add_new_category(self):
        self.add = AddStore(self.args[0])
        self.add.show()
        self.hide()

    def load_data(self, data, column_data):
        column_data = [item[1] for item in column_data]
        self.table_model.setHorizontalHeaderLabels(column_data)

        for index_row, data_row in enumerate(data):
            for index_column, data_column in enumerate(column_data):
                item = QStandardItem(str(data_row[index_column]))
                item.setFlags(item.flags() | Qt.ItemIsEnabled)
                self.table_model.setItem(index_row, index_column, item)

    def exit(self):
        self.profile = main.Profile(self.args[0])
        self.profile.show()
        self.hide()



class AddStore(QMainWindow):
    def __init__(self, *args):
        super(AddStore, self).__init__()
        self.args = args
        uic.loadUi('Screens/add_store.ui', self)
        self.setWindowTitle('Добавление нового магазина')

        self.label.setText('Добавить новый магазин')
        self.pushButton.hide()
        self.label_2.hide()
        self.lineEdit.setPlaceholderText('Название магазина')
        self.lineEdit_2.setPlaceholderText('Адрес')

        self.pushButton_2.clicked.connect(self.add_store)
        self.pushButton_3.clicked.connect(self.exit)

    def add_store(self):
        conn = Model().conn
        cur = conn.cursor()
        store_name = self.lineEdit.text()
        store_addres = self.lineEdit_2.text()
        if store_name == '' and store_addres == '':
            self.label_2.setText('* Не все поля заполнены')
            self.label_2.show()
        else:
            cur.execute("select store_id from Stores where location = ?", (store_addres,))
            if cur.fetchone() is None:
                name_store = 'store_name'
                name_addres = 'location'
                try:
                    cur.execute(
                        f"INSERT INTO Stores({name_store}, {name_addres}) VALUES ('{store_name}', '{store_addres}')")
                    conn.commit()
                    QMessageBox.information(self, 'Успех', 'Магазин добавлен', QMessageBox.Ok)
                    self.exit()
                except conn.Error as er:
                    QMessageBox.information(self, 'Провал', f'Ошибка добавления нового магазина{er}')
            else:
                self.label_2.setText('Такой адрес уже есть')
                self.label_2.show()

    def exit(self):
        self.dat = Delivery_view.DeliveryData(self.args[0])
        self.dat.show()
        self.hide()