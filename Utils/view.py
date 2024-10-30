from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QHeaderView, QMessageBox
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtSql import *
import sys
from Utils.sqlHandler import sqlHandler
from Utils.addWindow import AddWindow, ChangeWindow
# from analyse import NIR, Subyect, Konkurs

class View:
    def __init__(self, db_file,bd_name,form_view):
        self.query = QSqlQuery()
        #self.view=View
        self.Form, self.Window = uic.loadUiType(form_view)
        self.db_file=db_file
        self.app = QApplication([])
        self.window = self.Window()
        self.form = self.Form()
        self.form.setupUi(self.window)

        self.model = QSqlTableModel()
        self.model.setEditStrategy(QSqlTableModel.EditStrategy.OnManualSubmit)
        self.model.setTable(bd_name)
        self.model.select()
        self.form.tableView.setModel(self.model)

        #self.query_select = f'SELECT {name_table}.* FROM {name_table}'


        #self.connect_db(self.db_file, 'VUZ')
        self.form.tableView.setSortingEnabled(True)
        #self.tableView.setModel(F_used)
        self.form.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.form.closeBtn1.clicked.connect(lambda: self.closeWindow())



    def open(self):
        self.window.show()

    def closeWindow(self):
        self.window.close()

    def connect_db(self, db_file: str,db_name):
        '''
        Подключение в БД данной по адресу db_file
        '''
        self.db_file = db_file
        self._connect_db(db_name)
        if not self.db:
            sys.exit(-1)
        else:
            self.query = QSqlQuery()
            print("connection ok")

    def _connect_db(self, db_file: str):
        '''
        Открывает БД и сохраняет данные для работы с ней
        '''
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName(db_file)
        #self.tableView.setModel()
        if not self.db.open():
            print("Cannot establish a database connection to {}!".format(db_file))
            return False


'''class SqlHandler1:
    def __init__(self, db_file, name_table):
        self.db_file = db_file
        #self.mainWindow = mainWindow
        #self.query_select = f'SELECT {name_table}.* FROM {name_table}'

        self.connect_db(db_file)
        #self.column_names = self.select_column_names('Gr_prog')


class View_VUZ:
    def __init__(self, db_file, mainWindow):
        self.mainWindow = mainWindow
        self.Form, self.Window = uic.loadUiType("ui/VUZ_form.ui")
        self.app = QApplication([])
        self.window = self.Window()
        self.form = self.Form()
        self.form.setupUi(self.window)
        self.form.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.form.closeBtn2.clicked.connect(lambda: self.closeWindow())

    def open(self):
        self.window.show()

    def closeWindow(self):
        self.window.close()'''