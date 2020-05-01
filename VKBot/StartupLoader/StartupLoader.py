import json
import logging
import pathlib

from peewee import InternalError

from Database.CommandDbWorker import CommandWorker
from Database.Models.BaseModel import dbhandle
from Database.UserDbWorker import UserWorker


class StartupLoader:
    def __init__(self, config_name: str):
        logging.basicConfig(filename="logBook.log", level=logging.INFO)
        with open(str(pathlib.Path().absolute()) + '/StartupLoader/' + config_name) as json_file:
            self.data = json.load(json_file)

    def load_users_list(self) -> list:
        user_worker = UserWorker()
        return user_worker.select_all()

    def load_commands_list(self) -> list:
        command_worker = CommandWorker()
        return command_worker.select_all()

    def get_admin_id(self) -> int:
        return self.data['bot_admin']

    def get_vk_token(self) -> str:
        return self.data['token']
    def get_osu_token(self) -> str:
        return self.data['osu_token']
    def get_tel_api(self) -> str:
        return self.data['tel_api']