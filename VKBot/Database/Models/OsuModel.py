from peewee import *
from Database.Models.BaseModel import BaseModel


class OsuModel(BaseModel):
    vk_id = IntegerField(unique=True)
    nickname = CharField(max_length=100)
    nickname_gatari = CharField(max_length=100)
    mode = IntegerField()
    color = IntegerField()
    bg = CharField(max_length=100)
    percent = IntegerField()
    class Meta:
        db_table = "osu"         # название таблицы
        order_by = ('created_at',)      # как сортированы внутри субд

