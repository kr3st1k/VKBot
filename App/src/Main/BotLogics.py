import requests
import random


class Bot:
    token = str()
    chat_id = 0

    def __init__(self, token: str, chat_id: int):
        self.chat_id = chat_id
        self.token = token

    def send_message(self):
        pass

    def send_message_chat(self):
        pass

