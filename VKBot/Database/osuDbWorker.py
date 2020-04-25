import logging

from peewee import InternalError

from Database.Connector import DbSession
from Database.Models import OsuModel
from Database.Models.BaseModel import dbhandle


class OsuWorker:

    def __init__(self):
        self.db = DbSession(OsuModel.OsuModel)

    def select_all(self):
        data = self.db.select_all_table()
        items = []
        for item in data:
            items.append({
                'vk_id': item.vk_id,
                'nickname': item.nickname})

        return items

    def select_one(self, osu_vk_id: str):
        try:
            return OsuModel.OsuModel.get(OsuModel.OsuModel.vk_id == osu_vk_id).nickname
        except Exception as ex:
            print(ex)
            return None


    def insert(self, osu_vk_id: str, osu_nickname: str):
        row = OsuModel.OsuModel(vk_id=osu_vk_id, nickname=osu_nickname)
        self.db.insert(row)

    def delete(self, osu_vk_id: str):
        command = OsuModel.OsuModel.get(OsuModel.OsuModel.vk_id == osu_vk_id)
        self.db.delete(command)
    def update(self, vk_id, nickname: str = None,):
        row = OsuModel.OsuModel.get(OsuModel.OsuModel.vk_id == vk_id)
        self.db.delete(row)
        if (nickname is not None):
            row = OsuModel.OsuModel(vk_id=vk_id, nickname=nickname)
            self.db.insert(row)
        elif (nickname is not None):
            pass
