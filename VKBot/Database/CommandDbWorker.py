import logging

from Database.Connector import DbConnection, DbConnVersion
from Database.Models import CommandModel


class CommandDbWorker:

    def __init__(self):
        self.db = DbConnection('localhost', 'kr3st', 'root', 'zxc123', 3306, DbConnVersion.SYNC)
        self.table_name = 'categories'

    def select_all(self):
        data = self.db.select_all_table(self.table_name, ['access_level', 'name', 'value', 'attachment'])
        items = []
        for item in data:
            items.append({
                'access_level': item[0],
                'name': item[1],
                'value': item[2],
                'attachment': item[3]})

        return items
    def select_all_names(self):
        data = self.db.select_all_table(self.table_name, ['name'])
        items = ''
        for item in data:
            items = items + ''.join(item) + ', '
        return items + '[end.]'

    def insert(self, access_lvl: int, comm_name: str, comm_value: str = '', comm_attachment: str = None):
        if comm_attachment is not None:
            return self.db.insert_into(self.table_name, {'access_level': access_lvl,
                                                         'name': comm_name,
                                                         'value': comm_value,
                                                         'attachment': comm_attachment})
        else:
            return self.db.insert_into(self.table_name, {'access_level': access_lvl,
                                                         'name': comm_name,
                                                         'value': comm_value})

    def delete(self, comm_name: str):
        return self.db.delete_where(self.table_name, {'name': comm_name})

    def update(self,  comm_name: str, access_lvl: int = None, value: str = None, attachment: str = None) -> bool:

        args = locals()
        if any(args.values()) is not None:
            dict_of_updates = {}
            if access_lvl is not None:
                dict_of_updates.update({'access_level': access_lvl})
            if value is not None:
                dict_of_updates.update({'value': value})
            if attachment is not None:
                dict_of_updates.update({'attachment': attachment})
            return self.db.update_where(self.table_name, {'name': comm_name}, dict_of_updates)
        else:
            logging.warning('taken zero params and cannot be any update..')
            return False
