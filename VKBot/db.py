from peewee import *
from Database.Models.BaseModel import BaseModel


user = 'root'
password = 'zxc123'.encode('utf8')
db_name = 'kr3st'

dbhandle = MySQLDatabase(
    db_name, user=user,
    password=password,
    host='localhost'
)


class BaseModel(Model):
    class Meta:
        database = dbhandle


class UserModel(BaseModel):
    access_level = IntegerField()   # значения колеблются от 0 до 10
    vk_id = IntegerField(unique=True)
    association = CharField(max_length=100, unique=True)

    class Meta:
        db_table = "users"         # название таблицы
        order_by = ('created_at',)      # как сортированы внутри субд


UserModel.create_table()


