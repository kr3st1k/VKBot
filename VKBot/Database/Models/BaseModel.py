
from peewee import *


"""эта секция нужна для ОРМ конфигурации @user - название юзера MySQL субд
  пароль от субд понятно, и db_name - название базы данных проекта внутри MySQL
  host = localhost не трогать на своем компе"""


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

