from peewee import *
from Database.Models.BaseModel import BaseModel


class CommandModel(BaseModel):
    access_level = IntegerField(default=1)   # значения колеблются от 0 до 10
    name = CharField(max_length=100, unique=True)
    value = CharField(max_length=4000)

    class Meta:
        db_table = "categories"         # название таблицы
        order_by = ('created_at',)      # как сортированы внутри субд
