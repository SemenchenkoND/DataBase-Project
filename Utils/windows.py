from PyQt6 import uic
from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtSql import QSqlQuery
from PyQt6.QtWidgets import QApplication, QHeaderView, QMessageBox

from Utils.sqlHandler import sqlHandler


class MainWindow:
    def __init__(self, db_file):
        self.Form, self.Window = uic.loadUiType("UI/grant_form1.ui")
        self.app = QApplication([])
        self.window = self.Window()
        self.form = self.Form()
        self.form.setupUi(self.window)
        self._last_index = -1  # для changeSorting

        self.sqlHandler = sqlHandler(db_file, self)
        self.addWindow = addWindow(self)
        self.changeWindow = changeWindow(self)


        self.combos_default_and_column = {
            self.form.fedCombo: ('Все федеральные округи', 'region'),
            self.form.subCombo: ('Все субъекты', 'oblname'),
            self.form.gorCombo: ('Все города', 'city'),
            self.form.vuzCombo: ('Все ВУЗы', 'z2')
        }
        self.sqlHandler.populate_filtering_combos(self.combos_default_and_column)

        self.form.tableView.horizontalHeader().sectionClicked.connect(
            lambda ind: self.changeSorting(ind, self.sqlHandler.column_names))
        self.form.addBtn.clicked.connect(lambda: self.addWindow.show())
        self.form.changeBtn.clicked.connect(lambda: self.changeWindow.show())
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


class addWindow:
    def __init__(self, mainWindow: MainWindow):
        self.mainWindow = mainWindow
        self.query = QSqlQuery()
        self.Form, self.Window = uic.loadUiType("ui/add_form.ui")
        self.window = self.Window()
        self.form = self.Form()
        self.form.setupUi(self.window)

        mainWindow.sqlHandler._select_konks(self.form)
        self._refresh_codkon(0)
        mainWindow.sqlHandler._select_vuzes(self.form)
        self._refresh_codvuz(0)

        self.form.konkCombo.currentIndexChanged.connect(self._refresh_codkon)
        self.form.vuzCombo.currentIndexChanged.connect(self._refresh_codvuz)

        self.form.codGRNTILine.setInputMask('99.99.990')
        self.form.codGRNTILine.textEdited.connect(
            lambda text: self._codGRNTI_update_inputMask(self.form.codGRNTILine, text))

        validator = QRegularExpressionValidator(QRegularExpression(r'[0-9]+\.[0-9]*'))
        self.form.finansLine.setValidator(validator)

    def _codGRNTI_update_inputMask(self, qline, text):
        '''
         Для изменения маски ввода между двумя и одним кодами ГРНТИ
            '''
        oneCodeMask = '99.99.990'
        twoCodeMask = '99.99.99,99.99.99'

        if len(text) < 12 and qline.inputMask() == twoCodeMask:
            cur_pos = qline.cursorPosition() if qline.cursorPosition() <= 8 else 8
            qline.setInputMask(oneCodeMask)
            qline.setCursorPosition(cur_pos)

        elif len(text) >= 9 and qline.inputMask() == oneCodeMask:
            cur_pos = qline.cursorPosition()
            if cur_pos == 9:
                cur_pos += 1
            qline.setInputMask(twoCodeMask)
            qline.setCursorPosition(cur_pos)

    def _refresh_codkon(self, index):
        '''
        Обновляет код конурса в поле codkonkLine в соответствии с выбранным в konkCombo конкурсом
        '''
        codkon = self.mainWindow.sqlHandler.konks[self.form.konkCombo.itemText(index)]
        self.form.codkonkLine.setText(codkon)

    def _refresh_codvuz(self, index):
        '''
        Обновляет код ВУЗа в поле vuzcodLine в соответствии с выбранным в vuzCombo ВУЗом
        '''
        codvuz = self.mainWindow.sqlHandler.vuzes[self.form.vuzCombo.itemText(index)]
        self.form.vuzcodLine.setText(str(codvuz))

    def add_NIR_to_db(self):
        '''
                Метод для добавления новой записи НИР в БД.
                '''
        cod_nir = self.form.codnir.text()
        cod_grnti = self.form.codGRNTILine.text()
        cod_konk = self.form.codkonkLine.text()
        cod_vuz = self.form.vuzcodLine.text()
        ruk = self.form.rukLine.text()
        dolzh = self.form.dolzhLine.text()
        science_zvan = self.form.scienceZvanLine.text()
        science_step = self.form.scienceStepLine.text()
        finans = self.form.finansLine.text()
        nir_desc = self.form.nirDescText.toPlainText()

        # SQL-запрос для вставки данных
        query_str = f'''
                    INSERT INTO Gr_prog (g1, codkon, )
                    VALUES ("{cod_nir}", "{cod_grnti}", "{cod_konk}", "{cod_vuz}", "{ruk}",
                            "{dolzh}", "{science_zvan}", "{science_step}", "{finans}", "{nir_desc}")
                '''

        if not self.query.exec(query_str):
            print("Ошибка добавления НИР:", self.query.lastError().text())
            return
        print("НИР успешно добавлен!")

        # Закрытие окна после добавления
        self.window.close()


    def show(self):
            self.window.show()

class changeWindow(addWindow):
    def __init__(self, mainWindow):
        super().__init__(mainWindow)
        self.form.mainLabel.setText('Редактировать НИР')