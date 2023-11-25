from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QPixmap, QIcon, QStandardItem, QStandardItemModel, QDoubleValidator, QRegExpValidator
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QVBoxLayout

import main
from model.model import Model

class ProductData(QtWidgets.QMainWindow):
    def __init__(self, *args):
        super(ProductData, self).__init__()
        self.args = args
        uic.loadUi('Screens/table_data.ui', self)
        self.setWindowTitle('Товары')
        self.setMinimumSize(1120, 800)
        self.label.setText('Товары')
        self.tableView = self.findChild(QtWidgets.QTableView, 'tableView')
        self.table_model = QStandardItemModel()
        self.tableView.setModel(self.table_model)


        conn = Model().conn
        cur = conn.cursor()
        cur.execute("""
            select ProductID, ProductName, c.CategoryName, s.SupplierName, p.StockQuantity, p.UnitPrice
            from Products p
                join Suppliers s on p.SupplierID = s.SupplierID
                join Categories c on p.CategoryID = c.CategoryID
        """)
        data = cur.fetchall()
        cur.execute("PRAGMA table_info(Products)")
        column_data = cur.fetchall()
        self.load_data(data, column_data)

        self.pushButton_3.clicked.connect(self.exit)
        self.pushButton.clicked.connect(self.add_new_product)
        self.tableView.doubleClicked.connect(self.update_row)



    def update_row(self, index):
        row = index.row()
        id_row = self.table_model.item(row, 0).text()
        id_name = self.table_model.horizontalHeaderItem(0).text()

        self.update = UpdateData(id_row, id_name)
        self.update.show()
        self.hide()

    def add_new_product(self):
        self.add = AddProduct()
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
        self.profile = Profile(self.args[0])
        self.profile.show()
        self.hide()


class AddProduct(QMainWindow):
    def __init__(self, id_product=None):
        super(AddProduct, self).__init__()
        uic.loadUi('Screens/add_product.ui', self)
        self.setWindowTitle('Добавление нового товара')

        self.label.setText('Добавить новый продукт')
        self.label_2.hide()
        self.label_5.hide()
        self.pushButton_3.hide()
        double_validator = QDoubleValidator()
        double_validator.setDecimals(2)
        self.lineEdit_3.setValidator(double_validator)
        regex = QRegExp("[0-9]+")
        validator = QRegExpValidator(regex)
        self.lineEdit_2.setValidator(validator)

        self.load_comboBox()

        self.pushButton.clicked.connect(self.add_new_data_to_db)
        self.pushButton_2.clicked.connect(self.exit)




    def load_comboBox(self):
        conn = Model().conn
        cur = conn.cursor()

        self.comboBox_category = self.findChild(QtWidgets.QComboBox, 'comboBox')
        cur.execute("select CategoryName from Categories")
        data = [item[0] for item in cur.fetchall()]
        self.comboBox_category.addItems(data)

        self.comboBox_suppliers = self.findChild(QtWidgets.QComboBox, 'comboBox_2')
        cur.execute("select SupplierName from Suppliers")
        data = [item[0] for item in cur.fetchall()]
        self.comboBox_suppliers.addItems(data)


    def add_new_data_to_db(self):
        conn = Model().conn
        cur = conn.cursor()

        product_name = self.lineEdit.text()
        stock_quantity = self.lineEdit_2.text()
        unit_price = self.lineEdit_3.text()

        category_new = self.lineEdit_4.text()
        cur.execute("select CategoryID from Categories where CategoryName = ?",
                    (category_new,))
        test = cur.fetchone()
        if category_new == '' or test is not None:
            id_category = test[0]
        else:
            cur.execute("select CategoryID from Categories where CategoryName = ?", (category_new,))
            if cur.fetchone() is None:
                name = 'CategoryName'
                try:
                    cur.execute(f"INSERT INTO Categories({name}) VALUES ('{category_new}')")
                    conn.commit()
                    cur.execute("select CategoryID from Categories where CategoryName = ?", (category_new,))
                    id_category = cur.fetchone()[0]
                except conn.Error as er:
                    QMessageBox.information(self, 'Провал', 'Ошибка вставки новых категорий', QMessageBox.Ok)
                    return

        supplier_new = self.lineEdit_5.text()
        cur.execute("select SupplierID from Suppliers where SupplierName = ?",
                    (supplier_new,))
        test = cur.fetchone()
        if supplier_new == '' or test is not None:
            id_supplier = test[0]
        else:
            cur.execute("select SupplierID from Suppliers where SupplierName = ?", (supplier_new,))
            if cur.fetchone() is None:
                name = 'SupplierName'
                try:
                    cur.execute(f"INSERT INTO Suppliers({name}) VALUES ('{supplier_new}')")
                    conn.commit()
                    cur.execute("select SupplierID from Suppliers where SupplierName = ?", (supplier_new,))
                    id_supplier = cur.fetchone()[0]
                except conn.Error as er:
                    QMessageBox.information(self, 'Провал', 'Ошибка вставки новых поставщиков', QMessageBox.Ok)
                    return

        if not (product_name and stock_quantity and unit_price):
            self.label_5.setText('Не все поля заполнены')
            self.label_5.show()
            return

        data_insert = {
            'ProductName': product_name,
            'CategoryID': id_category,
            'SupplierID': id_supplier,
            'StockQuantity': stock_quantity,
            'UnitPrice': unit_price,
        }

        try:
            cur.execute("""
                INSERT INTO Products (ProductName, CategoryID, SupplierID, StockQuantity, UnitPrice)
                VALUES (:ProductName, :CategoryID, :SupplierID, :StockQuantity, :UnitPrice)
            """, data_insert)
            conn.commit()
            QMessageBox.information(self, 'Успех', 'Данные успешно добавлены', QMessageBox.Ok)
            self.exit()
        except conn.Error as er:
            QMessageBox.information(self, 'Провал', 'Произошла ошибка вставки данных, попробуйте поменять '
                                                'данные или не использовать сложные символы', QMessageBox.Ok)


    def exit(self):
        self.data = ProductData()
        self.data.show()
        self.hide()


class UpdateData(QMainWindow):
    def __init__(self, id_row, id_name):
        super(UpdateData, self).__init__()
        self.id_row = id_row
        uic.loadUi('Screens/add_product.ui', self)
        self.setWindowTitle('Добавление нового товара')

        self.label.setText('Обновить продукт')
        self.label_2.setText('')
        self.label_5.hide()
        regex = QRegExp("[0-9]+")
        validator = QRegExpValidator(regex)
        self.lineEdit_2.setValidator(validator)
        double_validator = QDoubleValidator()
        double_validator.setDecimals(2)
        self.lineEdit_3.setValidator(double_validator)

        self.load_comboBox()

        conn = Model().conn
        cur = conn.cursor()
        cur.execute("""
            select ProductID, ProductName, c.CategoryName, s.SupplierName, p.StockQuantity, p.UnitPrice
            from Products p
                join Suppliers s on p.SupplierID = s.SupplierID
                join Categories c on p.CategoryID = c.CategoryID
            where ProductID = ?
        """, (id_row,))
        data = cur.fetchone()
        self.upload_data(data)
        self.pushButton.setText('Обновить')
        self.pushButton.clicked.connect(self.update_data)
        self.pushButton_2.clicked.connect(self.exit)
        self.pushButton_3.clicked.connect(self.delete_data)

    def delete_data(self):
        conn = Model().conn
        cur = conn.cursor()
        try:
            cur.execute("""
                DELETE FROM Products
                WHERE ProductID = ?
            """, (self.id_row,))
            conn.commit()
            QMessageBox.information(self, 'Успех', 'Запись успешно удалена', QMessageBox.Ok)
            self.exit()
        except conn.Error as e:
            QMessageBox.information(self, 'Провал', 'Невозможно удалить запись', QMessageBox.Ok)

    def update_data(self):
        conn = Model().conn
        cur = conn.cursor()

        product_name = self.lineEdit.text()
        category = self.comboBox_category.currentText()
        cur.execute("select CategoryID from Categories where CategoryName = ?", (category,))
        id_category = cur.fetchone()[0]
        supplier = self.comboBox_suppliers.currentText()
        cur.execute("select SupplierID from Suppliers where SupplierName = ?", (supplier,))
        id_supplier = cur.fetchone()[0]
        stock_quantity = self.lineEdit_2.text()
        unit_price = self.lineEdit_3.text()

        if not (product_name and stock_quantity and unit_price):
            self.label_5.setText('Не все поля заполнены')
            self.label_5.show()
            return

        data_update = {
            'ProductName': product_name,
            'CategoryID': id_category,
            'SupplierID': id_supplier,
            'StockQuantity': stock_quantity,
            'UnitPrice': unit_price,
        }

        try:
            cur.execute(f"""
                            UPDATE Products
                            SET ProductName = :ProductName,
                                CategoryID = :CategoryID,
                                SupplierID = :SupplierID,
                                StockQuantity = :StockQuantity,
                                UnitPrice = :UnitPrice
                            WHERE ProductID = {self.id_row}
                            """, data_update)
            conn.commit()
            QMessageBox.information(self, 'Успех', 'Данные успешно обновлены', QMessageBox.Ok)
            self.exit()
        except conn.Error as er:
            QMessageBox.information(self, 'Провал', 'Произошла ошибка обновления данных, попробуйте поменять '
                                                    'данные или не использовать сложные символы', QMessageBox.Ok)
    def load_comboBox(self):
        conn = Model().conn
        cur = conn.cursor()

        self.comboBox_category = self.findChild(QtWidgets.QComboBox, 'comboBox')
        cur.execute("select CategoryName from Categories")
        data = [item[0] for item in cur.fetchall()]
        self.comboBox_category.addItems(data)

        self.comboBox_suppliers = self.findChild(QtWidgets.QComboBox, 'comboBox_2')
        cur.execute("select SupplierName from Suppliers")
        data = [item[0] for item in cur.fetchall()]
        self.comboBox_suppliers.addItems(data)

    def upload_data(self, data):
        self.label_2.setText(f'Номер записи - {data[0]}')
        self.lineEdit.setText(data[1])
        self.comboBox_category.setCurrentText(data[2])
        self.comboBox_suppliers.setCurrentText(data[3])
        self.lineEdit_2.setText(str(data[4]))
        self.lineEdit_3.setText(data[5])
    def exit(self):
        self.data = ProductData()
        self.data.show()
        self.hide()
