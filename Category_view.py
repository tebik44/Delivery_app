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
        self.pushButton.hide()


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
    def load_data(self, data, column_data):
        column_data = [item[1] for item in column_data]
        self.table_model.setHorizontalHeaderLabels(column_data)

        for index_row, data_row in enumerate(data):
            for index_column, data_column in enumerate(column_data):
                item = QStandardItem(str(data_row[index_column]))
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                self.table_model.setItem(index_row, index_column, item)

    def exit(self):
        self.profile = main.Profile(self.args[0])
        self.profile.show()
        self.hide()