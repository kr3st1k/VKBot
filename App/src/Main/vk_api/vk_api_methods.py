import requests
import random

class VKEvents:
    MESSAGE_NEW = 1
    MESSAGE_TYPING = 2
    MESSAGE_PICT_NEW = 3
    KICKED_USER = 4

    class Exceptions:
        MESSAGE_IO_EXCEPTION = 1
        KICK_IO_EXCEPTION = 2
        IO_EXCEPTION = 3
        CONSIDERING_EXCEPTION = 4
        VK_IO_EXCEPTION = 4200
        BAD_TOKEN_ARGS = 401
        VK_API_ERROR = 404
        BAD_SYNTAX = 102

        def print_stack_exception(self):
            pass

    def __init__(self):
        pass

class VKApi:
    token = str()
    api_url = "https://api.vk.com/method/"

    def __init__(self, token, mode=None):
        self.token = token

    @staticmethod
    def get_url_api(self):
        return self.api_url

    @classmethod
    def vk_method(self, method_name: str, parameters: list, validation_num=51181, return_JSON_mode = False):
        """Общий метод всего vk_api


            ;method_str : str => одно слово
            :parameters : str => цель аргументов без пробелов соединенных &
            ;validation_num : str => номер правильного response номера.По дефолту 51181 для сообщений / для исключений 1

            :return 0 если сообщение дошло
            :return -1 если невозможно открыть соединение или ошибка апи
            :return {404: dict()} если были даны неправельные аргументы
        """
        if return_JSON_mode:
            try:
                url = self.api_url + method_name + '?' + parameters + '&access_token=' + self.token + '&v=5.101'
                validation = requests.get(url).json()
                if validation['response'] is not None:
                    return validation
                else:
                    print('got wrong args..')
                    return {404: validation}  # bad_args
            except Exception:
                return -1  # Connection exception
        else:
            try:
                url = self.api_url + method_name + '?' + parameters + '&access_token=' + self.token + '&v=5.101'
                print(url)
                validation = requests.get(url).json()
                if validation['response'] is not None:
                    return 0
                else:
                    print('got wrong args..')
                    return {404: validation}  # bad_args
            except Exception:
                return -1  # Connection exception

    @classmethod
    def send_message(self, type_id: str, id: str, message: str = None, attachment: str = None, keyboard=None):
        """Метод vk_api отправки сообщений


        type_id : str =>         либо 'chat_id' либо 'user_id'. В случае неправлиного аргумента type_id возвращает 102
             id : str(integer)   идинтификационный номер адресуемого ползьзователя или же беседы
        message : str            строковое сообщение; на вк апи работает \n и др
        attachment: str приложение к сообщению (см документацию vk api)


                    (то же что и общий метод vk api)
        :returns: :return 0 если сообщение дошло
                  :return -1 если невозможно открыть соединение
                  :return {404: dict()} если были даны неправельные аргументы
        :return 102 если не было дано правильного type_id  (chat_id/user_id)
        """
        if type_id == 'chat_id':
            args = 'chat_id=' + id
        elif type_id == 'user_id':
            args = 'user_id=' + id
        else:
            return 102  # Bad Syntax
        args = args + '&random_id=' + str(random.randint(111, 453333)) + '&message=' + message
        if attachment is not None:
            args = args + '&attachment=' + attachment
        if keyboard is not None:
            args = args + '&keyboard=' + keyboard
        return self.vk_method('messages.send', args, 51181)

    @classmethod
    def remove_from_chat(self, user_id: str, chat_id: str):
        """Метод vk_api для исключения из беседы
        user_id : str(integer)   идинтификационный номер исключаемого ползьзователя
        chat_id : str(short_int) идентификатор беседы


                    (то же что и общий метод vk api)
        :returns: :return 0 если сообщение дошло
                  :return -1 если невозможно открыть соединение
                  :return {404: dict()} если были даны неправельные аргументы
        """
        args = 'chat_id=' + chat_id + '&user_id=' + user_id
        return self.vk_method('messages.removeChatUser', args, 1)

    @classmethod
    def invite_to_chat(self, user_id: str, chat_id: str):
        """Метод vk_api добавления в беседу

         user_id : str(integer)   идинтификационный номер исключаемого ползьзователя
        chat_id : str(short_int) идентификатор беседы


                    (то же что и общий метод vk api)
        :returns: :return 0 если сообщение дошло
                  :return -1 если невозможно открыть соединение или невозможно пригласить
                  :return {404: dict()} если были даны неправельные аргументы

        """

        args = 'chat_id=' + chat_id + '&user_id=' + user_id
        return self.vk_method('messages.addChatUser', args, 1)

