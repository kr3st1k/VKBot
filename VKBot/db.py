from peewee import *


user = 'ubuntu'
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


class OsuModel(BaseModel):
    vk_id = IntegerField(unique=True)
    nickname = CharField(max_length=100, unique=True)

    class Meta:
        db_table = "osu"         # название таблицы
        order_by = ('created_at',)      # как сортированы внутри субд


OsuModel.create_table()


