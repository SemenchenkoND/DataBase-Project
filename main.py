from PyQt6 import uic
from PyQt6.QtWidgets import QApplication
from PyQt6.QtSql import *
import sys

Form, Window = uic.loadUiType("Forms/MainForm.ui")

db_name = 'DataBases/main_db'
def on_click():
    print("click")

def connect_db(db_name):
    db = QSqlDatabase.addDatabase('QSQLITE')
    db.setDatabaseName(db_name)
    if not db.open():
        print("Cannot connect to database {}!".format(db_name))
        return False
    return db


table = QSqlTableModel()
table.setTable("Gr_prog")
table.select()

app = QApplication([])
window = Window()
form = Form()
form.setupUi(window)

if not connect_db(db_name):
    sys.exit(-1)
else:
    print("Connection OK")

form.pushButton.clicked.connect(on_click)
form.tableView.setSortingEnabled(True)
form.tableView.setModel(table)

window.show()
app.exec()
