from PyQt6 import uic
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtSql import *
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtCore import QRegularExpression


class AddWindow:
    def __init__(self, mainWindow):
        self.mainWindow = mainWindow
        self.query = QSqlQuery()
        self.Form, self.Window = uic.loadUiType("UI/add_form.ui")
        self.window = self.Window()
        self.form = self.Form()
        self.form.setupUi(self.window)
        self.data = None

        self.fields = {
            'codkon': self.form.codkonkLine,
            'g1': self.form.codnir,
            'z2': self.form.vuzCombo,
            'codvuz': self.form.vuzcodLine,
            'g7': self.form.codGRNTILine,
            'g8': self.form.rukLine,
            'g9': self.form.dolzhLine,
            'g10': self.form.scienceZvanLine,
            'g11': self.form.scienceStepLine,
            'g5': self.form.finansLine,
            'g6': self.form.nirDescText
        }

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

        self.form.backBtn.clicked.connect(lambda: self.close())
        self.form.saveBtn.clicked.connect(lambda: self.saveProccess())

    def open(self):
        self.query.exec(
            '''
            SELECT g1 FROM Gr_prog ORDER BY g1 DESC LIMIT 1
            '''
        )
        self.query.next()
        codnir = int(self.query.value(0)) + 1
        self.fields['g1'].setText(f'{codnir}')
        self.show()

    def saveProccess(self):
        valid = self.isValidInput()
        if not valid:
            msg = QMessageBox()
            msg.setText("Введены неверные данные")
            msg.exec()
            return

        columns = self.mainWindow.sqlHandler.column_names
        query = 'INSERT INTO Gr_prog ('
        for i, column in enumerate(columns):
            if i != (len(columns) - 1):
                query += f'{column},'
            else:
                query += f'{column}) VALUES ('

        for i, column in enumerate(columns):
            # QTextEdit
            if column == 'g6':
                query += f'"{self.fields[column].toPlainText()}",'
            # QComboBox
            elif column == 'z2':
                query += f'"{self.fields[column].currentText()}",'
            # INT
            elif column == 'g5':
                query += f'{self.fields[column].text()},'
            elif column == 'codvuz':
                query += f'{self.fields[column].text()});'
            # Все текстовые
            elif column in self.fields:
                query += f'"{self.fields[column].text()}",'
            elif i != (len(columns) - 1):
                query += '0,'

        print(query)
        isSuccesfull = self.query.exec(query)
        if not isSuccesfull:
            msg = QMessageBox()
            msg.setText("Не получилось сохранить данные в базу данных")
            msg.exec()
            return

        self.mainWindow.sqlHandler._sum_financing()
        self.mainWindow.sqlHandler._count_NIRs()
        self.mainWindow.sqlHandler.select()
        self.close()

    def close(self):
        self.window.close()
        for field in ['g1', 'g7', 'g8', 'g9', 'g10', 'g11', 'g5', 'g6']:
            self.fields[field].setText('')

    def isValidInput(self, isChange=False):
        codnir = self.fields['g1'].text()
        codkon = self.fields['codkon'].text()
        # Против SQL инжекций
        if '"' in codnir or '"' in codkon:
            print('Ошибка. Кавычки в поле codnir или codkon')
            return False

        if not isChange:
            self.query.exec(f'SELECT SUM(g1) from Gr_prog WHERE g1 = "{codnir}" AND codkon = "{codkon}"')
            self.query.next()
            if self.query.value(0):
                print('Такой первичный ключ существует')
                return False

        if not self.fields['g7'].hasAcceptableInput():
            print('Неверный ГРНТИ')
            return False

        for field in ['g1', 'g8', 'g9', 'g10', 'g11']:
            if len(self.fields[field].text()) == 0:
                print('Пустое поле')
                return False

        if len(self.fields['g6'].toPlainText()) == 0:
            print('Пустое поле описания')
            return False

        return True

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

    def show(self):
        self.window.show()


class ChangeWindow(AddWindow):
    def __init__(self, mainWindow):
        super().__init__(mainWindow)
        self.form.mainLabel.setText('Редактировать НИР')
        self.form.saveBtn.setText('Изменить НИР')

    def open(self, current_pk, current_vals) -> None:
        if not current_pk:
            msg = QMessageBox()
            msg.setText("Для редактирования строки выделите её и нажмите на кнопку редактирования строки")
            msg.exec()
            return
            # konkCombo
        codkon = current_pk['codkon']
        self.query.exec(f'SELECT k2 FROM Gr_konk WHERE codkon="{codkon}"')
        self.query.next()
        kon = self.query.value(0)
        self.form.konkCombo.setCurrentIndex(self.form.konkCombo.findText(kon))
        self.form.konkCombo.setEnabled(False)

        # codnir
        self.form.codnir.setText(str(current_pk['g1']))
        self.form.codnir.setEnabled(False)

        # vuzCombo
        vuz = current_vals[0]
        self.form.vuzCombo.setCurrentIndex(self.form.vuzCombo.findText(vuz))

        # codGRNTI
        grnti = current_vals[1]
        self.form.codGRNTILine.setText(grnti)

        self.form.rukLine.setText(current_vals[2])
        self.form.dolzhLine.setText(current_vals[3])
        self.form.scienceZvanLine.setText(current_vals[4])
        self.form.scienceStepLine.setText(current_vals[5])
        self.form.finansLine.setText(str(current_vals[6]))

        self.form.nirDescText.setText(current_vals[12])

        self.window.show()

    def saveProccess(self):
        valid = self.isValidInput(isChange=True)
        if not valid:
            msg = QMessageBox()
            msg.setText("Введены неверные данные")
            msg.exec()
            return

        columns = self.mainWindow.sqlHandler.column_names
        query = 'UPDATE Gr_prog \n\tSET '
        for i, column in enumerate(columns[2:]):
            # Не сбиваем финанисирование
            if column in ['g2', 'g21', 'g22', 'g23', 'g24']:
                continue

            if i != 0:
                query += '\t'
            query += f'{column}='
            # QTextEdit
            if column == 'g6':
                query += f'"{self.fields[column].toPlainText()}",\n'
            # QComboBox
            elif column == 'z2':
                query += f'"{self.fields[column].currentText()}",\n'
            # INT
            elif column == 'g5':
                query += f'{self.fields[column].text()},\n'
            elif column == 'codvuz':
                query += f'{self.fields[column].text()}\n'
            # Все текстовые
            elif column in self.fields:
                query += f'"{self.fields[column].text()}",\n'
        query += f'WHERE codkon="{self.fields[columns[0]].text()}" AND g1={self.fields[columns[1]].text()};'
        print(query)
        isSuccesfull = self.query.exec(query)
        if not isSuccesfull:
            msg = QMessageBox()
            msg.setText("Не получилось изменить данные в базе данных")
            msg.exec()
            return

        self.mainWindow.sqlHandler._sum_financing()
        self.mainWindow.sqlHandler.select()
        self.close()