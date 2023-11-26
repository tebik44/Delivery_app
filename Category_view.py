from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QPixmap, QIcon, QStandardItem, QStandardItemModel, QDoubleValidator, QRegExpValidator
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QVBoxLayout

import main
from model.model import Model

class CategoryData(QtWidgets.QMainWindow):
    def __init__(self, *args):
        super(CategoryData, self).__init__()
        self.args = args
        uic.loadUi('Screens/table_data.ui', self)
        self.setWindowTitle('Категории')
        self.setMinimumSize(1120, 800)
        self.label.setText('Категории')
        self.tableView = self.findChild(QtWidgets.QTableView, 'tableView')
        self.table_model = QStandardItemModel()
        self.tableView.setModel(self.table_model)
        self.pushButton.clicked.connect(self.add_new_category)

        conn = Model().conn
        cur = conn.cursor()
        cur.execute("""
            select * from Categories
        """)
        data = cur.fetchall()
        cur.execute("PRAGMA table_info(Categories)")
        column_data = cur.fetchall()
        self.load_data(data, column_data)

        self.pushButton_3.clicked.connect(self.exit)

        self.tableView.doubleClicked.connect(self.update_row)

    def update_row(self, index):
        row = index.row()
        id_row = self.table_model.item(row, 0).text()
        self.upda = UpdateCategory(self.args[0], id_row)
        self.upda.show()
        self.hide()
    def add_new_category(self):
        self.add = AddCategory(self.args[0])
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

class AddCategory(QMainWindow):
    def __init__(self, *args):
        super(AddCategory, self).__init__()
        self.args = args
        uic.loadUi('Screens/category_supplier.ui', self)
        self.setWindowTitle('Добавление новой категории')

        self.label.setText('Добавить новую категорию')
        self.pushButton.hide()
        self.label_2.hide()
        self.lineEdit.setPlaceholderText('Название категории')

        self.pushButton_2.clicked.connect(self.add_category_data)
        self.pushButton_3.clicked.connect(self.exit)

    def add_category_data(self):
        conn = Model().conn
        cur = conn.cursor()
        category_name = self.lineEdit.text()
        if category_name == '':
            self.label_2.setText('* Не все поля заполнены')
            self.label_2.show()
        else:
            cur.execute("select CategoryID from Categories where CategoryName = ?", (category_name,))
            if cur.fetchone() is None:
                name = 'CategoryName'
                try:
                    cur.execute(f"INSERT INTO Categories({name}) VALUES ('{category_name}')")
                    conn.commit()
                    QMessageBox.information(self, 'Успех', 'Категория добавлена', QMessageBox.Ok)
                    self.exit()
                except conn.Error as er:
                    QMessageBox.information(self, 'Провал', 'Ошибка добавления новой категории')
            else:
                self.label_2.setText('Такая категория уже есть')
                self.label_2.show()

    def exit(self):
        self.dat = CategoryData(self.args[0])
        self.dat.show()
        self.hide()


class UpdateCategory(QMainWindow):
    def __init__(self, *args):
        super(UpdateCategory, self).__init__()
        self.args = args
        uic.loadUi('Screens/category_supplier.ui', self)
        self.setWindowTitle('Редактирование категории')

        self.label.setText('Редактировать категорию')
        self.label_2.hide()
        self.lineEdit.setPlaceholderText('Название категории')

        conn = Model().conn
        cur = conn.cursor()
        cur.execute(f"select * from Categories where CategoryID = {self.args[1]}")
        data = cur.fetchone()
        self.upload_data(data)
        self.pushButton.clicked.connect(self.delete_category)
        self.pushButton_2.clicked.connect(self.update_category_data)
        self.pushButton_3.clicked.connect(self.exit)

    def delete_category(self):
        conn = Model().conn
        cur = conn.cursor()
        try:
            cur.execute("""
                            DELETE FROM Categories
                            WHERE CategoryID = ?
                        """, (self.args[1],))
            conn.commit()
            QMessageBox.information(self, 'Успех', 'Запись удалена', QMessageBox.Ok)
            self.exit()
        except conn.Error as er:
            QMessageBox.information(self, 'Провал', 'Произошла ошибка добавления данных', QMessageBox.Ok)


    def upload_data(self, data):
        self.lineEdit.setText(data[1])
    def update_category_data(self):
        conn = Model().conn
        cur = conn.cursor()
        category_name = self.lineEdit.text()
        if category_name == '':
            self.label_2.setText('* Не все поля заполнены')
            self.label_2.show()
        else:
            cur.execute("select CategoryID from Categories where CategoryName = ?", (category_name,))
            if cur.fetchone() is None:
                name = 'CategoryName'
                try:
                    cur.execute(f"""
                        UPDATE Categories
                            SET CategoryName = ?
                            WHERE CategoryID = ?
                    """, (category_name, int(self.args[1])))
                    conn.commit()
                    QMessageBox.information(self, 'Успех', 'Категория изменена', QMessageBox.Ok)
                    self.exit()
                except conn.Error as er:
                    QMessageBox.information(self, 'Провал', 'Ошибка изменений категории')
            else:
                self.label_2.setText('Такая категория уже есть')
                self.label_2.show()

    def exit(self):
        self.cate = CategoryData(self.args[0])
        self.cate.show()
        self.hide()