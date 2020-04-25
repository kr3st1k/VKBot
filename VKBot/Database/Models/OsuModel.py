from peewee import *
from Database.Models.BaseModel import BaseModel


class OsuModel(BaseModel):
    vk_id = IntegerField(unique=True)
    nickname = CharField(max_length=100)

    class Meta:
        db_table = "osu"         # название таблицы
        order_by = ('created_at',)      # как сортированы внутри субд

