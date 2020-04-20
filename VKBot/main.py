import traceback

from vk_api.longpoll import VkLongPoll, VkEventType
import vk_api
from datetime import datetime
import random
import time
import requests
import json
import logging
from Database.Models import BaseModel
from Database.CommandDbWorker import CommandWorker
from StartupLoader.StartupLoader import StartupLoader
from Database.UserDbWorker import UserWorker
from subprocess import Popen, PIPE
import subprocess
import enum


# Предзагрузка конфигураций
config_loader = StartupLoader('config.JSON')

admin_id_int = config_loader.get_admin_id()

# Создание БД воркеров
user_worker = UserWorker()
command_worker = CommandWorker()

# Загрузка листов из БД
commands = command_worker.select_all()
users = user_worker.select_all()

vk_session = vk_api.VkApi(token="vktoken")
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


def get_osu_token():
    return 'osutoken'


def send_photo(photo):
    url = vk_session.method('photos.getMessagesUploadServer', {'peer_id': 161959141})
    bg = photo
    wget.download(bg, 'photo.jpg')
    file = open('photo.jpg', 'rb')
    files = {'photo': file}
    nani = requests.post(url['upload_url'], files=files)
    result = json.loads(nani.text)
    hell = vk_session.method('photos.saveMessagesPhoto',
                             {'photo': result['photo'], 'server': result["server"], 'hash': result['hash']})


class osu_api:
    key = None
    mode = None  # std_mode
    api_url = 'https://osu.ppy.sh/api/'

    def __init__(self, token_key: str, mode=0):
        self.key = token_key
        self.mode = mode

    def request_json(self, url: str, args: str):
        try:
            return requests.get(str(url) + 'k=' + self.key).json()
        except:
            return ""

    def mods(self, num):
        mods_osu = {}
        modes = []
        opt = {'HalfTime': 256, 'NoFail': 1, 'Easy': 2, 'HardRock': 16,
               'Hidden': 8, 'FlashLight': 1024, 'SpunOut': 4096, 'TouchDevice': 4,
               'Relax': 128, 'Autoplay': 2048, 'Relax2': 8192, 'ScoreV2': 536870912}
        for key, value in opt.items():
            if value & num == value:
                mods_osu[key] = value
        num_s = 0

        for key in mods_osu:
            num_s = num_s + mods_osu[key]
        if num_s != num:
            if 576 + num_s == num:
                mods_osu['NightCore'] = 576
            if 32 + num_s == num:
                mods_osu['SuddenDeath'] = 32
            if 64 + num_s == num:
                mods_osu['DoubleTime'] = 64
            if 16416 + num_s == num:
                mods_osu['Perfect'] = 16416

            if 576 + 32 + num_s == num:
                mods_osu['NightCore'] = 576
                mods_osu['SuddenDeath'] = 32
            if 576 + 16416 + num_s == num:
                mods_osu['NightCore'] = 576
                mods_osu['Perfect'] = 16416

            if 64 + 32 + num_s == num:
                mods_osu['DoubleTime'] = 64
                mods_osu['SuddenDeath'] = 32
            if 64 + 16416 + num_s == num:
                mods_osu['DoubleTime'] = 64
                mods_osu['Perfect'] = 16416

        if mods_osu == {}:
            mods_osu['Нет'] = 'Нет'

        for key in mods_osu:
            modes.append(key)

        return ','.join(modes)

    def get_bg(self, beatmap_data: dict):
        pic = 'https://assets.ppy.sh/beatmaps/{0}/covers/cover.jpg'.format(str(beatmap_data['beatmapset_id']))
        url = vk_session.method('photos.getMessagesUploadServer', {'peer_id': 161959141})
        pas = requests.get(pic)
        out = open('photo.jpg', "wb")
        out.write(pas.content)
        out.close()
        file = open('photo.jpg', 'rb')
        files = {'photo': file}
        nani = requests.post(url['upload_url'], files=files)
        result = json.loads(nani.text)
        hell = vk_session.method('photos.saveMessagesPhoto',
                                 {'photo': result['photo'], 'server': result["server"], 'hash': result['hash']})
        return 'photo' + str(hell[0]['owner_id']) + '_' + str(hell[0]['id'])

    def get_profile_by_id(self, user_id: str):
        try:
            return requests.get(
                self.api_url + 'get_user?' + 'k=' + self.key + '&u=' + user_id + '&m=' + str(self.mode)).json()[0]
        except:
            return "1"

    def get_beatmap_by_id(self, beatmap_id: str):
        return requests.get(
            self.api_url + 'get_beatmaps?' + 'k=' + self.key + '&b=' + beatmap_id + '&m=' + str(self.mode)).json()[0]

    def get_score_by_id(self, user_id: str, beatmap_id: str):
        return requests.get(
            self.api_url + 'get_scores?' + 'k=' + self.key + '&b=' + beatmap_id + '&u=' + user_id + '&m=' + str(
                self.mode)).json()[0]

    def top_play(self, user_id: str)-> str:
        result = ''
        for item in requests.get(self.api_url + 'get_user_best?' + 'k=' + self.key + '&u=' + user_id + '&m=' + str(0) + '&limit=' + str(5)).json():
            result += str(item)
            result += str(self.get_beatmap_by_id(item['beatmap_id']))
            result += '\n' + '\n' + '\n'
        return result




    def get_recent_by_id(self, user_id: str):
        return requests.get(
            self.api_url + 'get_user_recent?' + 'k=' + self.key + '&u=' + user_id + '&m=' + str(self.mode)).json()[0]

    def get_top_by_id(self, user_id: str):
        return requests.get(
            self.api_url + 'get_user_recent?' + 'k=' + self.key + '&u=' + user_id + '&m=' + str(self.mode)).json()[0]

    def get_id_by_recent(self, user_id: str):
        r = self.get_recent_by_id(user_id)['beatmap_id']
        return requests.get(
            self.api_url + 'get_beatmaps?' + 'k=' + self.key + '&b=' + r + '&m=' + str(self.mode)).json()[0]
    def bb(self, user_id: str):
        return requests.get(
            self.api_url + 'get_beatmaps?' + 'k=' + self.key + '&b=' + self.get_recent_by_id(user_id)['beatmap_id'] + '&m=' + str(self.mode)).json()[0]

    def get_bg_rec(self, user_id: str):
        try:
            pic = 'https://assets.ppy.sh/beatmaps/{0}/covers/cover.jpg'.format(str(self.bb(user_id)['beatmapset_id']))
            url = vk_session.method('photos.getMessagesUploadServer', {'peer_id': 161959141})
            pas = requests.get(pic)
            out = open('rec.jpg', "wb")
            out.write(pas.content)
            out.close()
            file = open('rec.jpg', 'rb')
            files = {'photo': file}
            nani = requests.post(url['upload_url'], files=files)
            result = json.loads(nani.text)
            hell = vk_session.method('photos.saveMessagesPhoto',
                                     {'photo': result['photo'], 'server': result["server"], 'hash': result['hash']})
            return 'photo' + str(hell[0]['owner_id']) + '_' + str(hell[0]['id'])
        except:
            return 'video161959141_456240839'
    def osu_profile_tostring(self, profile_data: dict):
        try:
            pp = profile_data['pp_raw'].split(".")
            if len(pp) == 2:
                rawpp = int(pp[0])
                if float(pp[1]) > 0.5:
                    rawpp + 1
            else:
                rawpp = int(pp[0])
            return 'Ник: ' + profile_data['username'] + \
                   '\n' + 'Количество игр: ' + profile_data['playcount'] + \
                   '\n' + 'Мировой ранг: #' + profile_data['pp_rank'] + \
                   '\n' + 'Ранг по стране: #' + profile_data['pp_country_rank'] + \
                   '\n' + 'PP: ' + str(rawpp) + \
                   '\n' + 'Часов в игре: ' + str(int(int(profile_data['total_seconds_played']) / 3600)) + 'h' + \
                   '\n' + 'Точность: ' + str("%.2f" % float(profile_data['accuracy'])) + '%' + \
                   '\n\n' + 'Профиль: https://osu.ppy.sh/u/' + profile_data['username'] + \
                   '\n' + 'osu!Skills: http://osuskills.com/user/' + profile_data['username']

        except Exception:
            return "дурак, это кто?"

    def beatmap_get_send(self, beatmap_data: dict):
        info = beatmap_data['artist'] + ' - ' + beatmap_data['title'] + \
               '\n' + '[' + beatmap_data['version'] + ']' + ' Создатель: ' + beatmap_data['creator'] + \
               '\n' + 'Комбо:  ' + beatmap_data['max_combo'] + \
               '\n' + 'Длительность:  ' + str(int(beatmap_data['hit_length']) // 60) + ':' + str(
            int(beatmap_data['hit_length']) % 60) + \
               '\n' + 'AR ' + beatmap_data['diff_approach'] + ' | OD ' + beatmap_data['diff_overall'] + \
               ' | HP ' + beatmap_data['diff_overall'] + ' | CS ' + beatmap_data["diff_size"] + ' | ' + str(
            "%.2f" % float(beatmap_data['difficultyrating'])) + '*'
        return info

    def score_beatmap_get(self, usermap_info: dict, beatmap_data: dict, user_id: str):
        accur = int(usermap_info['count50']) * 50 + int(usermap_info['count100']) * 100 + int(usermap_info['count300']) * 300
        accur1 = int(usermap_info['count50']) + int(usermap_info['count100']) + int(usermap_info['count300']) + int(usermap_info['countmiss'])
        accur2 = 300 * accur1
        accur = accur / accur2
        count = len(str(accur))
        usermap_info["accuracy"] = accur
        if count > 3:
            accur = accur * 100
            accur = round(float(accur), 2)
            usermap_info["accuracy"] = accur
        elif type(accur) == float:
            accur = round(float(accur))
            usermap_info["accuracy"] = accur
        info = beatmap_data['artist'] + ' - ' + beatmap_data['title'] + \
               '\n' + '[' + beatmap_data['version'] + ']' + '\n' + ' Map Creator: ' + beatmap_data['creator'] + \
               '\n' + 'Сыграно игроком: ' + user_id + \
               '\n' + 'Очки: ' + usermap_info['score'] + \
               '\n' + 'Аккуратность: ' + str(usermap_info["accuracy"]) + '%' + \
               '\n' + 'Комбо: ' + usermap_info['maxcombo'] + '/' + beatmap_data['max_combo'] + \
               '\n' + usermap_info['count300'] + '/' + usermap_info['count100'] + '/' + usermap_info['count50'] + \
                                         '\n' + 'Миссы: ' + usermap_info['countmiss'] + \
               '\n' + 'Ранк: ' + usermap_info['rank'] + \
               '\n' + 'Моды: ' + self.mods(int(usermap_info['enabled_mods'])) + \
               '\n' + 'PP: ' + str("%.2f" % float(usermap_info['pp'])) + \
               '\n' + 'AR ' + beatmap_data['diff_approach'] + ' | OD ' + beatmap_data['diff_overall'] + \
               ' | HP ' + beatmap_data['diff_overall'] + ' | CS ' + beatmap_data["diff_size"] + ' | ' + str(
            "%.2f" % float(beatmap_data['difficultyrating'])) + '*'
        return info
    def score_beatmap_recent(self, usermap_info: dict, beatmap_data: dict, user_id: str):
        accur = int(usermap_info['count50']) * 50 + int(usermap_info['count100']) * 100 + int(usermap_info['count300']) * 300
        accur1 = int(usermap_info['count50']) + int(usermap_info['count100']) + int(usermap_info['count300']) + int(usermap_info['countmiss'])
        accur2 = 300 * accur1
        accur = accur / accur2
        count = len(str(accur))
        usermap_info["accuracy"] = accur
        if count > 3:
            accur = accur * 100
            accur = round(float(accur), 2)
            usermap_info["accuracy"] = accur
        elif type(accur) == float:
            accur = round(float(accur))
            usermap_info["accuracy"] = accur
        info = beatmap_data['artist'] + ' - ' + beatmap_data['title'] + \
                   '\n' + '[' + beatmap_data['version'] + ']' + '\n' + ' Map Creator: ' + beatmap_data['creator'] + \
                   '\n' + 'Player: ' + user_id + \
                   '\n' + 'Очки: ' + usermap_info['score'] + \
                   '\n' + 'Аккуратность: ' + str(usermap_info["accuracy"]) + '%' + \
                   '\n' + 'Комбо: ' + usermap_info['maxcombo'] + '/' + beatmap_data['max_combo'] + \
                   '\n' + usermap_info['count300'] + '/' + usermap_info['count100'] + '/' + usermap_info['count50'] + \
                                             '\n' + 'Миссы: ' + usermap_info['countmiss'] + \
                   '\n' + 'Ранк: ' + usermap_info['rank'] + \
                   '\n' + 'Моды: ' + self.mods(int(usermap_info['enabled_mods'])) + \
                   '\n' + 'Ссылка: https://osu.ppy.sh/b/' + beatmap_data['beatmap_id'] + \
                   '\n' + 'AR ' + beatmap_data['diff_approach'] + ' | OD ' + beatmap_data['diff_overall'] + \
                   ' | HP ' + beatmap_data['diff_overall'] + ' | CS ' + beatmap_data["diff_size"] + ' | ' + str(
                "%.2f" % float(beatmap_data['difficultyrating'])) + '*'
        return info

    def score_beatmap_top(self, usermap_info: dict, beatmap_data: dict, user_id: str):
        info = ''
        for item in enumerate(list(self.top_play(user_id))):
            for beatmaps in enumerate(list(self.top_play_map(user_id))):
                accur = int(usermap_info['count50']) * 50 + int(usermap_info['count100']) * 100 + int(
                    usermap_info['count300']) * 300
                accur1 = int(usermap_info['count50']) + int(usermap_info['count100']) + int(usermap_info['count300']) + int(
                    usermap_info['countmiss'])
                accur2 = 300 * accur1
                accur = accur / accur2
                count = len(str(accur))
                usermap_info["accuracy"] = accur
                if count > 3:
                    accur = accur * 100
                    accur = round(float(accur), 2)
                    usermap_info["accuracy"] = accur
                elif type(accur) == float:
                    accur = round(float(accur))
                    usermap_info["accuracy"] = accur
                info = info + beatmap_data['artist'] + ' - ' + beatmap_data['title'] + \
                       '\n' + '[' + beatmap_data['version'] + ']' + ' Создатель: ' + beatmap_data['creator'] + \
                       '\n' + 'Аккуратность: ' + str(usermap_info["accuracy"]) + '%' + \
                       '\n' + str(
                        "%.2f" % float(beatmap_data['difficultyrating'])) + '*, ' + 'Комбо: ' + usermap_info['maxcombo'] + '/' + beatmap_data['max_combo'] + \
                       '\n' + '300: ' + usermap_info['count300'] + '. 100: ' + usermap_info['count100'] + '. 50: ' + \
                       usermap_info['count50'] + '.' \
                                                 '\n' + 'Миссы: ' + usermap_info['countmiss'] + \
                       '\n' + 'Ранк: ' + usermap_info['rank'] + \
                       '\n' + 'PP: ' + str("%.2f" % float(usermap_info['pp'])) + '\n'
        return info


osu_session = osu_api(get_osu_token(), 0)

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        # print('Время: ' + str(datetime.strftime(datetime.now(), "%H:%M:%S")))
        # print('Текст человека: ' + str(event.text))
        # print(event.attachments)
        # try:
        # print(event.user_id)
        # except:
        # print(event.peer_id)
        response = event.text

        for item in commands:
            try:
                if item['name'] == event.text:
                    # from chat
                    send_message(vk_session, 'peer_id', event.peer_id, item['value'])
            except:
                pass

        if response.find('https') != -1:
            if response.split(' ') == 1:
                if response.find('osu.ppy.sh/b/') != -1:
                    url_arg = response.split('osu.ppy.sh/b/')[1:]
                    beatmap_id = str().join(arg for arg in url_arg).split('&')[0]
                    send_message(vk_session, 'peer_id', event.peer_id,
                                 osu_session.beatmap_get_send(osu_session.get_beatmap_by_id(beatmap_id)),
                                 attachment=osu_session.get_bg(osu_session.get_beatmap_by_id(mapid)))

        if event.text.lower() == "!stone":
            send_message(vk_session, 'peer_id', event.peer_id,
                         '🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿')

        if event.text.lower() == "!botoff":
            send_message(vk_session, 'peer_id', event.peer_id, "Выключаюсь...")
            break

        spaced_words = str(response).split(' ')
        if spaced_words[0] == "!profile" and len(spaced_words) == 2:
            send_message(vk_session, 'peer_id', event.peer_id,
                         osu_session.osu_profile_tostring(osu_session.get_profile_by_id(str(spaced_words[1]))))

        if spaced_words[0] == "!score" and len(spaced_words) == 3:
            url_arg = response.split('osu.ppy.sh/b/')[1:]
            mapid = str().join(arg for arg in url_arg).split('&')[0]
            send_message_nolinks(vk_session, 'peer_id', event.peer_id,
                         osu_session.score_beatmap_get(osu_session.get_score_by_id(spaced_words[1], mapid),
                                                       osu_session.get_beatmap_by_id(mapid), spaced_words[1]),
                         attachment=osu_session.get_bg(osu_session.get_beatmap_by_id(mapid)))

        if spaced_words[0] == "!recent" and len(spaced_words) == 2:
            send_message_nolinks(vk_session, 'peer_id', event.peer_id,
                         osu_session.score_beatmap_recent(osu_session.get_recent_by_id(spaced_words[1]), osu_session.get_id_by_recent(spaced_words[1]), spaced_words[1]),
                         attachment=osu_session.get_bg(osu_session.get_id_by_recent(spaced_words[1])))

        if spaced_words[0] == "!top" and len(spaced_words) == 2:
            send_message_nolinks(vk_session, 'peer_id', event.peer_id, osu_session.top_play(spaced_words[1])[0:500])
            send_message_nolinks(vk_session, 'peer_id', event.peer_id, osu_session.top_play(spaced_words[1])[500:1000])
            send_message_nolinks(vk_session, 'peer_id', event.peer_id, osu_session.top_play(spaced_words[1])[1000:1500])
            send_message_nolinks(vk_session, 'peer_id', event.peer_id, osu_session.top_play(spaced_words[1])[1500:2000])

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
            send_message(vk_session, 'peer_id', event.peer_id, str(commands))

        if event.text.lower() == "!шашлык":
            vk_session.method('messages.send', {'peer_id': event.peer_id,
                                                'message': 'Шашлычок ту-ту-ту-ду-ду и лучок ту-ту-ту-ду-ду\nНа природе ту-ту-ту-ду-ду, при погоде ту-ту-ту-ду-ду\nИз свинИны ту-ту-ту-ду-ду, из баранИны ту-ту-ту-ду-ду\nСлюнки текут ту-ту-ту-ду-ду, а гости ждут.',
                                                'random_id': 0,
                                                "attachment": 'audio161959141_456241535'})
        if event.text.lower() == "прикалюха":
            send_message(vk_session, 'peer_id', event.peer_id, attachment='video161959141_456240830')
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
        if spaced_words[0] == "!p" and len(spaced_words) == 2:
            try:
                send_message(vk_session, 'peer_id', event.peer_id,
                             attachment='photo161959141' + '_' + str(spaced_words[1]))
            except:
                send_message(vk_session, 'peer_id', event.peer_id, attachment='video161959141_456240839')

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
        if event.text == '!pic':
            try:
                if event.attachments['attach1_type'] == 'photo':
                    id_photo = event.attachments['attach1']
                    # print(id_photo)
                    send_message(vk_session, 'peer_id', event.peer_id, attachment='photo' + id_photo)
            except:
                send_message(vk_session, 'peer_id', event.peer_id, attachment='video161959141_456240839')
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
            if is_permitted(int(event.extra_values['from']), 5):
                if spaced_words[1] == spaced_words[2]:
                    send_message(vk_session, 'chat_id', event.chat_id, "Нельзя добавить эхо-комманду")
                elif spaced_words[1] in list(i['name'] for i in commands):
                    send_message(vk_session, 'chat_id',
                                 event.chat_id, "Нельзя добавить существуюую комманду")
                else:
                    command_worker.insert(10, spaced_words[1], ' '.join(spaced_words[2:]))
                    commands.insert(0, {
                        'access_level': 10,
                        'name': spaced_words[1],
                        'value': ' '.join(spaced_words[2:])})

                    send_message(vk_session, 'chat_id', event.chat_id,
                                 "Комманда " + spaced_words[1] + " добавлена!")
            else:
                send_message(vk_session, 'chat_id', event.chat_id, "Permission denied, required level to access: 5")

        if spaced_words[0] == '!delcom' and len(spaced_words) == 2:
            if is_permitted(event.extra_values['from'], 5):
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
