from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QDialog
from PyQt6.QtSql import *
import sys

# Основное окно
Form, Window = uic.loadUiType("Forms/MainForm.ui")

# Основное окно распоряжение
RasporajForm, _ = uic.loadUiType("Forms/rasporaj.ui")

# Основное окно данные
DataTableForm, _ = uic.loadUiType("Forms/dannie.ui")

# Наша база
db_name = 'DataBases/Database.sqlite'

# Функция для подключения к базе данных
def connect_db(db_name):
    db = QSqlDatabase.addDatabase('QSQLITE')
    db.setDatabaseName(db_name)
    if not db.open():
        print(f"Cannot connect to database {db_name}!")
        return False
    return db

# Для нашего диалогового окна - Распоряжение
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
        self.model_1 = QSqlTableModel(self)
        self.model_1.setTable("Gr_prog")  # Указываем имя таблиц
        self.model_1.select()  # Загружает данные из таблицы
        self.tableView.setModel(self.model_1)
        self.tableView.resizeColumnsToContents()
        self.tableView.setSortingEnabled(True)

        self.model_2 = QSqlTableModel(self)
        self.model_2.setTable("Gr_konk")
        self.model_2.select()
        self.tableView_2.setModel(self.model_2)
        self.tableView_2.resizeColumnsToContents()
        self.tableView.setSortingEnabled(True)

        self.model_3 = QSqlTableModel(self)
        self.model_3.setTable("VUZ")
        self.model_3.select()
        self.tableView_3.setModel(self.model_3)
        self.tableView_3.resizeColumnsToContents()
        self.tableView.setSortingEnabled(True)


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

