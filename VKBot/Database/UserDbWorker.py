import logging
from collections import Iterable, Sized

from Database.Connector import DbConnection, DbConnVersion
from Database.Models import UserModel


class UserDbWorker:
    def __init__(self):
        self.table_name = 'users'
        self.db = DbConnection('localhost', 'kr3st', 'root', 'zxc123', 3306, DbConnVersion.SYNC)

    def select_all(self) -> Iterable:
        data = self.db.select_all_table(self.table_name, ['access_level', 'vk_id', 'association', 'lvl_exp'])
        items = []
        for item in data:
            items.append({
                'access_level': item[0],
                'vk_id': item[1],
                'association': item[2],
                'lvl_exp': item[3]})

        return items

    def insert(self, access_level: int, vk_id: int, association: str, level_exp=0) -> bool:
        return self.db.insert_into(self.table_name, {'access_level': access_level,
                                                     'vk_id': vk_id,
                                                     'association': association,
                                                     'lvl_exp': level_exp})

    def delete(self, vk_id: int) -> bool:
        return self.db.delete_where(self.table_name, {'vk_id': vk_id})

    def update(self, vk_id, association: str = None, level: int = None, exp: float = None) -> bool:

        args = locals()
        if any(args.values()) is not None:
            dict_of_updates = {}
            if association is not None:
                dict_of_updates.update({'association': association})
            if level is not None:
                dict_of_updates.update({'access_level': level})
            if exp is not None:
                dict_of_updates.update({'lvl_exp': exp})
            return self.db.update_where(self.table_name, {'vk_id': vk_id}, dict_of_updates)
        else:
            logging.warning('taken zero params and cannot be any update..')
            return False
