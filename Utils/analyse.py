import sys
from PyQt6.QtWidgets import QComboBox, QMessageBox, QHeaderView
from PyQt6.QtSql import *
from PyQt6 import uic
from Utils.sqlHandler import sqlHandler
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtCore import QRegularExpression

class NIR:
    def __init__(self,db_file, mainWindow):
        self.mainWindow = mainWindow
        self.query = QSqlQuery()
        self.Form, self.Window = uic.loadUiType("UI/distribution_NIR.ui")
        self.window = self.Window()
        self.form = self.Form()
        self.form.setupUi(self.window)
        self.current_filter = dict()

        self.sqlModel = QSqlTableModel()
        self.sqlModel.setEditStrategy(QSqlTableModel.EditStrategy.OnManualSubmit)
        self.form.tableView.setModel(self.sqlModel)
        self.form.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.select()

        #self.sqlHandler = SqlHandler(db_file, self)

        self.combos_default_and_column = {self.form.VUZCombo: ('Все ВУЗы', 'z2')}

        self.populate_filtering_combos(self.combos_default_and_column)
        #self.form.saveBtn.clicked.connect(lambda: self.saveProccess())
        self.form.closeBtn.clicked.connect(lambda: self.closeWindow())


        #self.form.VUZCombo.activated.connect(lambda index: self.addFilter(self.form.VUZCombo, self.form.VUZCombo.currentText()))

    def select(self):
        where_filter = self.mainWindow.sqlHandler.query_where
        if 'WHERE' in where_filter:
            query_having = 'HAVING ' + self.mainWindow.sqlHandler.query_where.replace('WHERE ', '')
        else:
            query_having = ''
        query = \
        f'''SELECT Gr_prog.z2 as "ВУЗ",
            COUNT(*) as "Количество НИР",
            SUM(g5) as "Суммарное плановое финансирование",
            COUNT(DISTINCT codkon) as "Количество конкурсов, в которых участвует"
        FROM Gr_prog
        JOIN VUZ ON Gr_prog.codvuz = VUZ.codvuz
        GROUP BY Gr_prog.z2 {query_having}'''
        self.sqlModel.setQuery(query)
        self.sqlModel.select()

    def open(self):
        self.window.show()

    def closeWindow(self):
        self.window.close()

    def populate_filtering_combos(self, combos_default_and_columns: dict, restoreText: bool = False) -> None:
        '''
        ComboBox'ы из combos_default_and_columns (для фильтрации по регионам, субъектам и т.д.) заполняются вариантами с учётами введенных фильтров
        '''
        for combo in combos_default_and_columns:
            default, column = combos_default_and_columns[combo]
            items = [default, ]
            curText = combo.currentText()

            query = f'SELECT DISTINCT {column} FROM VUZ ORDER BY {column} ASC'
            self._select_and_fill_combo(items, query, combo)
            if restoreText:
                newIndex = combo.findText(curText)
                combo.setCurrentIndex(newIndex)
            if combo.count() == 2:
                combo.setCurrentIndex(1)
                default, column = self.mainWindow.combos_default_and_column[combo]
                self.current_filter[column] = combo.currentText()

    def _select_and_fill_combo(self, items_default: list, query: str, combo: QComboBox):
        '''
        Добавляет в список стандартные значения items_default и значения, полученные из SQL-запроса query
        '''
        self.query.exec(query)
        items = []
        while self.query.next():
            items.append(self.query.value(0))
        combo.clear()
        combo.addItems(items_default + items)



class Konkurs:
    def __init__(self,db_file, mainWindow):
        self.mainWindow = mainWindow
        self.query = QSqlQuery()
        self.Form, self.Window = uic.loadUiType("UI/distribution_Konkurs.ui")
        self.window = self.Window()
        self.form = self.Form()
        self.form.setupUi(self.window)
        self.current_filter = dict()

        self.sqlModel = QSqlTableModel()
        self.sqlModel.setEditStrategy(QSqlTableModel.EditStrategy.OnManualSubmit)
        self.form.tableView.setModel(self.sqlModel)
        self.form.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.select()

        self.combos_default_and_column = {self.form.KonkCombo: ('Все Конкурсы', 'k2')}

        self.populate_filtering_combos(self.combos_default_and_column)
        #self.form.saveBtn.clicked.connect(lambda: self.saveProccess())
        self.form.closeBtn1.clicked.connect(lambda: self.closeWindow())


        #self.form.VUZCombo.activated.connect(lambda index: self.addFilter(self.form.VUZCombo, self.form.VUZCombo.currentText()))

    def open(self):
        self.window.show()

    def closeWindow(self):
        self.window.close()

    def select(self):
        where_filter = self.mainWindow.sqlHandler.query_where
        query = \
        f'''SELECT k2 as "Конкурс",
            COUNT(DISTINCT g1) as "Количество НИР",
            SUM(g5) as "Суммарное плановое финансирование",
            COUNT(DISTINCT Gr_prog.codvuz) as "Количество ВУЗов"
        FROM Gr_konk
        JOIN Gr_prog on Gr_konk.codkon = Gr_prog.codkon
        JOIN VUZ on Gr_prog.codvuz = VUZ.codvuz
        {where_filter}
        GROUP BY k2'''
        self.sqlModel.setQuery(query)
        print(query)
        self.sqlModel.select()

    def populate_filtering_combos(self, combos_default_and_columns: dict, restoreText: bool = False) -> None:
        '''
        ComboBox'ы из combos_default_and_columns (для фильтрации по регионам, субъектам и т.д.) заполняются вариантами с учётами введенных фильтров
        '''
        for combo in combos_default_and_columns:
            default, column = combos_default_and_columns[combo]
            items = [default, ]
            curText = combo.currentText()

            query = f'SELECT DISTINCT {column} FROM VUZ ORDER BY {column} ASC;'
            self._select_and_fill_combo(items, query, combo)
            if restoreText:
                newIndex = combo.findText(curText)
                combo.setCurrentIndex(newIndex)
            if combo.count() == 2:
                combo.setCurrentIndex(1)
                default, column = self.mainWindow.combos_default_and_column[combo]
                self.current_filter[column] = combo.currentText()

    def _select_and_fill_combo(self, items_default: list, query: str, combo: QComboBox):
        '''
        Добавляет в список стандартные значения items_default и значения, полученные из SQL-запроса query
        '''
        self.query.exec(query)
        items = []
        while self.query.next():
            items.append(self.query.value(0))
        combo.clear()
        combo.addItems(items_default + items)

class Subyect:
    def __init__(self,db_file, mainWindow):
        self.mainWindow = mainWindow
        self.query = QSqlQuery()
        self.Form, self.Window = uic.loadUiType("UI/distribution_oblast.ui")
        self.window = self.Window()
        self.form = self.Form()
        self.form.setupUi(self.window)
        self.current_filter = dict()

        #self.sqlHandler = SqlHandler(db_file, self)

        self.combos_default_and_column = {self.form.SubCombo: ('Все Субъекты', 'oblname')}

        self.populate_filtering_combos(self.combos_default_and_column)
        #self.form.saveBtn.clicked.connect(lambda: self.saveProccess())
        self.form.closeBtn2.clicked.connect(lambda: self.closeWindow())


        #self.form.VUZCombo.activated.connect(lambda index: self.addFilter(self.form.VUZCombo, self.form.VUZCombo.currentText()))

    def open(self):
        self.window.show()

    def closeWindow(self):
        self.window.close()

    def populate_filtering_combos(self, combos_default_and_columns: dict, restoreText: bool = False) -> None:
        '''
        ComboBox'ы из combos_default_and_columns (для фильтрации по регионам, субъектам и т.д.) заполняются вариантами с учётами введенных фильтров
        '''
        for combo in combos_default_and_columns:
            default, column = combos_default_and_columns[combo]
            items = [default, ]
            curText = combo.currentText()

            query = f'SELECT DISTINCT {column} FROM Gr_konk ORDER BY {column} ASC;'
            self._select_and_fill_combo(items, query, combo)
            if restoreText:
                newIndex = combo.findText(curText)
                combo.setCurrentIndex(newIndex)
            if combo.count() == 2:
                combo.setCurrentIndex(1)
                default, column = self.mainWindow.combos_default_and_column[combo]
                self.current_filter[column] = combo.currentText()

    def _select_and_fill_combo(self, items_default: list, query: str, combo: QComboBox):
        '''
        Добавляет в список стандартные значения items_default и значения, полученные из SQL-запроса query
        '''
        self.query.exec(query)
        items = []
        while self.query.next():
            items.append(self.query.value(0))
        combo.clear()
        combo.addItems(items_default + items)