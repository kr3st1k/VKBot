import logging

from peewee import InternalError

from Database.Connector import DbSession
from Database.Models import UserModel
from Database.Models.BaseModel import dbhandle


class UserWorker:
    def __init__(self):
        self.db = DbSession(UserModel.UserModel)

    def select_all(self):
        data = self.db.select_all_table()
        items = []
        print(data)
        for item in data:
            items.append({
                'access_level': item.access_level,
                'vk_id': item.vk_id,
                'association': item.association})

        return items

    def insert(self, access_level: int, vk_id: int, association: str):
        row = UserModel.UserModel(access_level=access_level, vk_id=vk_id, association=association)
        self.db.insert(row)
    def delete(self, vk_id: int):
        user = UserModel.UserModel.get(UserModel.UserModel.vk_id == vk_id)
        self.db.delete(user)
    def update(self, vk_id, association: str = None, level: int = None):
        row = UserModel.UserModel.get(UserModel.UserModel.vk_id == vk_id)
        self.db.delete(row)
        if (association is not None) and (level is not None):
            row = UserModel.UserModel(access_level=level, vk_id=vk_id, association=association)
            self.db.insert(row)
        elif (association is not None) and (level is None):
            pass
#userworker=UserWorker()
#userworker.update(161959141,'9, 'mouse')