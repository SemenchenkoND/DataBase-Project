import sys
from contextlib import contextmanager

from PyQt6.QtSql import QSqlTableModel, QSqlQuery, QSqlDatabase
from PyQt6.QtWidgets import QComboBox


class sqlHandler:
    def __init__(self, db_file, mainWindow):
        self.db_file = db_file
        self.mainWindow = mainWindow
        self.query_select = 'SELECT Gr_prog.* FROM Gr_prog'
        self.query_join = ''
        self.query_where = ''
        self.query_orderBy = ''
        self.current_filter = dict()

        self.connect_db(db_file)
        self.column_names = self.select_column_names('Gr_prog')
        self.model = QSqlTableModel()
        self.model.setEditStrategy(QSqlTableModel.EditStrategy.OnManualSubmit)

        self.select()
        self.mainWindow.form.tableView.setModel(self.model)

    @contextmanager
    def get_db_connection(self):
        '''
        Контекстный менеджер для управления соединением с БД.
        '''
        try:
            self._connect_db(self.db_file)
            yield self.db
        finally:
            if self.db.isOpen():
                self.db.close()

    def connect_db(self, db_file: str):
        '''
        Подключение в БД данной по адресу db_file
        '''
        self.db_file = db_file
        self._connect_db(db_file)
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
        if not self.db.open():
            print("Cannot establish a database connection to {}!".format(db_file))
            return False

    def select_column_names(self, table_name: str) -> list:
        '''
        Запрашивает из БД названия столбцов таблицы table_name
        '''
        self.query.exec(
            f'''
            PRAGMA table_info({table_name})
            '''
        )
        column_names = []
        while self.query.next():
            column_names.append(self.query.value(1))
        return column_names

    def update_vuz_names(self):
        '''
        Обновляет столбец z2 данными о названиях ВУЗов на основе таблицы VUZ
        '''
        return self.query.exec(
            '''
            UPDATE Gr_prog
            SET z2 = (
                SELECT z2 from VUZ where Gr_prog.codvuz = VUZ.codvuz
            )
            '''
        )

    def _select_konks(self, form):
        '''
        Выбирает названия конкурсов и их кодов и сохраняет в словаре self.konks = { имя_конкурса: код_конкурса }
        '''
        self.query.exec(
            '''
            SELECT DISTINCT k2, codkon FROM Gr_konk
            ORDER BY k2
            '''
        )
        self.konks = {}  # name -> codkon
        while self.query.next():
            self.konks[self.query.value(0)] = self.query.value(1)
            form.konkCombo.addItem(self.query.value(0))

    def _select_vuzes(self, form):
        '''
        Выбирает название ВУЗов и их кодов и сохраняет в словаре self.vuzes = { имя_вуза: код_вуза }
        '''
        self.query.exec(
            '''
            SELECT DISTINCT z2, codvuz FROM VUZ
            ORDER BY z2
            '''
        )
        self.vuzes = {}  # name -> codvuz
        while self.query.next():
            self.vuzes[self.query.value(0)] = self.query.value(1)
            form.vuzCombo.addItem(self.query.value(0))

    def select(self) -> None:
        '''
        Делается запрос, состоящий из конкатенации хранящихся отдельно self.query_<название_части>. Полученные данные выводятся в таблице в программе
        '''
        query = self.query_select + self.query_join + self.query_where + self.query_orderBy
        self.model.setQuery(query)
        self.model.select()

    def resetFilter(self) -> None:
        '''
        Фильтры по упорядочиванию по столбцу и по определённым регионам, субъектам и т.д. сбрасываются
        '''
        self.query_orderBy = ''
        self.query_join = ''
        self.query_where = ''
        self.current_filter = dict()
        self.populate_filtering_combos(self.mainWindow.combos_default_and_column)
        self.select()

    def populate_filtering_combos(self, combos_default_and_columns: dict, restoreText: bool = False) -> None:
        '''
        ComboBox'ы из combos_default_and_columns (для фильтрации по регионам, субъектам и т.д.) заполняются вариантами с учётами введенных фильтров
        '''
        for combo in combos_default_and_columns:
            default, column = combos_default_and_columns[combo]
            items = [default, ]
            curText = combo.currentText()

            query = f'SELECT DISTINCT {column} FROM VUZ' + self.query_where
            self._select_and_fill_combo(items, query, combo)
            if restoreText:
                newIndex = combo.findText(curText)
                combo.setCurrentIndex(newIndex)

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

    def addFilter(self, comboBox: QComboBox, text: str) -> None:
        '''
        Для добавления изменений в фильтрацию по регионам, субъектам и тд, когда один из соответствующих comboBox изменён пользователем на значение text.
        Новый фильтр применяется, набор возможных значений комбоБоксов меняется и данные выбираются из БД в соответствии с фильтром.
        '''
        default, column = self.mainWindow.combos_default_and_column[comboBox]
        if text == default and column not in self.current_filter:
            return

        if text == '':
            return

        if text == default:
            self.current_filter.pop(column)
            self._construct_filter_query()
            self.populate_filtering_combos(self.mainWindow.combos_default_and_column, restoreText=True)
            self.select()
            return

        self.current_filter[column] = text
        self._construct_filter_query()
        self.populate_filtering_combos(self.mainWindow.combos_default_and_column, restoreText=True)
        self.select()

    def _construct_filter_query(self):
        '''
        На основании сохранённых данных о введённых фильтрах в словаре self.current_filter = { столбец: значение_для_поиска } формируются части SQL-запроса для фильтрации: query_join, query_where
        '''
        if len(self.current_filter) == 0:
            self.query_join = ''
            self.query_where = ''
            return

        self.query_join = '\nJOIN VUZ ON Gr_prog.codvuz = VUZ.codvuz'
        self.query_where = '\nWHERE '
        first = True
        for column, text in self.current_filter.items():
            if first:
                self.query_where += f'VUZ.{column} = "{text}"'
                first = False
            else:
                self.query_where += f'\n\tAND VUZ.{column} = "{text}"'