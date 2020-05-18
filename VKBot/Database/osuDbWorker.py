from collections import Iterable

from Database.Connector import DbConnection, DbConnVersion
from Database.Models import OsuModel


class OsuDbWorker:

    def __init__(self):
        self.db = DbConnection('localhost', 'kr3st', 'root', 'zxc123', 3306, DbConnVersion.SYNC)
        self.table_name = 'osu'

    def select_all(self) -> Iterable:
        data = self.db.select_all_table(self.table_name, ['vk_id', 'nickname', 'mode', 'color', 'bg', 'percent', 'nickname_gatari'])
        items = []
        for item in data:
            items.append({
                'vk_id': item[0],
                'nickname': item[1],
                'mode': item[2],
                'color': item[3],
                'bg': item[4],
                'percent': item[5],
                'nickname_gatari': item[6]})

        return items

    def select_one(self, osu_vk_id: int) -> object:
        return self.db.select_where(self.table_name, {'vk_id': osu_vk_id})

    def select_one_color(self, osu_vk_id: str):
        try:
            return OsuModel.OsuModel.get(OsuModel.OsuModel.vk_id == osu_vk_id).color
        except Exception as ex:
            print(ex)
            return None

    def select_one_bg(self, osu_vk_id: str):
        try:
            return OsuModel.OsuModel.get(OsuModel.OsuModel.vk_id == osu_vk_id).bg
        except Exception as ex:
            print(ex)
            return None
    def select_one_percent(self, osu_vk_id: str):
        try:
            return OsuModel.OsuModel.get(OsuModel.OsuModel.vk_id == osu_vk_id).percent
        except Exception as ex:
            print(ex)
            return None


    def insert(self, osu_vk_id: int, osu_nickname: str, mode: int = 1):
        return self.db.insert_into(self.table_name, {'vk_id': osu_vk_id,
                                                     'nickname': osu_nickname,
                                                     'mode': mode})

    def delete(self, osu_vk_id: int) -> bool:
        return self.db.delete_where(self.table_name, {'vk_id': osu_vk_id})

    def update(self, vk_id, nickname: str = None, color: int = None,mode: int = None,bg: int = None, percent: int = None, nickname_gatari: str = None) -> bool:
        args = locals()
        if any(args.values()) is not None:
            dict_of_updates = {}
            if nickname is not None:
                dict_of_updates.update({'nickname': nickname})
            if mode is not None:
                dict_of_updates.update({'mode': mode})
            if bg is not None:
                dict_of_updates.update({'bg': bg})
            if percent is not None:
                dict_of_updates.update({'percent': percent})
            if color is not None:
                dict_of_updates.update({'color': color})
            if nickname_gatari is not None:
                dict_of_updates.update({'nickname_gatari': nickname_gatari})
            return self.db.update_where(self.table_name, {'vk_id': vk_id}, dict_of_updates)
        else:
            logging.warning('taken zero params and cannot be any update..')
            return False
