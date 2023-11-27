import sqlite3
import sys

from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QPixmap, QIcon, QStandardItem, QStandardItemModel, QDoubleValidator, QRegExpValidator
from PyQt5.QtCore import Qt, QRegExp, QDate

from PyQt5.QtWidgets import QMainWindow, QMessageBox, QVBoxLayout

import Category_view
import Delivery_view
import Products_view
import Suppliers_view
import main
from model.model import Model



class DeliveryData(QMainWindow):
    def __init__(self, *args):
        super(DeliveryData, self).__init__()
        uic.loadUi('Screens/table_data.ui', self)
        self.setWindowTitle('Поставки')
        self.args = args
        self.setMinimumSize(1120, 800)
        self.label.setText('Поставки')
        self.tableView = self.findChild(QtWidgets.QTableView, 'tableView')
        self.table_model = QStandardItemModel()
        self.tableView.setModel(self.table_model)
        self.pushButton.clicked.connect(self.add_new_category)
        self.tableView.doubleClicked.connect(self.update_row)


        conn = Model().conn
        cur = conn.cursor()
        cur.execute("""
                    select delivery_id, s.store_name, sp.SupplierName, p.ProductName, quantity, delivery_date
                    from Deliveries d
                        join Stores s on d.store_id = s.store_id
                        join Suppliers sp on d.supplier_id = sp.SupplierID
                        join Products p on d.product_id = p.ProductID
                """)
        data = cur.fetchall()
        cur.execute("PRAGMA table_info(Deliveries)")
        column_data = cur.fetchall()
        self.load_data(data, column_data)

        self.pushButton_3.clicked.connect(self.exit)

        self.tableView.doubleClicked.connect(self.update_row)

    def update_row(self, index):
        row = index.row()
        id_row = self.table_model.item(row, 0).text()
        self.upda = UpdateData(self.args[0], id_row)
        self.upda.show()
        self.hide()

    def add_new_category(self):
        self.add = AddDelivery(self.args[0])
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


class AddDelivery(QMainWindow):
    def __init__(self, *args):
        super(AddDelivery, self).__init__()
        self.args = args
        uic.loadUi('Screens/add_delivery.ui', self)
        self.setWindowTitle('Добавление новой поставки')

        self.label.setText('Добавить новую поставку')
        self.label_2.hide()
        self.label_5.hide()
        self.pushButton_3.hide()
        regex = QRegExp("[0-9]+")
        validator = QRegExpValidator(regex)
        self.lineEdit_2.setValidator(validator)

        self.load_comboBox()

        self.pushButton.clicked.connect(self.add_new_data_to_db)
        self.pushButton_2.clicked.connect(self.exit)

    def update_row(self, index):
        row = index.row()
        id_row = self.table_model.item(row, 0).text()
        id_name = self.table_model.horizontalHeaderItem(0).text()

        self.update = UpdateData(id_row, id_name, self.args[0])
        self.update.show()
        self.hide()


    def load_comboBox(self):
        conn = Model().conn
        cur = conn.cursor()

        self.comboBox_store = self.findChild(QtWidgets.QComboBox, 'comboBox')
        cur.execute("select location from Stores")
        data = [item[0] for item in cur.fetchall()]
        self.comboBox_store.addItems(data)

        self.comboBox_suppliers = self.findChild(QtWidgets.QComboBox, 'comboBox_2')
        cur.execute("select SupplierName from Suppliers")
        data = [item[0] for item in cur.fetchall()]
        self.comboBox_suppliers.addItems(data)

        self.comboBox_product = self.findChild(QtWidgets.QComboBox, 'comboBox_3')
        cur.execute("select ProductName from Products")
        data = [item[0] for item in cur.fetchall()]
        self.comboBox_product.addItems(data)


    def add_new_data_to_db(self):
        conn = Model().conn
        cur = conn.cursor()

        store_addres = self.comboBox_store.currentText()
        supplier = self.comboBox_suppliers.currentText()
        product = self.comboBox_product.currentText()
        quantity = self.lineEdit_2.text()
        date_travle = self.dateEdit.text()

        cur.execute("select store_id from Stores where location = ?", (store_addres,))
        id_store = cur.fetchone()[0]
        cur.execute("select SupplierID from Suppliers where SupplierName = ?", (supplier,))
        id_supplier = cur.fetchone()[0]
        cur.execute("select ProductID from Products where ProductName = ?", (product,))
        id_product = cur.fetchone()[0]

        if quantity == '':
            self.label_5.setText('Не все поля заполнены')
            self.label_5.show()
            return

        data_insert = {
            'store_id': id_store,
            'supplier_id': id_supplier,
            'product_id': id_product,
            'quantity': quantity,
            'delivery_date': date_travle,
        }

        try:
            cur.execute("""
                INSERT INTO Deliveries (store_id, supplier_id, product_id, quantity, delivery_date)
                VALUES (:store_id, :supplier_id, :product_id, :quantity, :delivery_date)
            """, data_insert)
            conn.commit()
            QMessageBox.information(self, 'Успех', 'Данные успешно добавлены', QMessageBox.Ok)
            self.exit()
        except conn.Error as er:
            QMessageBox.information(self, 'Провал', 'Произошла ошибка вставки данных, попробуйте поменять '
                                                'данные или не использовать сложные символы', QMessageBox.Ok)


    def exit(self):
        self.data = DeliveryData(self.args[0])
        self.data.show()
        self.hide()


class UpdateData(QMainWindow):
    def __init__(self,username, id_row):
        super(UpdateData, self).__init__()
        self.id_row = id_row
        self.username = username
        uic.loadUi('Screens/add_delivery.ui', self)
        self.setWindowTitle('Обновления доставки')

        self.label.setText('Обновить доставку')
        self.label_2.setText('')
        self.label_5.hide()
        regex = QRegExp("[0-9]+")
        validator = QRegExpValidator(regex)
        self.lineEdit_2.setValidator(validator)

        self.load_combobox()

        conn = Model().conn
        cur = conn.cursor()
        cur.execute("""
            select delivery_id, s.store_name, sp.SupplierName, p.ProductName, quantity, delivery_date
                    from Deliveries d
                        join Stores s on d.store_id = s.store_id
                        join Suppliers sp on d.supplier_id = sp.SupplierID
                        join Products p on d.product_id = p.ProductID
                    where delivery_id = ?
        """, (id_row,))
        data = cur.fetchone()
        self.upload_data(data)
        self.pushButton.setText('Обновить')
        self.pushButton.clicked.connect(self.update_data)
        self.pushButton_2.clicked.connect(self.exit)
        self.pushButton_3.clicked.connect(self.delete_data)

    def load_combobox(self):
        conn = Model().conn
        cur = conn.cursor()

        self.comboBox_store = self.findChild(QtWidgets.QComboBox, 'comboBox')
        cur.execute("select location from Stores")
        data = [item[0] for item in cur.fetchall()]
        self.comboBox_store.addItems(data)

        self.comboBox_suppliers = self.findChild(QtWidgets.QComboBox, 'comboBox_2')
        cur.execute("select SupplierName from Suppliers")
        data = [item[0] for item in cur.fetchall()]
        self.comboBox_suppliers.addItems(data)

        self.comboBox_product = self.findChild(QtWidgets.QComboBox, 'comboBox_3')
        cur.execute("select ProductName from Products")
        data = [item[0] for item in cur.fetchall()]
        self.comboBox_product.addItems(data)
    def delete_data(self):
        conn = Model().conn
        cur = conn.cursor()
        try:
            cur.execute("""
                DELETE FROM Deliveries
                WHERE delivery_id = ?
            """, (self.id_row,))
            conn.commit()
            QMessageBox.information(self, 'Успех', 'Запись успешно удалена', QMessageBox.Ok)
            self.exit()
        except conn.Error as e:
            QMessageBox.information(self, 'Провал', 'Невозможно удалить запись', QMessageBox.Ok)

    def update_data(self):
        conn = Model().conn
        cur = conn.cursor()

        store_addres = self.comboBox_store.currentText()
        supplier = self.comboBox_suppliers.currentText()
        product = self.comboBox_product.currentText()
        quantity = self.lineEdit_2.text()
        date_travle = self.dateEdit.text()

        cur.execute("select store_id from Stores where location = ?", (store_addres,))
        id_store = cur.fetchone()[0]
        cur.execute("select SupplierID from Suppliers where SupplierName = ?", (supplier,))
        id_supplier = cur.fetchone()[0]
        cur.execute("select ProductID from Products where ProductName = ?", (product,))
        id_product = cur.fetchone()[0]

        if quantity == '':
            self.label_5.setText('Не все поля заполнены')
            self.label_5.show()
            return

        data_insert = {
            'store_id': id_store,
            'supplier_id': id_supplier,
            'product_id': id_product,
            'quantity': quantity,
            'delivery_date': date_travle,
        }

        try:
            cur.execute(f"""
                UPDATE Deliveries
                SET store_id = :store_id, supplier_id = :supplier_id, product_id = :product_id,
                    quantity = :quantity, delivery_date = :delivery_date
                WHERE delivery_id = {self.id_row}
            """, data_insert)
            conn.commit()
            QMessageBox.information(self, 'Успех', 'Данные успешно добавлены', QMessageBox.Ok)
            self.exit()
        except conn.Error as er:
            QMessageBox.information(self, 'Провал', 'Произошла ошибка вставки данных, попробуйте поменять '
                                                    f'данные или не использовать сложные символы{er}', QMessageBox.Ok)

    def replace_comma(self, value):
        if isinstance(value, float):
            return str(value).replace('.', ',')
        return value
    def upload_data(self, data):
        self.label_2.setText(f'Номер записи - {data[0]}')
        self.comboBox.setCurrentText(data[1])
        self.comboBox_2.setCurrentText(data[2])
        self.comboBox_3.setCurrentText(data[3])
        self.lineEdit_2.setText(str(data[4]))
        date_object = QDate.fromString(data[5], 'yyyy-MM-dd')
        self.dateEdit.setDate(date_object)


    def exit(self):
        self.data = DeliveryData(self.username)
        self.data.show()
        self.hide()