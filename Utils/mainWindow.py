from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QHeaderView, QMessageBox
from PyQt6.QtSql import *
from Utils.sqlHandler import sqlHandler
from Utils.addWindow import AddWindow, ChangeWindow
from Utils.analyse import NIR, Subyect, Konkurs
from Utils.view import View


class MainWindow:
    def __init__(self, db_file):
        self.Form, self.Window = uic.loadUiType("UI/grant_form1.ui")
        self.app = QApplication([])
        self.window = self.Window()
        self.form = self.Form()
        self.form.setupUi(self.window)
        self._last_index = -1  # для changeSorting

        self.form.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.sqlHandler = sqlHandler(db_file, self)
        self.addWindow = AddWindow(self)
        self.changeWindow = ChangeWindow(self)

        self.View_VUZ = View(db_file, 'VUZ', "UI/VUZ_form.ui")
        self.View_Konk = View(db_file, "Gr_Konk", "UI/Konk_form.ui")

        self.distr_NIR = NIR(db_file, self)
        self.distr_Konk = Konkurs(db_file, self)
        self.distr_Sub = Subyect(db_file, self)

        self.combos_default_and_column = {
            self.form.fedCombo: ('Все федеральные округа', 'region'),
            self.form.subCombo: ('Все субъекты', 'oblname'),
            self.form.gorCombo: ('Все города', 'city'),
            self.form.vuzCombo: ('Все ВУЗы', 'z2')
        }
        self.sqlHandler.populate_filtering_combos(self.combos_default_and_column)

        self.form.action_2.triggered.connect(lambda: self.View_VUZ.open())
        self.form.action_3.triggered.connect(lambda: self.View_Konk.open())

        self.form.action_4.triggered.connect(lambda: self.distr_NIR.open())
        self.form.action_5.triggered.connect(lambda: self.distr_Konk.open())
        self.form.action_6.triggered.connect(lambda: self.distr_Sub.open())

        self.form.tableView.horizontalHeader().sectionClicked.connect(
            lambda ind: self.changeSorting(ind, self.sqlHandler.column_names))
        self.form.addBtn.clicked.connect(lambda: self.addWindow.open())
        self.form.changeBtn.clicked.connect(lambda: self.changeWindow.open(*self.get_selected_row_values()))
        self.form.deleteBtn.clicked.connect(lambda: self.delete_row())
        self.form.closeBtn.clicked.connect(lambda: (
            self.sqlHandler.update_vuz_names(),
            self.sqlHandler.select()
        ))
        self.form.resetFilter.clicked.connect(lambda: self.sqlHandler.resetFilter())

        self.form.fedCombo.activated.connect(
            lambda index: self.sqlHandler.addFilter(self.form.fedCombo, self.form.fedCombo.currentText()))
        self.form.subCombo.activated.connect(
            lambda index: self.sqlHandler.addFilter(self.form.subCombo, self.form.subCombo.currentText()))
        self.form.gorCombo.activated.connect(
            lambda index: self.sqlHandler.addFilter(self.form.gorCombo, self.form.gorCombo.currentText()))
        self.form.vuzCombo.activated.connect(
            lambda index: self.sqlHandler.addFilter(self.form.vuzCombo, self.form.vuzCombo.currentText()))

    def changeSorting(self, header_index, header: QHeaderView):
        '''
        Для изменения фильтра по столбцу и направления фильтрации (по возрастанию и убыванию поочередно)
        '''
        key_columns = [0, 1]
        if header_index in key_columns:
            header_index = 0

        changeTable = {'ASC': 'DESC', 'DESC': 'ASC'}
        if header_index != self._last_index:
            self._current_sorting_dir = 'ASC'
            self._last_index = header_index
        else:
            self._current_sorting_dir = changeTable[self._current_sorting_dir]

        if header_index in key_columns:
            self.sqlHandler.query_orderBy = f'\nORDER BY codkon {self._current_sorting_dir}, g1 {self._current_sorting_dir}'
            self.sqlHandler.select()
            return

        col_name = header[header_index]
        self.sqlHandler.query_orderBy = f'\nORDER BY {col_name} {self._current_sorting_dir}'
        self.sqlHandler.select()

    def get_selected_row_values(self):
        selected_indexes = self.form.tableView.selectedIndexes()
        if not selected_indexes:
            print('Строка не выбрана')
            return (None, None)
        data = [index.data() for index in selected_indexes]

        codkon = data[0]
        codnir = data[1]
        pk = {
            'codkon': codkon,
            'g1': codnir
        }
        other_vals = data[2:]
        return (pk, other_vals)

    def delete_row(self):
        pk, row_values = self.get_selected_row_values()
        if not pk:
            msg = QMessageBox()
            msg.setText("Для удаления строки выделите её и нажмите на кнопку удаления строки")
            msg.exec()
            return

        title = row_values[14 - 2]

        msgBox = QMessageBox()
        msgBox.setText(f"Удалить грант с кодом НИР {pk['g1']}?")
        msgBox.setInformativeText(f"Будет удален грант с названием: {title}")
        msgBox.setStandardButtons(QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard)
        msgBox.button(QMessageBox.StandardButton.Save).setText('Удалить')
        msgBox.button(QMessageBox.StandardButton.Discard).setText('Отмена')
        msgBox.setDefaultButton(QMessageBox.StandardButton.Save)
        ret = msgBox.exec()

        if ret == QMessageBox.StandardButton.Save:
            query = 'DELETE FROM Gr_prog WHERE codkon = "{}" AND g1 = {}'.format(pk['codkon'], pk['g1'])
            isGood = self.sqlHandler.query.exec(query)
            msg = QMessageBox()
            if not isGood:
                msg.setText("Не удалось удалить строку из базы данных")
                msg.exec()
                return
            else:
                msg.setText("Выбранная строка была удалена")
                msg.exec()

            self.sqlHandler._sum_financing()
            self.sqlHandler._count_NIRs()
            self.sqlHandler.select()

    def distribution_VUZS(self):
        sp = []

