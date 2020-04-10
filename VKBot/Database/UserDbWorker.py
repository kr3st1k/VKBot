from Database.Connector import DbSession
from Database.Models import UserModel


class UserWorker:
    def __init__(self):
        self.db = DbSession(UserModel.UserModel)

    def select_all(self):
        data = self.db.select_all_table()
        items = []
        for item in data:
            items.append({
                'access_level': item.access_level,
                'vk_id': item.vk_id,
                'association': item.association})

        return items

    def insert(self, access_lvl: int, vk_id: int, association: str):
        row = UserModel.UserModel(access_lvl=access_lvl, vk_id=vk_id, association=association)
        self.db.insert(row)

    def delete(self, vk_id: int):
        user = UserModel.UserModel.get(UserModel.UserModel.vk_id == vk_id)
        self.db.delete(user)