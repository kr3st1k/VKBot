import traceback

from vk_api.longpoll import VkLongPoll, VkEventType
import vk_api
from datetime import datetime
import random
import time
import requests
import json
import sys
import logging
from Database.Models import BaseModel
from Database.osuDbWorker import OsuWorker
from Database.CommandDbWorker import CommandWorker
from StartupLoader.StartupLoader import StartupLoader
from Database.UserDbWorker import UserWorker
from subprocess import Popen, PIPE
import subprocess
import enum
from bancho import osu_session, osu_api

# Предзагрузка конфигураций
config_loader = StartupLoader('config.JSON')

admin_id_int = config_loader.get_admin_id()

# Создание БД воркеров
user_worker = UserWorker()
command_worker = CommandWorker()
osu_worker = OsuWorker()

# Загрузка листов из БД
commands = command_worker.select_all()
users = user_worker.select_all()
nicks = osu_worker.select_all()
names = command_worker.select_all_name()

vk_session = vk_api.VkApi(token=config_loader.get_vk_token())
session_api = vk_session.get_api()
longpoll = VkLongPoll(vk_session)


def send_wo_mention(vk_session, id_type, id, message=None, attachment=None, keyboard=None):
    vk_session.method('messages.send',
                      {id_type: id, 'message': message, 'random_id': random.randint(-2147483648, +2147483648),
                       "attachment": attachment, 'keyboard': keyboard, 'disable_mentions': 1})


def send_message(vk_session, id_type, id, message=None, attachment=None, keyboard=None):
    vk_session.method('messages.send',
                      {id_type: id, 'message': message, 'random_id': random.randint(-2147483648, +2147483648),
                       "attachment": attachment, 'keyboard': keyboard})


def send_message_nolinks(vk_session, id_type, id, message=None, attachment=None, keyboard=None):
    vk_session.method('messages.send',
                      {id_type: id, 'message': message, 'random_id': random.randint(-2147483648, +2147483648),
                       "attachment": attachment, 'keyboard': keyboard, 'dont_parse_links': 1})


def edit_message(vk_session, id_type, id, message=None, message_id=None, attachment=None):
    vk_session.method('messages.edit',
                      {id_type: id, 'message': message, 'message_id': int(message_id), "attachment": attachment})


def send_sticker(vk_session, sticker_id):
    vk_session.method('messages.sendSticker', {'peer_id': event.peer_id, 'random_id': 0,
                                               "sticker_id": sticker_id})


def get_pictures(vk_session, id_group, vk):
    try:
        attachment = ''
        max_num = vk.photos.get(owner_id=id_group, album_id='wall', count=0)['count']
        num = random.randint(1, max_num)
        pictures = vk.photos.get(owner_id=str(id_group), album_id='wall', count=1, offset=num)['items']
        buf = []
        for element in pictures:
            buf.append('photo' + str(id_group) + '_' + str(element['id']))
        # print(buf)
        attachment = ','.join(buf)
        # print(type(attachment))
        # print(attachment)
        return attachment
    except:
        return get_pictures(vk_session, id_group, vk)


"""Возвтращает True если у человека доступ такой же или выше, в иных случаях False"""


def is_permitted(vk_id: int, required_level: int):
    for user in users:
        if user['vk_id'] == int(vk_id):
            return user['access_level'] >= required_level
    return False


def get_random_audio(owner_id, vk_session):
    try:
        list = []
        num = random.randint(1, 100)
        huy = vk_session.method('wall.get', {'owner_id': owner_id, 'count': 1, 'offset': num})['items'][0][
            'attachments']
        for item in huy:
            if item['type'] == "audio":
                list.append((str(item['audio']['owner_id']) + '_' + str(item['audio']['id'])))
        qwert = random.choice(list)
        send_message(vk_session, 'peer_id', event.peer_id, attachment='audio' + qwert)
    except:
        logging.info("error has occurred because of offset" + str(num))
        get_random_audio(owner_id, vk_session)

def get_random_photo_album(album_id ,owner_id, vk_session):
    list = []
    num = random.randint(1, 175)
    huy = vk_session.method('photos.get', {'owner_id': owner_id, 'album_id': album_id, 'offset': num, 'count': 1})[
        'items']
    for item in huy:
        list = str(item['owner_id']) + '_' + str(item['id'])
    qwert = list
    send_message(vk_session, 'peer_id', event.peer_id, attachment='photo' + qwert)


def send_photo(photo):
    url = vk_session.method('photos.getMessagesUploadServer', {'peer_id': 161959141})
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
            hell = vk_session.method('photos.saveMessagesPhoto',
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
            hell = vk_session.method('photos.saveMessagesPhoto',
                                     {'photo': result['photo'], 'server': result["server"], 'hash': result['hash']})
            return 'photo' + str(hell[0]['owner_id']) + '_' + str(hell[0]['id'])
    else:
        send_message(vk_session, 'peer_id', event.peer_id, 'Пошел вон отсюда не приходи сюда больше')
def get_photo_id(photo_id: str):
    puk = vk_session.method('messages.getById', {'message_ids': photo_id,'preview_length': 0})
    ress = []
    for i in range(len(puk['items'][0]['attachments'][0]['photo']['sizes'])):
        ress.append(puk['items'][0]['attachments'][0]['photo']['sizes'][i]['width'])
    jk = max(list(ress))
    for i in range(len(puk['items'][0]['attachments'][0]['photo']['sizes'])):
        smthh = puk['items'][0]['attachments'][0]['photo']['sizes'][i]
        if smthh['width'] == jk:
            juiced = smthh['url']
            return send_photo(juiced)

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        # print('Время: ' + str(datetime.strftime(datetime.now(), "%H:%M:%S")))
        # print('Текст человека: ' + str(event.text))
        print(event.message_id)
        print(event.attachments)
        # try:
        # print(event.user_id)
        # except:
        # print(event.peer_id)
        response = event.text

        for item in commands:
            try:
                if item['name'] == event.text:
                    if item['value'] == ' ':
                        send_message(vk_session, 'peer_id', event.peer_id, attachment=item['attachment'])
                    else:
                        send_message(vk_session, 'peer_id', event.peer_id, item['value'])
            except:
                pass

        if ''.join(list(' '.join(response.split()[:1]))[0:21]) == 'https://osu.ppy.sh/b/':
            try:
                url_arg = response.split('osu.ppy.sh/b/')[1:]
                beatmap_id = str().join(arg for arg in url_arg).split('&')[0]
                send_message(vk_session, 'peer_id', event.peer_id,
                             osu_session.beatmap_get_send(osu_session.get_beatmap_by_id(beatmap_id)),
                             attachment=osu_session.get_bg(osu_session.get_beatmap_by_id(beatmap_id)))
            except:
                pass

        if event.text.lower() == "!stone":
            send_message(vk_session, 'peer_id', event.peer_id,
                         '🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿')

        if event.text.lower() == "!botoff":
            send_message(vk_session, 'peer_id', event.peer_id, "Выключаюсь...")
            break

        spaced_words = str(response).split(' ')
        if spaced_words[0] == '!profile':
            if len(spaced_words) == 1:
                if int(event.user_id) in list(i['vk_id'] for i in nicks):
                    kill = osu_worker.select_one(str(event.user_id))
                    send_message(vk_session, 'peer_id', event.peer_id,
                                                         osu_session.osu_profile_tostring(osu_session.get_profile_by_id(kill)))
                else:
                    send_message(vk_session, 'peer_id', event.peer_id, 'Вы не зарегестрированны! Введи !osume и ник')
            if len(spaced_words) == 2:
                send_message(vk_session, 'peer_id', event.peer_id,
                             osu_session.osu_profile_tostring(osu_session.get_profile_by_id(str(spaced_words[1]))))

        if spaced_words[0] == "!score":
            url_arg = response.split('osu.ppy.sh/b/')[1:]
            mapid = str().join(arg for arg in url_arg).split('&')[0]
            if len(spaced_words) == 2:
                if int(event.user_id) in list(i['vk_id'] for i in nicks):
                    kill = osu_worker.select_one(str(event.user_id))
                    try:
                        send_message_nolinks(vk_session, 'peer_id', event.peer_id,
                                         osu_session.score_beatmap_get(osu_session.get_score_by_id(kill, mapid),
                                                                       osu_session.get_beatmap_by_id(mapid), kill),
                                         attachment=osu_session.get_bg(osu_session.get_beatmap_by_id(mapid)))
                    except: send_message(vk_session, 'peer_id', event.peer_id, 'У вас нет скора на этой мапе или неправильный ник')
                else:
                    send_message(vk_session, 'peer_id', event.peer_id, 'Вы не зарегестрированны! Введи !osume и ник')
            if len(spaced_words) == 3:
                try:
                    send_message_nolinks(vk_session, 'peer_id', event.peer_id,
                                         osu_session.score_beatmap_get(osu_session.get_score_by_id(spaced_words[1], mapid),
                                                                       osu_session.get_beatmap_by_id(mapid),
                                                                       spaced_words[1]),
                                         attachment=osu_session.get_bg(osu_session.get_beatmap_by_id(mapid)))
                except:
                    send_message(vk_session, 'peer_id', event.peer_id,
                                 'У вас нет скора на этой мапе или неправильный ник')
        if spaced_words[0] == "!recent":
            if len(spaced_words) == 1:
                if int(event.user_id) in list(i['vk_id'] for i in nicks):
                    kill = osu_worker.select_one(str(event.user_id))
                    try:
                        send_message_nolinks(vk_session, 'peer_id', event.peer_id,
                                         osu_session.score_beatmap_recent(osu_session.get_recent_by_id(kill),
                                                                          osu_session.get_id_by_recent(kill),
                                                                          kill),
                                         attachment=osu_session.get_bg(osu_session.get_id_by_recent(kill)))
                    except:
                        send_message(vk_session, 'peer_id', event.peer_id, 'Нет недавних игр или неправильно ник!')
                else:
                    send_message(vk_session, 'peer_id', event.peer_id, 'Вы не зарегестрированны! Введи !osume и ник')
            if len(spaced_words) == 2:
                try:
                    send_message_nolinks(vk_session, 'peer_id', event.peer_id,
                                         osu_session.score_beatmap_recent(osu_session.get_recent_by_id(spaced_words[1]),
                                                                          osu_session.get_id_by_recent(spaced_words[1]),
                                                                          spaced_words[1]),
                                         attachment=osu_session.get_bg(osu_session.get_id_by_recent(spaced_words[1])))
                except:
                    send_message(vk_session, 'peer_id', event.peer_id, 'Нет недавних игр или неправильно ник!')

        if spaced_words[0] == "!top":
            if len(spaced_words) == 1:
                if int(event.user_id) in list(i['vk_id'] for i in nicks):
                    kill = osu_worker.select_one(str(event.user_id))
                    send_message_nolinks(vk_session, 'peer_id', event.peer_id, osu_session.score_beatmap_top(kill))
                else:
                    send_message(vk_session, 'peer_id', event.peer_id, 'Вы не зарегестрированны! Введи !osume и ник')
            if len(spaced_words) == 2:
                send_message_nolinks(vk_session, 'peer_id', event.peer_id,
                                     osu_session.score_beatmap_top(spaced_words[1]))

        if event.text.lower() == ".monday":
            send_message(vk_session, 'peer_id', event.peer_id,
                         'Понедельник: ОБЖ каб.321, Физика каб.320, Информатика каб.416, Обществознание Каб.111')
        if event.text.lower() == ".tuesday1":
            send_message(vk_session, 'peer_id', event.peer_id,
                         'Вторник: Физкультура, Физика каб.320, Информатика каб.416')
        if event.text.lower() == ".tuesday2":
            send_message(vk_session, 'peer_id', event.peer_id,
                         'Вторник: Физкультура, Физика каб.320, Информатика каб.416, Обществознание каб.111')
        if event.text.lower() == ".wednesday1":
            send_message(vk_session, 'peer_id', event.peer_id,
                         'Среда: Ко второй паре, Матика каб.303, Литература каб.314, Англ (Леонова) каб.315')
        if event.text.lower() == ".wednesday2":
            send_message(vk_session, 'peer_id', event.peer_id,
                         'Среда: Ко второй паре, Матика каб.303, Литература каб.314, ОБЖ каб.321')
        if event.text.lower() == ".thursday1":
            send_message(vk_session, 'peer_id', event.peer_id,
                         'Четверг: Литература Каб.314, История Каб.230, История каб.230')
        if event.text.lower() == ".thursday2":
            send_message(vk_session, 'peer_id', event.peer_id,
                         'Четверг: Физкультура, История каб.230, Обществознание каб.111')
        if event.text.lower() == ".friday1":
            send_message(vk_session, 'peer_id', event.peer_id,
                         'Пятница: Иностранный язык (Сакерина) каб.304, Матика каб.303, Английский каб.304 (Сакерина) каб.315 (Леонова), Русский каб.314')
        if event.text.lower() == ".friday2":
            send_message(vk_session, 'peer_id', event.peer_id,
                         'Пятница: Астрономия каб.422, Матика каб.303, Английский каб.304 (Сакерина) каб.315 (Леоновa), Русский каб.314 Каб.111')
        if event.text.lower() == ".saturday1":
            send_message(vk_session, 'peer_id', event.peer_id, 'Суббота: Матика каб.303, Химия каб.422')
        if event.text.lower() == ".saturday2":
            send_message(vk_session, 'peer_id', event.peer_id,
                         'Суббота: Матика каб.303, Химия каб.422, Биология каб.403, Экология каб.403')

        if event.text.lower() == "!лоличан":
            code = [-127518015, -101072212]
            attachment = get_pictures(vk_session, random.choice(code), session_api)
            send_message(vk_session, 'peer_id', event.peer_id, 'Держи девочку!', attachment)
        if event.text.lower() == "!murnelis":
            attachment = get_pictures(vk_session, -182090873, session_api)
            send_message(vk_session, 'peer_id', event.peer_id, 'Держи мем!', attachment)
        if event.text.lower() == "!ll":
            attachment = get_pictures(vk_session, -119420102, session_api)
            send_message(vk_session, 'peer_id', event.peer_id, 'Держи LoveLive!', attachment)
        if event.text.lower() == "!rx4d":
            hug = [456241533, 456241532, 456241531, 456241530, 456241529, 456241528, 456241527, 456241526,
                   456241525, 456241524, 456241523, 456241522, 456241521, 456241520, 456241519, 456241518,
                   456241517, 456241516, 456241515, 456241514, 456241513, 456241512, 456241511]
            send_message(vk_session, 'peer_id', event.peer_id,
                         attachment='audio' + str(161959141) + '_' + str(random.choice(hug)))

        if event.text.lower() == "!1канал":
            send_message(vk_session, 'peer_id', event.peer_id, attachment='audio161959141_456241503')
        if event.text.lower() == "!com":
            send_message(vk_session, 'peer_id', event.peer_id, str(names))

        if event.text.lower() == "!шашлык":
            vk_session.method('messages.send', {'peer_id': event.peer_id,
                                                'message': 'Шашлычок ту-ту-ту-ду-ду и лучок ту-ту-ту-ду-ду\nНа природе ту-ту-ту-ду-ду, при погоде ту-ту-ту-ду-ду\nИз свинИны ту-ту-ту-ду-ду, из баранИны ту-ту-ту-ду-ду\nСлюнки текут ту-ту-ту-ду-ду, а гости ждут.',
                                                'random_id': 0,
                                                "attachment": 'audio161959141_456241535'})
        if event.text.lower() == "прикалюха":
            send_message(vk_session, 'peer_id', event.peer_id, attachment='video161959141_456240830')
        if event.text.lower() == "!avx":
            send_message(vk_session, 'peer_id', event.peer_id, attachment='video218534351_456239232')
        if event.text.lower() == "!куда":
            send_message(vk_session, 'peer_id', event.peer_id, attachment='video210923765_456239281')
        spaced_words = str(response).split(' ')
        if spaced_words[0] == "!кто" and len(spaced_words) == 2:
            if event.from_chat:
                if is_permitted(int(event.extra_values['from']), 5):
                    vaal = random.choice(
                        (vk_session.method('messages.getChat', {'chat_id': event.chat_id}))['users'])
                    send_wo_mention(vk_session, 'peer_id', event.peer_id,
                                    "Я думаю, что " + str(spaced_words[1]) + " @id" + str(vaal) + "(он!!!)")
                else:
                    send_message(vk_session, 'chat_id', event.chat_id,
                                 "Permission denied, required level to access: 5")
            else:
                send_message(vk_session, 'peer_id', event.peer_id,
                             "Хей брателла! Это команда только для чатов!! Пошел вон, я не сделаю")
        if event.text.lower() == "!gvn":
            huy = vk_session.method('video.get', {'owner_id': '-164489758', 'count': 200, 'offset': 1})['items']
            qwert = random.choice(list(i for i in huy))
            send_message(vk_session, 'peer_id', event.peer_id, 'Держи gvn!',
                         attachment='video' + str(-164489758) + '_' + str(qwert['id']))
        if event.text == '!статус':
            # TODO WTF rewrite it
            found = False
            for user in users:
                if user['vk_id'] == int(event.extra_values['from']):
                    send_message(vk_session, 'chat_id', event.chat_id, "Вы зарегестрированы как " +
                                 user['association'] + " и ваш текущий уровень: " + str(user['access_level']))
                    found = True
            if not found:
                send_message(vk_session, 'chat_id', event.chat_id, "Вы не зарегестрированы ;d" +
                             " чтобы разегаться юзай !regme <ник>")

        if event.text.lower() == "!rin":
            get_random_photo_album(272155856, 161959141, vk_session)

        if event.text.lower() == "!webm":
            huy = vk_session.method('video.get', {'owner_id': '-30316056', 'count': 200, 'offset': 1})['items']
            qwert = random.choice(list(i for i in huy))
            send_message(vk_session, 'peer_id', event.peer_id, 'Держи webm!',
                         attachment='video' + str(-30316056) + '_' + str(qwert['id']))
        if event.text.lower() == "!mashup":
            get_random_audio(str(-39786657), vk_session)
        spaced_words = str(response).split(' ')
        if spaced_words[0] == "!s" and len(spaced_words) == 2:
            if event.from_chat:
                if is_permitted(int(event.extra_values['from']), 1):
                    try:
                        send_sticker(vk_session, int(spaced_words[1]))
                    except:
                        send_message(vk_session, 'peer_id', event.peer_id,
                                     'Не существует этого стикера или у автора не куплен!',
                                     attachment='video161959141_456240839')
                else:
                    send_message(vk_session, 'peer_id', event.peer_id,
                                 'Poshel von nelizya tebe: @id' + str(event.user_id),
                                 attachment='video161959141_456240839')
            else:
                try:
                    send_sticker(vk_session, int(spaced_words[1]))
                except:
                    send_message(vk_session, 'peer_id', event.peer_id,
                                 'Не существует этого стикера или у автора не куплен!',
                                 attachment='video161959141_456240839')
        if event.text.lower() == "!silvagun":
            get_random_audio(str(-144211359), vk_session)
        spaced_words = str(response).split(' ')

        if event.text.lower() == "!help":
            send_message(vk_session, 'peer_id', event.peer_id,
                         'Картиночки: !лоличан, !murnelis, !ll\nВидео: !куда, !gvn, !webm\nМузло: !rx4d, !1канал, !mashup\nhreni: !тварь, !шанс, !шар, !кто',
                         attachment='doc161959141_544191358')
        if event.text.lower() == ".help":
            send_message(vk_session, 'peer_id', event.peer_id,
                         'Расписание: .monday, .tuesday1, .tuesday2, .wednesday1, .wednesday2, .thursday1, .thursday2, .friday1, .friday2, .saturday1, .saturday2',
                         attachment='doc161959141_544191358')
        if event.text.lower() == "!питон":
            send_message(vk_session, 'peer_id', event.peer_id, attachment='doc161959141_544191358')
        spaced_words = str(response).split(' ')
        if event.text.lower() == "!тварь":
            if event.from_chat:
                if is_permitted(int(event.extra_values['from']), 5):
                    val = random.choice(
                        (vk_session.method('messages.getChat', {'chat_id': event.chat_id}))['users'])
                    send_wo_mention(vk_session, 'peer_id', event.peer_id, "@id" + str(val) + "(тварына!!!)")
                else:
                    send_message(vk_session, 'chat_id', event.chat_id,
                                 "Permission denied, required level to access: 5")
            else:
                send_message(vk_session, 'peer_id', event.peer_id,
                             "Хей брателла! Это команда только для чатов!! Пошел вон, я не сделаю")
        if event.text.lower() == "!everyone":
            if event.from_chat:
                if is_permitted(int(event.extra_values['from']), 5):
                    varl = (vk_session.method('messages.getChat', {'chat_id': event.chat_id})['users'])
                    send_message(vk_session, 'peer_id', event.peer_id,
                                 "[kristian5336|@bruhsoziv][id" + "[id".join(str(i) + "|\u2063]" for i in varl))
                else:
                    send_message(vk_session, 'chat_id', event.chat_id,
                                 "Permission denied, required level to access: 5")
            else:
                send_message(vk_session, 'peer_id', event.peer_id,
                             "Хей брателла! Это команда только для чатов!! Пошел вон, я не сделаю")
        if spaced_words[0] == '!шанс' and len(spaced_words) > 1:
            send_message(vk_session, 'peer_id', event.peer_id,
                         'Шанс того, что ' + ' '.join(spaced_words[1:]) + ' - '
                         + str(random.randint(1, 100)) + '%')
        if spaced_words[0] == '!pic' and len(spaced_words) == 2:
            send_message(vk_session, 'peer_id', event.peer_id, attachment=send_photo(spaced_words[1]))
        if spaced_words[0] == '!шар':
            send_message(vk_session, 'peer_id', event.peer_id, 'Мой ответ - ' +
                         str(random.choice(["Да",
                                            "Нет",
                                            "Скорее всего, но это не точно",
                                            "В душе не ебу если честно",
                                            "Да, это прям 100%",
                                            "нет,ты чё шизоид?"])) + ' ')

        """ Добавление и редактирование в список пользователей """
        if spaced_words[0] == '!regme' and len(spaced_words) == 2:
            if (spaced_words[1] not in list(i['association'] for i in users)) and \
                    (int(event.extra_values['from']) not in list(i['vk_id'] for i in users)):
                if admin_id_int != int(event.extra_values['from']):
                    user_worker.insert(1, int(event.extra_values['from']), spaced_words[1])
                    users.insert(0, {
                        'access_level': 1,
                        'vk_id': int(event.extra_values['from']),
                        'association': spaced_words[1]})
                    send_message(vk_session, 'chat_id', event.chat_id, "вы зарегестировались! Ваш ник: "
                                 + str(spaced_words[1]) + " и уровень 1 :)")

                else:
                    user_worker.insert(10, event.extra_values['from'], spaced_words[1])
                    users.insert(0, {
                        'access_level': 10,
                        'vk_id': event.extra_values['from'],
                        'association': spaced_words[1]})
                    send_message(vk_session, 'chat_id', event.chat_id, "вы зарегестировались админом! Ваш ник: "
                                 + spaced_words[1] + " и уровень 10 (max) :)")

            elif int(event.extra_values['from']) in list(i['vk_id'] for i in users):
                send_message(vk_session, 'chat_id', event.chat_id, "Вы зарегестрированы :c")
            # TODO добавить сообщение для комманды изменения ассоциации
            else:
                send_message(vk_session, 'chat_id', event.chat_id, "Ассоциация занята")
        if spaced_words[0] == '!osume' and len(spaced_words) == 2:
            if (int(event.user_id) not in list(i['vk_id'] for i in nicks)):
                osu_worker.insert(int(event.user_id), spaced_words[1])
                nicks.insert(0, {
                    'vk_id': int(event.user_id),
                    'nickname': spaced_words[1]})
                send_message(vk_session, 'chat_id', event.chat_id, "вы зарегестировались! Ваш ник: "
                                 + str(spaced_words[1]))
            elif int(event.user_id) in list(i['vk_id'] for i in nicks):
                send_message(vk_session, 'chat_id', event.chat_id, "Вы зарегестрированы, можете сменить ник !reosu и ник")
            # TODO добавить сообщение для комманды изменения ассоциации
        if spaced_words[0] == '!reosu' and len(spaced_words) == 2:
            if int(event.user_id) in list(i['vk_id'] for i in nicks):
                for rgp in users:
                    if rgp['vk_id'] == int(event.user_id):
                        osu_worker.update(rgp['vk_id'], spaced_words[1])
                        send_message(vk_session, 'chat_id', event.chat_id,
                                     "Поздравляю вы теперь: " + spaced_words[1])
            else:
                send_message(vk_session, 'chat_id', event.chat_id, "Вы не зарегестрированны! Введи !osume и ник")
        if spaced_words[0] == '!delme':
            if is_permitted(event.extra_values['from'], 1):
                for pgr in users:
                    # print(users)
                    if pgr['vk_id'] == int(event.extra_values['from']):
                        users.remove(pgr)
                        user_worker.delete(pgr['vk_id'])
                        send_message(vk_session, 'chat_id', event.chat_id, "готово?)))")
            else:
                send_message(vk_session, 'chat_id', event.chat_id, "вас и так нет)))")
        # TODO добавить сообщение для комманды изменения ассоциации
        if spaced_words[0] == '!rename' and len(spaced_words) == 3:
            if is_permitted(event.extra_values['from'], 1):
                for pgr in users:
                    if pgr['association'] == spaced_words[1]:
                        index = list(i['association'] for i in users).index(spaced_words[1])
                        commands.pop(index)
                        users[index] = {
                            'access_level': 2,
                            'vk_id': pgr['vk_id'],
                            'association': spaced_words[2]}
                        user_worker.update(pgr['vk_id'], spaced_words[2], 2)
                        send_message(vk_session, 'chat_id', event.chat_id,
                                     "Поздравляю вы теперь: " + spaced_words[2] + ".\n И ваш уровень: 2")
            else:
                send_message(vk_session, 'chat_id', event.chat_id, "Ты кто такой сука?")
        if spaced_words[0] == '!renamelev' and len(spaced_words) == 4:
            if is_permitted(event.extra_values['from'], 10):
                for pgr in users:
                    if pgr['association'] == spaced_words[1]:
                        index = list(i['association'] for i in users).index(spaced_words[1])
                        commands.pop(index)
                        users[index] = {
                            'access_level': int(spaced_words[3]),
                            'vk_id': pgr['vk_id'],
                            'association': spaced_words[2]}
                        user_worker.update(pgr['vk_id'], spaced_words[2], int(spaced_words[3]))
                        send_message(vk_session, 'chat_id', event.chat_id,
                                     "Поздравляю вы теперь: " + spaced_words[2] + "\nИ ваш уровень: " + spaced_words[3])
            else:
                send_message(vk_session, 'chat_id', event.chat_id, "Ты кто такой сука?")
        if spaced_words[0] == '!relev' and len(spaced_words) == 3:
            if is_permitted(event.extra_values['from'], 10):
                for pgr in users:
                    if pgr['association'] == spaced_words[1]:
                        index = list(i['association'] for i in users).index(spaced_words[1])
                        commands.pop(index)
                        users[index] = {
                            'access_level': int(spaced_words[2]),
                            'vk_id': pgr['vk_id'],
                            'association': pgr['association']}
                        user_worker.update(pgr['vk_id'], pgr['association'], int(spaced_words[2]))
                        send_message(vk_session, 'chat_id', event.chat_id,
                                     "Поздравляю вы " + spaced_words[1] + " получили уровень: " + spaced_words[2])
            else:
                send_message(vk_session, 'chat_id', event.chat_id, "Ты кто такой сука?")

        """ Добавление и удаление комманд """
        # TODO добавить уровни и контроль юзеров
        if spaced_words[0] == '!addcom' and len(spaced_words) >= 3:
            if is_permitted(event.user_id, 1):
                if spaced_words[1] == spaced_words[2]:
                    send_message(vk_session, 'chat_id', event.chat_id, "Нельзя добавить эхо-комманду")
                elif spaced_words[1] in list(i['name'] for i in commands):
                    send_message(vk_session, 'chat_id',
                                 event.chat_id, "Нельзя добавить существуюую комманду")
                else:
                    print(spaced_words[-1])
                    if ('http' in spaced_words[-1] or 'https' in spaced_words[-1]) and ('jpeg' in spaced_words[-1] or 'jpg' in spaced_words[-1] or 'png' in spaced_words[-1]):
                        print(spaced_words[-1])
                        try:
                            pic = send_photo(spaced_words[2])
                            command_worker.insert(10, spaced_words[1], ' ', pic)
                            commands.insert(0, {
                                'access_level': 1,
                                'name': spaced_words[1],
                                'value': ' ',
                                'attachment': pic})

                            send_message(vk_session, 'chat_id', event.chat_id,
                                         "Комманда " + spaced_words[1] + " добавлена!")
                        except: send_message(vk_session, 'peer_id', event.peer_id, 'Пошел вон отсюда не приходи сюда больше')
                    if ('photo' in spaced_words[-1] or 'video' in spaced_words[-1] or 'http' not in spaced_words[-1] or 'https' not in spaced_words[-1]) and ('video' in spaced_words[-1] or 'photo' in spaced_words[-1] or 'jpeg' not in spaced_words[-1] or 'jpg' not in spaced_words[-1] or 'png' not in spaced_words[-1]):
                        if 'photo' not in spaced_words[-1]:
                            if  'video' not in spaced_words[-1]:
                                if ''.join(' '.join(response.split()[:1])) != 'vto.pe' or 'vkmix.com' or 'Синий кит' or 'Сова никогда не спит':
                                    command_worker.insert(10, spaced_words[1], ' '.join(spaced_words[2:]), ' ')
                                    commands.insert(0, {
                                                'access_level': 1,
                                                'name': spaced_words[1],
                                                'value': ' '.join(spaced_words[2:]),
                                                'attachment': ''})

                                    send_message(vk_session, 'chat_id', event.chat_id,
                                                 "Комманда " + spaced_words[1] + " добавлена!")
                                else:
                                    send_message(vk_session, 'peer_id', event.peer_id, 'А нафиг пойти не? не добавлю')
                        if 'photo' in spaced_words[-1]:
                            if event.attachments['attach1_type'] == 'photo':
                                print(get_photo_id(event.message_id))
                                id_photo = get_photo_id(event.message_id)
                                command_worker.insert(10, spaced_words[1], ' ', id_photo)
                                commands.insert(0, {
                                    'access_level': 1,
                                    'name': spaced_words[1],
                                    'value': ' ',
                                    'attachment': id_photo})
                                send_message(vk_session, 'chat_id', event.chat_id,
                                 "Комманда " + spaced_words[1] + " добавлена!")
                        if 'video' in spaced_words[-1]:
                            if event.attachments['attach1_type'] == 'video':
                                id_photo = 'video' + event.attachments['attach1']
                                command_worker.insert(10, spaced_words[1], ' ', id_photo)
                                commands.insert(0, {
                                    'access_level': 1,
                                    'name': spaced_words[1],
                                    'value': ' ',
                                    'attachment': id_photo})
                                send_message(vk_session, 'chat_id', event.chat_id,"Комманда " + spaced_words[1] + " добавлена!")
            else:
                send_message(vk_session, 'chat_id', event.chat_id, "Permission denied, required level to access: 5")

        if spaced_words[0] == '!delcom' and len(spaced_words) == 2:
            if is_permitted(event.user_id, 1):
                for item in commands:
                    if item['name'] == spaced_words[1]:
                        command_worker.delete(spaced_words[1])
                        index = list(i['name'] for i in commands).index(spaced_words[1])
                        commands.pop(index)
                        send_message(vk_session, 'chat_id', event.chat_id,
                                     "Комманда " + spaced_words[1] + " удалена!")
                        break
            else:
                send_message(vk_session, 'chat_id', event.chat_id, "Permission denied, required level to access: 5")
# if event.type == VkEventType.MESSAGE_EDIT:
# print('Время: ' + str(datetime.strftime(datetime.now(), "%H:%M:%S")))
# print('edited message: ' + str(event.text))
# print(event.attachments)

