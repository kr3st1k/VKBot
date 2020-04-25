from Database.Connector import DbSession
from Database.Models import CommandModel


class CommandWorker:

    def __init__(self):
        self.db = DbSession(CommandModel.CommandModel)

    def select_all(self):
        data = self.db.select_all_table()
        items = []
        for item in data:
            items.append({
                'access_level': item.access_level,
                'name': item.name,
                'value': item.value,
                'attachment': item.attachment})

        return items

    def insert(self, access_lvl: int, comm_name: str, comm_value: str, comm_attachment: str):
        row = CommandModel.CommandModel(access_lvl=access_lvl, name=comm_name, value=comm_value, attachment=comm_attachment)
        self.db.insert(row)

    def delete(self, comm_name: str):
        command = CommandModel.CommandModel.get(CommandModel.CommandModel.name == comm_name)
        self.db.delete(command)