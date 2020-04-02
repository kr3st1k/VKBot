import peewee
from Database.Models import BaseModel, CommandModel
from Database.Models.BaseModel import dbhandle, InternalError


class DbSession:

    """Метод(функция) инициализации класса
        в аргументы принимает модель таблицы с котоорой будет работать"""
    def __init__(self, model: BaseModel):
        self.model = model
        try:
            dbhandle.connect()
        except InternalError as ex:
            print(ex)   # TODO Logger here
            raise ex

    """Методы вызывает создание таблицы внутри субд если таковой нету
        не вызывать если таблица уже есть
        при ошибке запишет в логги и выбросит обратно ошибку"""
    def create_table(self):
        try:
            self.model.create_table()
        except InternalError as ex:
            print(ex)   # TODO Logger here
            raise ex
    """Метод запроса к таблице определенных данных и возвращает запрошенный объект (таблицу) 
    причем с разным размером 
    sql_select - str запроса"""
    def select(self, sql_select: str):
        raise NotImplementedError

    """Метод загружает всю таблицу из бд"""
    def select_all_table(self):
        try:
            return self.model.select()
        except InternalError as ex:
            print(ex)  # TODO Logger here
            raise ex
    """Метод записи/добавления в таблицу данных
        :argument data : object то что заносится в базу данных (должно совпадать с типом стоблца)
        :argument column_name : object название столбца куда добавляешь"""
    def alter(self, data, column_name: str):
        raise NotImplementedError
    """Метод записи в таблицу нового значения (строки)
    :argument row : BaseModel модель которую заносив в таблицу со всеми полями
    выкинет ошибку ArgumentError в несоответствии типов"""
    def insert(self, row_model):
        # TODO raise Error if attrs is incorrect
        row = row_model
        row.save()

    def delete(self):
        raise NotImplementedError

