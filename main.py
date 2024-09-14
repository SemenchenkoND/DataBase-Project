from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QDialog
from PyQt6.QtSql import *
import sys

# Основное окно
Form, Window = uic.loadUiType("DataBase-Project/Forms/MainForm.ui")

# Основное окно распоряжение
RasporajForm, _ = uic.loadUiType("DataBase-Project/Forms/rasporaj.ui")

# Основное окно данные
DataTableForm, _ = uic.loadUiType("DataBase-Project/Forms/dannie.ui")

# Наша база
db_name = 'DataBases/Database.db'

# Функция для подключения к базе данных
def connect_db(db_name):
    db = QSqlDatabase.addDatabase('QSQLITE')
    db.setDatabaseName(db_name)
    if not db.open():
        print(f"Cannot connect to database {db_name}!")
        return False
    return db

# Для нашего диалогового окна - Распоряжение-
class RasporajDialog(QDialog, RasporajForm):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)  

# Для окна с Данными и его таблицами
class DataTableDialog(QDialog, DataTableForm):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)  
        self.setup_table()

    # Настройка таблицы
    def setup_table(self):
        self.model = QSqlTableModel(self)  
        self.model.setTable("Gr_prog")  # Указываем имя таблиц
        self.model.select()  # Загружает данные из таблицы
        self.tableView.setModel(self.model) 
        self.tableView.resizeColumnsToContents()  


app = QApplication([])


window = Window()
form = Form()
form.setupUi(window)


if not connect_db(db_name):
    sys.exit(-1)
else:
    print("Connection OK")


rasporaj_dialog = RasporajDialog()  # Экземпляр для распоряжения
data_table_dialog = DataTableDialog()  # Экземпляр для диалога с таблицами(наши данные)

# Для прочтения текста в "Распоряжении"
form.pushButton_3.clicked.connect(rasporaj_dialog.exec)

# Для открытия кнопки "Данные" и её таблиц
form.pushButton.clicked.connect(data_table_dialog.exec)

# Для закрытия окна при нажатии на "Выход" 
form.pushButton_6.clicked.connect(window.close)


window.show()
app.exec()

