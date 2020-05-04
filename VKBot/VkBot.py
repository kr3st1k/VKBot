import asyncio
import telebot
from PIL import Image
from vk_api.longpoll import VkLongPoll, VkEventType
import vk_api
import random
import logging
from datetime import datetime
import requests
import json
import time
from google_images_search import GoogleImagesSearch

class VkTel:
    def __init__(self, token):
        self.token = token
        self.bot = telebot.TeleBot(self.token)
    def send_from_vk(self, text, user_name):
        self.bot.send_message(-1001298351029, str(user_name) + ": " + str(text))
class VkBan:
    def __init__(self, vk_session, session_api):
        self.vk = vk_session
        self.session = session_api

    def send_wo_mention(self, id_type, id, message=None, attachment=None, keyboard=None):
        self.vk.method('messages.send',
                       {id_type: id, 'message': message, 'random_id': random.randint(-2147483648, +2147483648),
                        "attachment": attachment, 'keyboard': keyboard, 'disable_mentions': 1})

    def send_message(self, id_type, id, message=None, attachment=None, keyboard=None):
        self.vk.method('messages.send',
                       {id_type: id, 'message': message, 'random_id': random.randint(-2147483648, +2147483648),
                        "attachment": attachment, 'keyboard': keyboard})

    #TODO переписать это легаси говно без try
    async def ban(self, chat_id, user_id, time_delay='permanent', reason=None):
            if time_delay == 'permanent':
                self.send_message('chat_id', chat_id,
                    'забанен по причине: ' + str(reason) if reason is not None else 'Причина: без причины')
                self.send_message('chat_id', chat_id,'на время: навсегда')
                self.vk.method('messages.removeChatUser', {'chat_id': chat_id, 'user_id': user_id})

            elif 1 <= int(time_delay) <= 100000:
                self.send_message('chat_id', chat_id,
                    'забанен по причине: ' + str(reason) if reason is not None else ' без причины')
                self.send_message('chat_id', chat_id,'на время: ' + str(time_delay) + ' секунд')
                self.vk.method('messages.removeChatUser', {'chat_id': chat_id, 'user_id': user_id})
                time.sleep(float(time_delay))
                self.invite(chat_id, user_id)
    def invite(self, chat_id, user_id):
        """Только для беседы. Требует только id человека для добавления в беседу"""
        try:
            self.vk.method('messages.addChatUser', {'chat_id': chat_id, 'user_id': user_id})
        except Exception:
            self.send_message('chat_id', chat_id,
                'Ошибка добавления... Возможно, пользователя не существует в беседе..')

class VkBot:
    def __init__(self, vk_session, session_api, admin_id):
        self.vk = vk_session
        self.session = session_api
        self.google = GoogleImagesSearch('AIzaSyAMSQjEUlI9cg_B8beR-XtJZwkJl4aVnLI', '005710364809358714397:hpc0r63jwas')
        self.my_id = admin_id
    #TODO переписать это легаси говно без try
    def send_wo_mention(self, id_type, id, message=None, attachment=None, keyboard=None):
        self.vk.method('messages.send',
                       {id_type: id, 'message': message, 'random_id': random.randint(-2147483648, +2147483648),
                        "attachment": attachment, 'keyboard': keyboard, 'disable_mentions': 1})

    def send_message(self, id_type, id, message=None, attachment=None, keyboard=None):
        self.vk.method('messages.send',
                       {id_type: id, 'message': message, 'random_id': random.randint(-2147483648, +2147483648),
                        "attachment": attachment, 'keyboard': keyboard})

    def send_message_nolinks(self, id_type, id, message=None, attachment=None, keyboard=None):
        self.vk.method('messages.send',
                       {id_type: id, 'message': message, 'random_id': random.randint(-2147483648, +2147483648),
                        "attachment": attachment, 'keyboard': keyboard, 'dont_parse_links': 1})

    def edit_message(self, id_type, id, message=None, message_id=None, attachment=None):
        self.vk.method('messages.edit',
                       {id_type: id, 'message': message, 'message_id': int(message_id), "attachment": attachment})

    def send_sticker(self, id, sticker_id):
        self.vk.method('messages.sendSticker', {'peer_id': id, 'random_id': 0,
                                                "sticker_id": sticker_id})
    def name_last_user(self, id):
        shish = self.vk.method('users.get', {'user_ids': id})
        return shish

    def get_random_video(self, owner_id):
        huy = self.vk.method('video.get', {'owner_id': str(owner_id), 'count': 200, 'offset': 1})['items']
        hh = random.choice(list(i for i in huy))
        return hh['id']

    def get_pictures(self, id_group):
        attachment = ''
        max_num = self.session.photos.get(owner_id=id_group, album_id='wall', count=0)['count']
        num = random.randint(1, max_num)
        pictures = self.session.photos.get(owner_id=str(id_group), album_id='wall', count=1, offset=num)['items']
        buf = []
        for element in pictures:
            buf.append('photo' + str(id_group) + '_' + str(element['id']))
        attachment = ','.join(buf)
        return attachment

    def get_random_audio(self, owner_id):
        try:
            list = []
            num = random.randint(1, 100)
            huy = self.vk.method('wall.get', {'owner_id': owner_id, 'count': 1, 'offset': num})['items'][0][
                'attachments']
            for item in huy:
                if item['type'] == "audio":
                    list.append((str(item['audio']['owner_id']) + '_' + str(item['audio']['id'])))
            qwert = random.choice(list)
            return qwert
        except:
            logging.info("error has occurred because of offset" + str(num))
            self.get_random_audio(owner_id)

    def get_all(self, chat_id):
        return (self.vk.method('messages.getChat', {'chat_id': chat_id})['users'])

    def get_random_person(self, chat_id):
        return random.choice(
            (self.vk.method('messages.getChat', {'chat_id': chat_id}))['users'])

    def get_random_photo_album(self,count , album_id, owner_id):
        list = []
        num = random.randint(1, count)
        huy = self.vk.method('photos.get', {'owner_id': owner_id, 'album_id': album_id, 'offset': num, 'count': 1})[
            'items']
        for item in huy:
            list = str(item['owner_id']) + '_' + str(item['id'])
        qwert = list
        return 'photo' + qwert

    def send_photo(self, photo):
        url = self.vk.method('photos.getMessagesUploadServer', {'peer_id': self.my_id})
        image_formats = ("image/png", "image/jpeg", "image/jpg")
        r = requests.head(photo)
        if r.headers["content-type"] in image_formats:
            if ''.join(photo) == '.jpg' or '.jpeg':
                pas = requests.get(photo)
                out = open('vkphoto.jpg', "wb")
                out.write(pas.content)
                out.close()
                file = open('vkphoto.jpg', 'rb')
                files = {'photo': file}
                nani = requests.post(url['upload_url'], files=files)
                result = json.loads(nani.text)
                hell = self.vk.method('photos.saveMessagesPhoto',
                                      {'photo': result['photo'], 'server': result["server"], 'hash': result['hash']})
                return 'photo' + str(hell[0]['owner_id']) + '_' + str(hell[0]['id'])
            if ''.join(photo) == '.png':
                pas = requests.get(photo)
                out = open('vkphoto.png', "wb")
                out.write(pas.content)
                out.close()
                file = open('vkphoto.png', 'rb')
                files = {'photo': file}
                nani = requests.post(url['upload_url'], files=files)
                result = json.loads(nani.text)
                hell = self.vk.method('photos.saveMessagesPhoto',
                                      {'photo': result['photo'], 'server': result["server"], 'hash': result['hash']})
                return 'photo' + str(hell[0]['owner_id']) + '_' + str(hell[0]['id'])


    def send_graphiti(self, photo):
        if ''.join(photo) == '.jpg' or '.jpeg':
            pas = requests.get(photo)
            im1 = Image.open(r'profile.jpg')
            im1.save(r'profile.png')
            out = open('profile.png', "wb")
            out.write(pas.content)
            out.close()
            url = self.vk.method("docs.getMessagesUploadServer", {
                'peer_id': self.my_id,
                'type': 'graffiti'})
            file = [('file', ('profile.png', open('profile.png', 'rb')))]
            nani = requests.post(url['upload_url'], files=file)
            result = json.loads(nani.text)
            print(result)
            hell = self.vk.method('docs.save',
                                     {'file': result['file']})
            return 'graffiti' + str(hell['graffiti']['owner_id']) + '_' + str(hell['graffiti']['id'])
        if ''.join(photo) == '.png':
            pas = requests.get(photo)
            out = open('profile.png', "wb")
            out.write(pas.content)
            out.close()
            url = self.vk.method("docs.getMessagesUploadServer", {
                'peer_id': self.my_id,
                'type': 'graffiti'})
            file = [('file', ('profile.png', open('profile.png', 'rb')))]
            nani = requests.post(url['upload_url'], files=file)
            result = json.loads(nani.text)
            print(result)
            hell = self.vk.method('docs.save',
                                  {'file': result['file']})
            return 'graffiti' + str(hell['graffiti']['owner_id']) + '_' + str(hell['graffiti']['id'])

    def photo_google(self, google):
        def my_progressbar(url):
            print(url)
        gis = GoogleImagesSearch('AIzaSyAMSQjEUlI9cg_B8beR-XtJZwkJl4aVnLI', '005710364809358714397:hpc0r63jwas', progressbar_fn=my_progressbar)
        _search_params = {
            'q': google,
        }
        gis.search(search_params=_search_params)

    def get_photo_id(self, photo_id: str, graffiti=None):
        if graffiti == None:
            puk = self.vk.method('messages.getById', {'message_ids': photo_id, 'preview_length': 0})
            ress = []
            for i in range(len(puk['items'][0]['attachments'][0]['photo']['sizes'])):
                ress.append(puk['items'][0]['attachments'][0]['photo']['sizes'][i]['width'])
            jk = max(list(ress))
            for i in range(len(puk['items'][0]['attachments'][0]['photo']['sizes'])):
                smthh = puk['items'][0]['attachments'][0]['photo']['sizes'][i]
                if smthh['width'] == jk:
                    juiced = smthh['url']
                    return self.send_photo(juiced)
        if graffiti != None:
            puk = self.vk.method('messages.getById', {'message_ids': photo_id, 'preview_length': 0})
            ress = []
            for i in range(len(puk['items'][0]['attachments'][0]['photo']['sizes'])):
                ress.append(puk['items'][0]['attachments'][0]['photo']['sizes'][i]['width'])
            jk = max(list(ress))
            for i in range(len(puk['items'][0]['attachments'][0]['photo']['sizes'])):
                smthh = puk['items'][0]['attachments'][0]['photo']['sizes'][i]
                if smthh['width'] == jk:
                    juiced = smthh['url']
                    return self.send_graphiti(juiced)
    def add_me(self, user_id):
        self.vk.method('friends.add', {'user_id': user_id})
