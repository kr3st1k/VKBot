import asyncio
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
import threading
from threading import Thread
from Database.osuDbWorker import OsuDbWorker
from Database.CommandDbWorker import CommandDbWorker
from StartupLoader.StartupLoader import StartupLoader
from Database.UserDbWorker import UserDbWorker
from subprocess import Popen, PIPE
import subprocess
import enum
from bancho import bancho_session, BanchoApi
from gatari import gatari_session, GatariApi
from VkBot import VkBot, VkBan, VkTel
import math
import sched, time
from google_images_search import GoogleImagesSearch
# Предзагрузка конфигураций
config_loader = StartupLoader('config.JSON')

admin_id_int = config_loader.get_admin_id()

# Создание БД воркеров
user_worker = UserDbWorker()
command_worker = CommandDbWorker()
osu_worker = OsuDbWorker()

# Загрузка листов из БД
commands = command_worker.select_all()
users = user_worker.select_all()
nicks = osu_worker.select_all()
names = command_worker.select_all_names()

vk_session = vk_api.VkApi(token=config_loader.get_vk_token())
session_api = vk_session.get_api()
longpoll = VkLongPoll(vk_session)
teleg = VkTel(config_loader.get_tel_api())
bot = VkBot(vk_session, session_api, admin_id_int)
ban = VkBan(vk_session, session_api)
dict_of_levels = {
    1: 1000,
    2: 2700,
    3: 7000,
    4: 10000,
    5: 15000,
    6: 20000,
    7: 30000,
    8: float('inf'),
    9: float('inf'),
    10: float('inf')
}
def is_permitted(vk_id: int, required_level: int):
    for user in users:
        if user['vk_id'] == int(vk_id):
            return user['access_level'] >= required_level
    return False


def distribution_func(value: int):
    if value < 50:
        return 5 * math.sin(2 * math.pi * value - math.pi / 2) + 6.2
    else:
        return 6 / value


async def longpool_handle():
    user_spam_coeffs = dict(zip([user['vk_id'] for user in users], [1] * len(users)))
    counter_of_messages = 0

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            # print('Время: ' + str(datetime.strftime(datetime.now(), "%H:%M:%S")))
            # print('Текст человека: ' + str(event.text))
            print(event.message_id)
            print(event.attachments)
            if event.from_chat:
                if event.chat_id == 1:
                    if event.user_id != 595719899:
                        if event.attachments == {}:
                            oo = bot.name_last_user(event.user_id)
                            for i in oo:
                                namen = i['first_name']
                                lastn = i['last_name']
                            teleg.send_from_vk(event.text, 'VK\n' + str(namen) + ' ' + str(lastn))
            # try:
            # print(event.user_id)
            #  except:
            # print(event.peer_id)
            counter_of_messages += 1
            if counter_of_messages >= 10:
                for pgr in users:
                    user_worker.update(pgr['vk_id'], pgr['association'], pgr['access_level'], pgr['lvl_exp'])
                user_spam_coeffs = dict(zip([user['vk_id'] for user in users], [1] * len(users)))
                counter_of_messages = 0
            response = event.text
            current_user = {'access_level': 0,
                            'vk_id': None,
                            'association': "Unknown",
                            'lvl_exp': 0}
            if event.from_chat:
                if int(event.extra_values['from']) != 595719899:
                    for pgr in users:
                        if pgr['vk_id'] == int(event.extra_values['from']):
                            current_user = pgr
                            if pgr['access_level'] <= 10:
                                coef = 0.33  # coef of accseleration the level
                                pgr['lvl_exp'] += distribution_func(len(event.text.split(' '))) / coef * \
                                                   user_spam_coeffs[pgr['vk_id']]
                                if user_spam_coeffs[pgr['vk_id']] > 0.7:
                                    user_spam_coeffs[pgr['vk_id']] -= 0.03
                                else:
                                    user_spam_coeffs[pgr['vk_id']] *= 0.57
                                if pgr['access_level'] < 7:
                                    if pgr['lvl_exp'] >= dict_of_levels[pgr['access_level']]:
                                        # level up
                                        pgr['access_level'] += 1
                                        bot.send_wo_mention('chat_id', event.chat_id, "@id" + event.extra_values['from']
                                                     +'(' + pgr['association']+") Апнул " + str(pgr['access_level'])
                                                            + 'lvl!', attachment='video-167123504_456245219')
                                        user_worker.update(pgr['vk_id'],
                                                           pgr['association'],
                                                           pgr['access_level'],
                                                           pgr['lvl_exp'])

            for item in commands:
                try:
                    if item['name'] == event.text.lower():
                        if item['attachment'] != ' ':
                            bot.send_message('peer_id', event.peer_id, item['value'], attachment=item['attachment'])
                        else:
                            bot.send_message('peer_id', event.peer_id, item['value'])
                except:
                    pass

            if ''.join(list(' '.join(response.split()[:1]))[0:21]) == 'https://osu.ppy.sh/b/':
                try:
                    url_arg = response.split('osu.ppy.sh/b/')[1:]
                    beatmap_id = str().join(arg for arg in url_arg).split('&')[0]
                    bot.send_message('peer_id', event.peer_id,
                                     bancho_session.beatmap_get_send(bancho_session.get_beatmap_by_id(beatmap_id)),
                                     attachment=bancho_session.get_bg(bancho_session.get_beatmap_by_id(beatmap_id)))
                except:
                    print('no.')
            if ''.join(list(' '.join(response.split()[:1]))[0:30]) == 'https://osu.ppy.sh/beatmapsets':
                map = response.split('/')
                url_arg = map[5]
                beatmap_id = str().join(arg for arg in url_arg).split('&')[0]
                bot.send_message('peer_id', event.peer_id,
                                     bancho_session.beatmap_get_send(bancho_session.get_beatmap_by_id(beatmap_id)),
                                     attachment=bancho_session.get_bg(bancho_session.get_beatmap_by_id(beatmap_id)))
            if event.text == "!stone":
                bot.send_message('peer_id', event.peer_id,
                             '🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿'+\
                             '🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿')

            spaced_words = str(response).split(' ')
            if spaced_words[0] == '?o': #bancho
                if spaced_words[1] == 'n':
                    if int(event.user_id) not in list(i['vk_id'] for i in nicks):
                        osu_worker.insert(int(event.user_id),  ' '.join(spaced_words[2:]))
                        nicks.insert(0, {
                            'vk_id': int(event.user_id),
                            'nickname':  ' '.join(spaced_words[2:]),
                            'mode': 0,
                            'color': None})
                        bot.send_message('peer_id', event.peer_id, "вы зарегестировались! Ваш ник: "
                                         +  ' '.join(spaced_words[2:]))
                    elif int(event.user_id) in list(i['vk_id'] for i in nicks):
                        for rgp in nicks:
                            if rgp['vk_id'] == int(event.user_id):
                                osu_worker.update(rgp['vk_id'], ' '.join(spaced_words[2:]), rgp['color'], rgp['mode'], rgp['bg'],
                                                  rgp['percent'])
                                index = list(i['vk_id'] for i in nicks).index(event.user_id)
                                nicks[index] = {
                                    'vk_id': event.user_id,
                                    'nickname': ' '.join(spaced_words[2:]),
                                    'color': rgp['color'],
                                    'mode': rgp['mode'],
                                    'bg': rgp['bg'],
                                    'percent': rgp['percent']}
                                bot.send_message('peer_id', event.peer_id,
                                                 "Поздравляю вы теперь: " + ' '.join(spaced_words[2:]))
                if spaced_words[1] == 'u':
                    if len(spaced_words) == 2:
                        if int(event.user_id) in list(i['vk_id'] for i in nicks):
                            for rgp in nicks:
                                if rgp['vk_id'] == int(event.user_id):
                                    bot.send_message_nolinks('peer_id', event.peer_id,
                                                                         bancho_session.osu_profile_tostring(bancho_session
                                                                                                          .get_profile_by_id(rgp['nickname'], rgp['mode'])))
                        else:
                            bot.send_message('peer_id', event.peer_id, 'Вы не зарегистрированы!')
                    if len(spaced_words) >= 3:
                        if int(event.user_id) in list(i['vk_id'] for i in nicks):
                            for rgp in nicks:
                                if rgp['vk_id'] == int(event.user_id):
                                    bot.send_message_nolinks('peer_id', event.peer_id, bancho_session.osu_profile_tostring(
                                            bancho_session.get_profile_by_id(str(' '.join(spaced_words[2:])), rgp['mode'])))
                        else:
                            bot.send_message_nolinks('peer_id', event.peer_id, bancho_session.osu_profile_tostring(
                                bancho_session.get_profile_by_id(str(' '.join(spaced_words[2:])), 0)))
                if spaced_words[1] == 'pic':
                    if len(spaced_words) == 2:
                        if int(event.user_id) in list(i['vk_id'] for i in nicks):
                            for rgp in nicks:
                                if rgp['vk_id'] == int(event.user_id):
                                    bot.send_message('peer_id', event.peer_id,
                                                     attachment=bancho_session.osu_profile_pic(bancho_session
                                                                                            .get_profile_by_id(rgp['nickname'], rgp['mode']),
                                                                                            1, rgp['percent'], rgp['color'],
                                                                                            rgp['bg']))
                        else:
                                bot.send_message('peer_id', event.peer_id, 'Вы не зарегистрированы!')
                    if len(spaced_words) >= 3:
                        if int(event.user_id) in list(i['vk_id'] for i in nicks):
                            for rgp in nicks:
                                if rgp['vk_id'] == int(event.user_id):
                                    bot.send_message('peer_id', event.peer_id,
                                                     attachment=bancho_session.osu_profile_pic(
                                                         bancho_session.get_profile_by_id(str(' '.join(spaced_words[2:])),
                                                                                          rgp['mode']), 1, 100))
                        else:
                            bot.send_message('peer_id', event.peer_id, attachment=bancho_session.osu_profile_pic(
                                    bancho_session.get_profile_by_id(str(' '.join(spaced_words[2:])), 0), 1, 100))
                if spaced_words[1] == 'graffiti':
                    if len(spaced_words) == 2:
                        if int(event.user_id) in list(i['vk_id'] for i in nicks):
                            for rgp in nicks:
                                if rgp['vk_id'] == int(event.user_id):
                                    bot.send_message('peer_id', event.peer_id,
                                                     attachment=bancho_session.osu_profile_pic(bancho_session
                                                                                               .get_profile_by_id(
                                                         rgp['nickname'], rgp['mode']),
                                                                                               2, rgp['percent'],
                                                                                               rgp['color'],
                                                                                               rgp['bg']))
                        else:
                            bot.send_message('peer_id', event.peer_id, 'Вы не зарегистрированы!')
                    if len(spaced_words) >= 3:
                        if int(event.user_id) in list(i['vk_id'] for i in nicks):
                            for rgp in nicks:
                                if rgp['vk_id'] == int(event.user_id):
                                    bot.send_message('peer_id', event.peer_id,
                                                     attachment=bancho_session.osu_profile_pic(
                                                         bancho_session.get_profile_by_id(str(' '.join(spaced_words[2:])),
                                                                                          rgp['mode']), 2, 100))
                        else:
                            bot.send_message('peer_id', event.peer_id, attachment=bancho_session.osu_profile_pic(
                                bancho_session.get_profile_by_id(str(' '.join(spaced_words[2:])), 0), 2, 100))
                if spaced_words[1] == "s":
                    if 'osu.ppy.sh/b/' in response:
                        url_arg = response.split('osu.ppy.sh/b/')[1:]
                    if 'osu.ppy.sh/beatmapsets/' in response:
                        map = response.split('/')
                        url_arg = map[5]
                    mapid = str().join(arg for arg in url_arg).split('&')[0]
                    if len(spaced_words) == 3:
                        if int(event.user_id) in list(i['vk_id'] for i in nicks):
                            for rgp in nicks:
                                if rgp['vk_id'] == int(event.user_id):
                                    try:
                                        bot.send_message_nolinks('peer_id', event.peer_id,
                                                         bancho_session.score_beatmap_get(bancho_session.get_score_by_id(rgp['nickname'], mapid),
                                                                                       bancho_session.get_beatmap_by_id(mapid), rgp['nickname']),
                                                         attachment=bancho_session.get_bg(bancho_session.get_beatmap_by_id(mapid)))
                                    except Exception as ex:
                                        logging.info(ex)
                                        bot.send_message('peer_id', event.peer_id,
                                                         'У вас нет скора на этой мапе или неправильный ник')
                        else:
                            bot.send_message('peer_id', event.peer_id, 'Вы не зарегистрированы!')
                    if len(spaced_words) == 4:
                        try:
                            bot.send_message_nolinks('peer_id', event.peer_id,
                                                 bancho_session.score_beatmap_get(bancho_session.get_score_by_id(spaced_words[2],
                                                                                                           mapid),
                                                                               bancho_session.get_beatmap_by_id(mapid),
                                                                               spaced_words[2]),
                                                 attachment=bancho_session.get_bg(bancho_session.get_beatmap_by_id(mapid)))
                        except:
                            bot.send_message('peer_id', event.peer_id,
                                         'У вас нет скора на этой мапе или неправильный ник')
                if spaced_words[1] == "r":
                    if len(spaced_words) == 2:
                        if int(event.user_id) in list(i['vk_id'] for i in nicks):
                            for rgp in nicks:
                                if rgp['vk_id'] == int(event.user_id):
                                    bot.send_message_nolinks('peer_id', event.peer_id,
                                                                 bancho_session.score_beatmap_get(bancho_session.get_recent_by_id(rgp['nickname']),
                                                                                               bancho_session.get_id_by_recent(rgp['nickname']),
                                                                                               rgp['nickname']),
                                                                 attachment=bancho_session.get_bg(bancho_session.get_id_by_recent(rgp['nickname'])))
                        else:
                            bot.send_message('peer_id', event.peer_id, 'Вы не зарегистрированы!')
                    if len(spaced_words) >= 3:
                        try:
                            bot.send_message_nolinks('peer_id', event.peer_id,
                                bancho_session.score_beatmap_get(bancho_session.get_recent_by_id(str(' '.join(spaced_words[2:]))),
                                                                bancho_session.get_id_by_recent(str(' '.join(spaced_words[2:]))),
                                                                spaced_words[2]),
                                attachment=bancho_session.get_bg(bancho_session.get_id_by_recent(str(' '.join(spaced_words[2:])))))
                        except:
                            bot.send_message('peer_id', event.peer_id, 'Нет недавних игр или неправильно ник!')
                if spaced_words[1] == "t":
                    if len(spaced_words) == 2:
                        if int(event.user_id) in list(i['vk_id'] for i in nicks):
                            for rgp in nicks:
                                if rgp['vk_id'] == int(event.user_id):
                                    bot.send_message_nolinks('peer_id', event.peer_id, bancho_session.score_beatmap_top(rgp['nickname'], bancho_session.top_play(rgp['nickname'])))
                        else:
                            bot.send_message('peer_id', event.peer_id, 'Вы не зарегистрированы!')
                    if len(spaced_words) == 3:
                        try:
                            bot.send_message_nolinks('peer_id', event.peer_id,
                                                 bancho_session.score_beatmap_top(spaced_words[2], bancho_session.top_play(spaced_words[2])))
                        except:
                            bot.send_message('peer_id', event.peer_id, 'Неправильно ник!')
                if spaced_words[1] == 'm':
                    if int(event.user_id) in list(i['vk_id'] for i in nicks):
                        for rgp in nicks:
                            if rgp['vk_id'] == int(event.user_id):
                                osu_worker.update(rgp['vk_id'], rgp['nickname'], rgp['color'], int(spaced_words[2]),
                                                  rgp['bg'], rgp['percent'], rgp['nickname_gatari'])
                                index = list(i['vk_id'] for i in nicks).index(event.user_id)
                                nicks[index] = {
                                    'vk_id': event.user_id,
                                    'nickname': rgp['nickname'],
                                    'color': rgp['color'],
                                    'mode': spaced_words[2],
                                    'bg': rgp['bg'],
                                    'percent': rgp['percent'],
                                    'nickname_gatari': rgp['nickname_gatari']}
                                if int(spaced_words[2]) == 0:
                                    spaced_words[2] = 'Standard'
                                elif int(spaced_words[2]) == 1:
                                    spaced_words[2] = 'Taiko'
                                elif int(spaced_words[2]) == 2:
                                    spaced_words[2] = 'CtB'
                                elif int(spaced_words[2]) == 3:
                                    spaced_words[2] = 'Mania'
                                bot.send_message('peer_id', event.peer_id,
                                                 "Поздравляю установлен режим " + str(spaced_words[2]))
                    else:
                        bot.send_message('peer_id', event.peer_id, "Вы не зарегистрированы!")
            if spaced_words[0] == '?g': #gatari
                if spaced_words[1] == 'n':
                    if int(event.user_id) not in list(i['vk_id'] for i in nicks):
                        osu_worker.insert(int(event.user_id), None)
                        nicks.insert(0, {
                            'vk_id': int(event.user_id),
                            'nickname': None,
                            'mode': 0,
                            'color': None})
                        bot.send_message('peer_id', event.peer_id, "вы зарегестировались! Ваш ник: "
                                         + str(spaced_words[2]))
                    elif int(event.user_id) in list(i['vk_id'] for i in nicks):
                        for rgp in nicks:
                            if rgp['vk_id'] == int(event.user_id):
                                osu_worker.update(rgp['vk_id'], rgp['nickname'], rgp['color'], rgp['mode'], rgp['bg'],
                                                  rgp['percent'], str(' '.join(spaced_words[2:])).replace(' ', '%20'))
                                index = list(i['vk_id'] for i in nicks).index(event.user_id)
                                nicks[index] = {
                                    'vk_id': event.user_id,
                                    'nickname': rgp['nickname'],
                                    'color': rgp['color'],
                                    'mode': rgp['mode'],
                                    'bg': rgp['bg'],
                                    'percent': rgp['percent'],
                                    'nickname_gatari': str(' '.join(spaced_words[2:])).replace(' ', '%20')}
                                bot.send_message('peer_id', event.peer_id,
                                                 "Поздравляю вы теперь: " + ' '.join(spaced_words[2:]))
                if spaced_words[1] == 'u':
                    if len(spaced_words) == 2:
                        if int(event.user_id) in list(i['vk_id'] for i in nicks):
                            for rgp in nicks:
                                if rgp['vk_id'] == int(event.user_id):
                                    bot.send_message_nolinks('peer_id', event.peer_id,
                                                             gatari_session.osu_profile_tostring(gatari_session
                                                                                                 .get_basic_info(
                                                                 rgp['nickname_gatari']), gatari_session.get_stats(
                                                                 rgp['nickname_gatari'], str(rgp['mode']))))
                        else:
                            bot.send_message('peer_id', event.peer_id, 'Вы не зарегистрированы!')
                    if len(spaced_words) >= 3:
                        if int(event.user_id) in list(i['vk_id'] for i in nicks):
                            for rgp in nicks:
                                if rgp['vk_id'] == int(event.user_id):
                                    bot.send_message_nolinks('peer_id', event.peer_id,
                                                             gatari_session.osu_profile_tostring(
                                                                 gatari_session
                                                                     .get_basic_info(
                                                                     str(' '.join(spaced_words[2:])).replace(' ',
                                                                                                             '%20')),
                                                                 gatari_session.get_stats(
                                                                     str(' '.join(spaced_words[2:])).replace(' ',
                                                                                                             '%20'),
                                                                     str(rgp['mode']))))
                        else:
                            bot.send_message_nolinks('peer_id', event.peer_id, gatari_session.osu_profile_tostring(
                                gatari_session
                                    .get_basic_info(str(' '.join(spaced_words[2:])).replace(' ', '%20')),
                                gatari_session.get_stats(str(' '.join(spaced_words[2:])).replace(' ', '%20'), str(0))))
                if spaced_words[1] == 'pic':
                    if len(spaced_words) == 2:
                        if int(event.user_id) in list(i['vk_id'] for i in nicks):
                            for rgp in nicks:
                                if rgp['vk_id'] == int(event.user_id):
                                    bot.send_message('peer_id', event.peer_id,
                                                     attachment=gatari_session.osu_profile_pic(gatari_session
                                                                                                 .get_basic_info(
                                                                 rgp['nickname_gatari']), gatari_session.get_stats(
                                                                 rgp['nickname_gatari'], str(rgp['mode'])),
                                                                                            1, rgp['percent'], rgp['color'],
                                                                                            rgp['bg']))
                        else:
                                bot.send_message('peer_id', event.peer_id, 'Вы не зарегистрированы!')
                    if len(spaced_words) >= 3:
                        if int(event.user_id) in list(i['vk_id'] for i in nicks):
                            for rgp in nicks:
                                if rgp['vk_id'] == int(event.user_id):
                                    bot.send_message('peer_id', event.peer_id,
                                                     attachment=gatari_session.osu_profile_pic(
                                                         gatari_session.get_basic_info(str(' '.join(spaced_words[2:])).replace(' ', '%20')), gatari_session.get_stats(
                                                                 str(' '.join(spaced_words[2:])).replace(' ', '%20'), str(rgp['mode'])),1, 100))
                        else:
                            bot.send_message('peer_id', event.peer_id, attachment=gatari_session.osu_profile_pic(
                                gatari_session.get_basic_info(str(' '.join(spaced_words[2:])).replace(' ', '%20')), gatari_session.get_stats(
                                                                 str(' '.join(spaced_words[2:])).replace(' ', '%20'), str(0)), 1, 100))
                if spaced_words[1] == 'graffiti':
                    if len(spaced_words) == 2:
                        if int(event.user_id) in list(i['vk_id'] for i in nicks):
                            for rgp in nicks:
                                if rgp['vk_id'] == int(event.user_id):
                                    bot.send_message('peer_id', event.peer_id,
                                                     attachment=gatari_session.osu_profile_pic(gatari_session
                                                         .get_basic_info(
                                                         rgp['nickname_gatari']), gatari_session.get_stats(
                                                         rgp['nickname_gatari'], str(rgp['mode'])),
                                                         2, rgp['percent'], rgp['color'],
                                                         rgp['bg']))
                        else:
                            bot.send_message('peer_id', event.peer_id, 'Вы не зарегистрированы!')
                    if len(spaced_words) >= 3:
                        if int(event.user_id) in list(i['vk_id'] for i in nicks):
                            for rgp in nicks:
                                if rgp['vk_id'] == int(event.user_id):
                                    bot.send_message('peer_id', event.peer_id,
                                                     attachment=gatari_session.osu_profile_pic(
                                                         gatari_session.get_basic_info(
                                                             str(' '.join(spaced_words[2:])).replace(' ', '%20')),
                                                         gatari_session.get_stats(
                                                             str(' '.join(spaced_words[2:])).replace(' ', '%20'),
                                                             str(rgp['mode'])), 2, 100))
                        else:
                            bot.send_message('peer_id', event.peer_id, attachment=gatari_session.osu_profile_pic(
                                gatari_session.get_basic_info(str(' '.join(spaced_words[2:])).replace(' ', '%20')),
                                gatari_session.get_stats(
                                    str(' '.join(spaced_words[2:])).replace(' ', '%20'), str(0)), 2, 100))
                if spaced_words[1] == 'm':
                    if int(event.user_id) in list(i['vk_id'] for i in nicks):
                        for rgp in nicks:
                            if rgp['vk_id'] == int(event.user_id):
                                osu_worker.update(rgp['vk_id'], rgp['nickname'], rgp['color'], int(spaced_words[2]),
                                                  rgp['bg'], rgp['percent'], rgp['nickname_gatari'])
                                index = list(i['vk_id'] for i in nicks).index(event.user_id)
                                nicks[index] = {
                                    'vk_id': event.user_id,
                                    'nickname': rgp['nickname'],
                                    'color': rgp['color'],
                                    'mode': spaced_words[2],
                                    'bg': rgp['bg'],
                                    'percent': rgp['percent'],
                                    'nickname_gatari': rgp['nickname_gatari']}
                                if int(spaced_words[2]) == 0:
                                    spaced_words[2] = 'Standard'
                                elif int(spaced_words[2]) == 1:
                                    spaced_words[2] = 'Taiko'
                                elif int(spaced_words[2]) == 2:
                                    spaced_words[2] = 'CtB'
                                elif int(spaced_words[2]) == 3:
                                    spaced_words[2] = 'Mania'
                                bot.send_message('peer_id', event.peer_id,
                                                 "Поздравляю установлен режим " + str(spaced_words[2]))
                    else:
                        bot.send_message('peer_id', event.peer_id, "Вы не зарегистрированы!")
            if spaced_words[0] == '!graffiti' and len(spaced_words) == 2:
                bot.send_message('peer_id', event.peer_id, attachment=bot.send_graphiti(spaced_words[1]))

            if event.text == "!лоличан":
                code = [-127518015, -101072212]
                attachment = bot.get_pictures(random.choice(code))
                bot.send_message('peer_id', event.peer_id, 'Держи девочку!', attachment)
            if event.text == "!murnelis":
                attachment = bot.get_pictures(-182090873)
                bot.send_message('peer_id', event.peer_id, 'Держи мем!', attachment)
            if event.text == "!ll":
                attachment = bot.get_pictures(-119420102)
                bot.send_message('peer_id', event.peer_id, 'Держи LoveLive!', attachment)
            if event.text == "!rx4d":
                hug = [456241533, 456241532, 456241531, 456241530, 456241529, 456241528, 456241527, 456241526,
                       456241525, 456241524, 456241523, 456241522, 456241521, 456241520, 456241519, 456241518,
                       456241517, 456241516, 456241515, 456241514, 456241513, 456241512, 456241511]
                bot.send_message('peer_id', event.peer_id,
                             attachment='audio' + str(161959141) + '_' + str(random.choice(hug)))


            if spaced_words[0] == '!погода':
                try:
                    if len(spaced_words) >= 2:
                        if spaced_words[1] != 'завтра':
                            if spaced_words[1] != 'сегодня':
                                res = requests.get("http://api.openweathermap.org/data/2.5/weather",
                                                   params={'q': str(' ').join(i for i in spaced_words[1:]),
                                                           'units': 'metric', 'lang': 'ru',
                                                           'APPID': '81d59d3e4bcd5bd5b69f6f95250213ee'})
                                data = res.json()
                                bot.send_message('peer_id', event.peer_id, data['name'] + ' | ' + data['sys']['country']
                                                 + '\n🌍Погода: ' + str(data['weather'][0]['description']) + '\n🚩Ветер: '
                                                 + str(data['wind']['speed']) + 'm/s '
                                                 + str(data['wind']['deg']) + '°' + '\n🌡Температура: '
                                                 + str(data['main']['temp']) + '°C' + '\n✌🏻Ощущается как: '
                                                 + str(data['main']['feels_like']) + '°C' + '\n\n☁Облачность: '
                                                 + str(data['clouds']['all']) + '%\n💧Влажнось: '
                                                 + str(data['main']['humidity']) + '%\n📊Давление: '
                                                 + str(data['main']['pressure']))
                    if len(spaced_words) >= 3:
                        if spaced_words[1] == 'завтра':
                            res = requests.get("https://api.openweathermap.org/data/2.5/forecast/daily",
                                               params={'q': str(' ').join(i for i in spaced_words[2:]), 'units': 'metric',
                                                       'lang': 'ru',
                                                       'APPID': '81d59d3e4bcd5bd5b69f6f95250213ee', 'cnt': 2})
                            data = res.json()
                            bot.send_message('peer_id', event.peer_id,
                                             data['city']['name'] + ' | ' + data['city']['country'] + '\n🌍Погода: '
                                             + str(data['list'][1]['weather'][0]['description'])
                                             + '\n🌄Температура днем: '
                                             + str(data['list'][1]['temp']['day']) + '°C' + '\n🌃Температура ночью: '
                                             + str(data['list'][1]['temp']['night']) + '°C' + '\n\n☁Облачность: '
                                             + str(data['list'][1]['clouds']) + '%\n💧Влажнось: '
                                             + str(data['list'][1]['humidity']) + '%\n📊Давление: '
                                             + str(data['list'][1]['pressure']))
                        if spaced_words[1] == 'сегодня':
                            res = requests.get("https://api.openweathermap.org/data/2.5/forecast/daily",
                                               params={'q': str(' ').join(i for i in spaced_words[2:]), 'units': 'metric',
                                                       'lang': 'ru',
                                                       'APPID': '81d59d3e4bcd5bd5b69f6f95250213ee', 'cnt': 2})
                            data = res.json()
                            bot.send_message('peer_id', event.peer_id,
                                             data['city']['name'] + ' | ' + data['city']['country'] + '\n🌍Погода: '
                                             + str(data['list'][0]['weather'][0]['description'])
                                             + '\n🌄Температура днем: '
                                             + str(data['list'][0]['temp']['day']) + '°C' + '\n🌃Температура ночью: '
                                             + str(data['list'][0]['temp']['night']) + '°C' + '\n\n☁Облачность: '
                                             + str(data['list'][0]['clouds']) + '%\n💧Влажнось: '
                                             + str(data['list'][0]['humidity']) + '%\n📊Давление: '
                                             + str(data['list'][0]['pressure']))
                except: bot.send_message('peer_id', event.peer_id, 'Город не найден!')
            if event.text.lower() == "!com":
                bot.send_message('peer_id', event.peer_id, str(names))

            if spaced_words[0] == '!google':
                def my_progressbar(url):
                    print(url)

                gis = GoogleImagesSearch('AIzaSyA_VKOXdLZ3M9bkzTwpgC_M3H6CyUEKfxM', '005710364809358714397:ftptwfvq0s3',
                                         progressbar_fn=my_progressbar)
                s = random.randint(1, 10)
                search_params = {
                    'q': spaced_words[1:],
                    'num': s,
                    'fileType': 'png'}
                gis.search(search_params=search_params)
                for image in gis.results():
                    photo = image.url
                bot.send_message('peer_id', event.peer_id, attachment=bot.send_photo(photo))

            if spaced_words[0] == '!roll':
                if len(spaced_words) == 2:
                    bot.send_message('peer_id', event.peer_id, random.randint(1, int(spaced_words[1])))
                if len(spaced_words) == 1:
                    bot.send_message('peer_id', event.peer_id, random.randint(1, 100))
                    #TODO in DB
            if spaced_words[0] == "!кто" and len(spaced_words) == 2:
                if event.from_chat:
                    if is_permitted(int(event.extra_values['from']), 5):
                        vaal = random.choice(
                            (vk_session.method('messages.getChat', {'chat_id': event.chat_id}))['users'])
                        bot.send_wo_mention('peer_id', event.peer_id,
                                        "Я думаю, что " + str(spaced_words[1]) + " @id" + str(vaal) + "(он!!!)")
                    else:
                        bot.send_message('chat_id', event.chat_id,
                                     "Permission denied, required level to access: 5")
                else:
                    bot.send_message('peer_id', event.peer_id,
                                 "Хей брателла! Это команда только для чатов!! Пошел вон, я не сделаю")
            if event.text == "!gvn":
                bot.send_message('peer_id', event.peer_id, 'Держи gvn!',
                             attachment='video' + str(-164489758) + '_' + str(bot.get_random_video(-164489758)))
            if event.text == '!статус':
                # TODO WTF rewrite it
                found = False
                for user in users:
                    if str(user['vk_id']) == event.extra_values['from']:
                        if user['access_level'] < 7:
                            bot.send_message('chat_id', event.chat_id, "Вы зарегестрированы как " +
                                         user['association'] + "\nВаш текущий уровень: " +
                                         str(user['access_level']) + 'lvl и ' + str(round(user['lvl_exp'], 2)) + ' / ' +
                                         str(dict_of_levels[user['access_level']]) + 'XP')
                            found = True
                        if user['access_level'] >= 7:
                            bot.send_message('chat_id', event.chat_id, "Вы зарегестрированы как " +
                                             user['association'] + "\nВаш текущий уровень: " +
                                             str(user['access_level']) + 'lvl и ' + str(
                                round(user['lvl_exp'], 2)) + 'XP')
                            found = True
                if not found:
                    bot.send_message('chat_id', event.chat_id, "Вы не зарегестрированы ;d" +
                                 " чтобы разегаться юзай !regme <ник>")
            if event.text == '!топ': #TODO delete .lower
                result = 'ТОП по кол-во опыта:\n'
                for i, pgr in enumerate(sorted(users, key=lambda k: (-k['lvl_exp']))[:10]):
                    result += str(i+1) + ')'+ ' @id' + \
                              str(pgr['vk_id']) + '('+ \
                              str(pgr['association']) + ') | exp=' \
                              + str(round(pgr['lvl_exp'], 2))+ '\n'
                bot.send_wo_mention('chat_id', event.chat_id, result)
            if event.text == "!rin":
                bot.send_message('peer_id', event.peer_id, attachment=bot.get_random_photo_album(216,272317811, 595719899))
            if event.text == "!addme":
                try:
                    bot.add_me(event.user_id)
                except:
                    bot.send_message('peer_id', event.peer_id, event.user_id + ': Я вас не смогла добавить!')
            if event.text == "!webm":
                bot.send_message('peer_id', event.peer_id, 'Держи webm!',
                             attachment='video' + str(-30316056) + '_' + str(bot.get_random_video(-30316056)))
            if event.text == "!mashup":
                bot.send_message('peer_id', event.peer_id, attachment='audio' + str(bot.get_random_audio(-39786657)))
            if spaced_words[0] == "!s" and len(spaced_words) == 2:
                if event.from_chat:
                    if is_permitted(int(event.extra_values['from']), 1):
                        try:
                            bot.send_sticker(event.peer_id, int(spaced_words[1]))
                        except:
                            bot.send_message('peer_id', event.peer_id,
                                             'Не существует этого стикера или у автора не куплен!',
                                             attachment='video161959141_456240839')
                    else:
                        bot.send_message_nolinks('peer_id', event.peer_id,
                                     'Poshel von nelizya tebe: @id' + str(event.user_id),
                                     attachment='video161959141_456240839')
                else:
                    try:
                        bot.send_sticker(event.peer_id, int(spaced_words[1]))
                    except:
                        bot.send_message('peer_id', event.peer_id,
                                     'Не существует этого стикера или у автора не куплен!',
                                     attachment='video161959141_456240839')
            if event.text == "!silvagun":
                bot.send_message('peer_id', event.peer_id, attachment='audio' + str(bot.get_random_audio(-144211359)))

            if event.text == "!help":
                bot.send_message('peer_id', event.peer_id,
                             'Картиночки: !лоличан, !murnelis, !ll\nВидео: !gvn, !webm\nМузло: !rx4d, !1канал, '+\
                             '!mashup\nhreni: !тварь, !шанс, !шар, !кто',
                             attachment='doc595719899_550153771')
            if event.text == "!тварь":
                if event.from_chat:
                    if is_permitted(int(event.extra_values['from']), 5):
                        bot.send_wo_mention('peer_id', event.peer_id, "@id" + str(bot.get_random_person(event.chat_id))
                                            + "(тварына!!!)")
                    else:
                        bot.send_message('chat_id', event.chat_id,
                                     "Permission denied, required level to access: 5")
                else:
                    bot.send_message('peer_id', event.peer_id,
                                 "Хей брателла! Это команда только для чатов!! Пошел вон, я не сделаю")
            if event.text == "!everyone":
                if event.from_chat:
                    if is_permitted(int(event.extra_values['from']), 5):
                        bot.send_message('chat_id', event.chat_id,
                                     "[kristian5336|@bruhsoziv][id" +
                                         "[id".join(str(i) + "|\u2063]" for i in bot.get_all(event.chat_id)))
                    else:
                        bot.send_message('chat_id', event.chat_id,
                                     "Permission denied, required level to access: 5")
                else:
                    bot.send_message('peer_id', event.peer_id,
                                 "Хей брателла! Это команда только для чатов!! Пошел вон, я не сделаю")

            if (spaced_words[0] == '!ban' or spaced_words[0] == '!бан') and event.from_chat:
                if is_permitted(int(event.extra_values['from']), 8):
                    if len(spaced_words) >= 2:
                        if len(spaced_words) == 2:
                            await ban.ban(str(event.chat_id),str(spaced_words[1]))
                        if len(spaced_words) == 3:
                            await ban.ban(str(event.chat_id),spaced_words[1], spaced_words[2])
                        if len(spaced_words) > 3:
                            ban.ban(str(event.chat_id),spaced_words[1], spaced_words[2], ' '.join(str(x) for x in spaced_words[3:]))
                    else:
                        bot.send_message('chat_id', event.chat_id, 'Непрвелньый синтаксис!')

            if response == '!suicide':
                bot.send_message('chat_id', event.chat_id, 'Ну и псех..')
                await ban.ban(str(event.chat_id), event.extra_values['from'], 60, 'ебаный самоубийца..')

            if spaced_words[0] == '!шанс' and len(spaced_words) > 1:
                bot.send_message('peer_id', event.peer_id,
                             'Шанс того, что ' + ' '.join(spaced_words[1:]) + ' - '
                             + str(random.randint(1, 100)) + '%')
            if spaced_words[0] == '!pic' and len(spaced_words) == 2:
                bot.send_message('peer_id', event.peer_id, attachment=bot.send_photo(spaced_words[1]))
            if spaced_words[0] == '!шар':
                bot.send_message('peer_id', event.peer_id, 'Мой ответ - ' +
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
                        user_worker.insert(1, int(event.extra_values['from']), spaced_words[1], 0)
                        users.insert(0, {
                            'access_level': 1,
                            'vk_id': int(event.extra_values['from']),
                            'association': spaced_words[1],
                            'lvl_exp': 0})
                        bot.send_message('chat_id', event.chat_id, "вы зарегестировались! Ваш ник: "
                                     + str(spaced_words[1]) + " и уровень 1 :)")

                    else:
                        user_worker.insert(10, event.extra_values['from'], spaced_words[1], 0)
                        users.insert(0, {
                            'access_level': 10,
                            'vk_id': event.extra_values['from'],
                            'association': spaced_words[1],
                            'lvl_exp': 0})
                        bot.send_message('chat_id', event.chat_id, "вы зарегестировались админом! Ваш ник: "
                                     + spaced_words[1] + " и уровень 10 (max) :)")

                elif int(event.extra_values['from']) in list(i['vk_id'] for i in users):
                    bot.send_message('chat_id', event.chat_id, "Вы зарегестрированы :c")
                # TODO добавить сообщение для комманды изменения ассоциации
                else:
                    bot.send_message('chat_id', event.chat_id, "Ассоциация занята")
            if spaced_words[0] == 'o.recolor' and len(spaced_words) == 2:
                if int(event.user_id) in list(i['vk_id'] for i in nicks):
                    for rgp in nicks:
                        if rgp['vk_id'] == int(event.user_id):
                            osu_worker.update(rgp['vk_id'], rgp['nickname'], spaced_words[1],rgp['mode'], rgp['bg'], rgp['percent'])
                            index = list(i['vk_id'] for i in nicks).index(event.user_id)
                            nicks[index] = {
                                'vk_id': event.user_id,
                                'nickname': rgp['nickname'],
                                'color': spaced_words[1],
                                'mode': rgp['mode'],
                                'bg': rgp['bg'],
                                'percent': rgp['percent']}
                            bot.send_message('peer_id', event.peer_id,
                                         "Поздравляю у вас теперь цвет: " + spaced_words[1])
                else:
                    bot.send_message('peer_id', event.peer_id, "Вы не зарегистрированы!")
            if spaced_words[0] == 'o.repos' and len(spaced_words) == 2:
                if int(event.user_id) in list(i['vk_id'] for i in nicks):
                    for rgp in nicks:
                        if rgp['vk_id'] == int(event.user_id):
                            if int(spaced_words[1]) <= int(100):
                                osu_worker.update(rgp['vk_id'], rgp['nickname'], rgp['color'],rgp['mode'], rgp['bg'], spaced_words[1])
                                index = list(i['vk_id'] for i in nicks).index(event.user_id)
                                nicks[index] = {
                                    'vk_id': event.user_id,
                                    'nickname': rgp['nickname'],
                                    'color': rgp['color'],
                                    'mode': rgp['mode'],
                                    'bg': rgp['bg'],
                                    'percent': spaced_words[1]}
                                bot.send_message('peer_id', event.peer_id,
                                             "Расположение было изменено")
                else:
                    bot.send_message('peer_id', event.peer_id, "Вы не зарегистрированы!")
            if spaced_words[0] == 'o.setbg':
                if int(event.user_id) in list(i['vk_id'] for i in nicks):
                    for rgp in nicks:
                        if rgp['vk_id'] == int(event.user_id):
                            if event.attachments == None:
                                if len(spaced_words) == 2:
                                    if ('http' in spaced_words[1] or 'https' in spaced_words[1]) and ('jpg' in spaced_words[1] or 'png' in spaced_words[1]or 'jpeg' in spaced_words[1]):
                                        image_formats = ("image/png", "image/jpeg", "image/jpg")
                                        r = requests.head(spaced_words[1])
                                        if r.headers["content-type"] in image_formats:
                                            osu_worker.update(rgp['vk_id'], rgp['nickname'], rgp['color'], rgp['mode'], spaced_words[1])
                                            index = list(i['vk_id'] for i in nicks).index(event.user_id)
                                            nicks[index] = {
                                                'vk_id': event.user_id,
                                                'nickname': rgp['nickname'],
                                                'mode': rgp['mode'],
                                                'color': rgp['color'],
                                                'bg': spaced_words[1]}
                                            bot.send_message('peer_id', event.peer_id,
                                                             "Поздравляю у вас установлен фон!")
                            if len(spaced_words) == 1:
                                if event.attachments['attach1_type'] == 'photo':
                                    photo = bot.get_link_photo(event.message_id)
                                    osu_worker.update(rgp['vk_id'], rgp['nickname'], rgp['color'],rgp['mode'], photo)
                                    index = list(i['vk_id'] for i in nicks).index(event.user_id)
                                    nicks[index] = {
                                        'vk_id': event.user_id,
                                        'nickname': rgp['nickname'],
                                        'color': rgp['color'],
                                        'mode': rgp['mode'],
                                        'bg': photo}
                                    bot.send_message('peer_id', event.peer_id,
                                                     "Поздравляю у вас установлен фон!")
                else:
                    bot.send_message('peer_id', event.peer_id, "Вы не зарегистрированы!")
            if spaced_words[0] == 'o.delbg':
                if int(event.user_id) in list(i['vk_id'] for i in nicks):
                    for rgp in nicks:
                        if rgp['vk_id'] == int(event.user_id):
                            osu_worker.update(rgp['vk_id'], rgp['nickname'], rgp['color'], rgp['mode'], None)
                            index = list(i['vk_id'] for i in nicks).index(event.user_id)
                            nicks[index] = {
                                'vk_id': event.user_id,
                                'nickname': rgp['nickname'],
                                'mode': rgp['mode'],
                                'color': rgp['color'],
                                'bg': None}
                            bot.send_message('peer_id', event.peer_id,
                                         "Поздравляю фон удален!")
                else:
                    bot.send_message('peer_id', event.peer_id, "Вы не зарегистрированы!")
            if spaced_words[0] == 'o.delcolor':
                if int(event.user_id) in list(i['vk_id'] for i in nicks):
                    for rgp in nicks:
                        if rgp['vk_id'] == int(event.user_id):
                            osu_worker.update(rgp['vk_id'], rgp['nickname'], 0, None, rgp['mode'], rgp['percent'])
                            index = list(i['vk_id'] for i in nicks).index(event.user_id)
                            nicks[index] = {
                                'vk_id': event.user_id,
                                'nickname': rgp['nickname'],
                                'mode': rgp['mode'],
                                'color': None,
                                'bg': rgp['percent']}
                            bot.send_message('peer_id', event.peer_id,
                                         "Цвет удален!")
                else:
                    bot.send_message('peer_id', event.peer_id, "Вы не зарегистрированы!")
            if spaced_words[0] == '!delme':
                if is_permitted(event.extra_values['from'], 1):
                    for pgr in users:
                        # print(users)
                        if pgr['vk_id'] == int(event.extra_values['from']):
                            users.remove(pgr)
                            user_worker.delete(pgr['vk_id'])
                            bot.send_message('chat_id', event.chat_id, "готово?)))")
                else:
                    bot.send_message('chat_id', event.chat_id, "вас и так нет)))")
            # TODO добавить сообщение для комманды изменения ассоциации
            if spaced_words[0] == '!rename' and len(spaced_words) == 2:
                if is_permitted(event.extra_values['from'], 1):
                    for pgr in users:
                        if pgr['vk_id'] == event.user_id:
                            index = list(i['vk_id'] for i in users).index(event.user_id)
                            users[index] = {
                                'access_level': pgr['access_level'],
                                'vk_id': pgr['vk_id'],
                                'association': spaced_words[1],
                                'lvl_exp': pgr['lvl_exp']}
                            user_worker.update(pgr['vk_id'], spaced_words[1], pgr['access_level'], pgr['lvl_exp'])
                            bot.send_message('chat_id', event.chat_id,
                                         "Поздравляю вы теперь: " + spaced_words[1])
                else:
                    bot.send_message('chat_id', event.chat_id, "Ты кто такой сука?")
            if spaced_words[0] == '!addexp':
                if event.from_chat:
                    if admin_id_int == int(event.extra_values['from']):
                        for pgr in users:
                            if pgr['association'] == spaced_words[1]:
                                index = list(i['vk_id'] for i in users).index(pgr['vk_id'])
                                exp = pgr['lvl_exp'] + float(spaced_words[2])
                                users[index] = {
                                    'access_level': pgr['access_level'],
                                    'vk_id': pgr['vk_id'],
                                    'association': pgr['association'],
                                    'lvl_exp': exp}
                                user_worker.update(pgr['vk_id'], spaced_words[1], pgr['access_level'], exp)
                                bot.send_message('chat_id', event.chat_id,
                                             "Поздравляю у пользователя " + spaced_words[1]+ ' ' + str(round(exp, 2))+ 'XP!')
            if spaced_words[0] == '!delexp':
                if event.from_chat:
                    if admin_id_int == int(event.extra_values['from']):
                        for pgr in users:
                            if pgr['association'] == spaced_words[1]:
                                index = list(i['vk_id'] for i in users).index(pgr['vk_id'])
                                exp = pgr['lvl_exp'] - float(spaced_words[2])
                                users[index] = {
                                    'access_level': pgr['access_level'],
                                    'vk_id': pgr['vk_id'],
                                    'association': pgr['association'],
                                    'lvl_exp': exp}
                                user_worker.update(pgr['vk_id'], spaced_words[1], pgr['access_level'], exp)
                                bot.send_message('chat_id', event.chat_id,
                                             "Поздравляю у пользователя " + spaced_words[1]+ ' ' + str(round(exp, 2)) + 'XP!')
            if spaced_words[0] == '!renamelev' and len(spaced_words) == 3:
                if is_permitted(event.extra_values['from'], 10):
                    for pgr in users:
                        if pgr['vk_id'] == event.user_id:
                            index = list(i['vk_id'] for i in users).index(event.user_id)
                            users[index] = {
                                'access_level': int(spaced_words[2]),
                                'vk_id': pgr['vk_id'],
                                'association': spaced_words[1],
                                'lvl_exp': pgr['lvl_exp']}
                            user_worker.update(pgr['vk_id'], spaced_words[1], int(spaced_words[2]), pgr['lvl_exp'])
                            bot.send_message('chat_id', event.chat_id,
                                         "Поздравляю вы теперь: " + spaced_words[1]
                                             + "\nИ ваш уровень: " + spaced_words[2])
                else:
                    bot.send_message('chat_id', event.chat_id, "Ты кто такой сука?")
            if spaced_words[0] == '!relev' and len(spaced_words) == 3:
                if is_permitted(event.extra_values['from'], 10):
                    for pgr in users:
                        if pgr['association'] == spaced_words[1]:
                            index = list(i['association'] for i in users).index(spaced_words[1])
                            users[index] = {
                                'access_level': int(spaced_words[2]),
                                'vk_id': pgr['vk_id'],
                                'association': pgr['association'],
                                'lvl_exp': pgr['lvl_exp']}
                            user_worker.update(pgr['vk_id'], pgr['association'], int(spaced_words[2]), pgr['lvl_exp'])
                            bot.send_message('chat_id', event.chat_id,
                                         "Поздравляю вы " + pgr['association'] +
                                             " получили уровень: " + spaced_words[2])
                else:
                    bot.send_message('chat_id', event.chat_id, "Ты кто такой сука?")

            """ Добавление и удаление комманд """
            # TODO добавить уровни и контроль юзеров
            if spaced_words[0] == '!addcom' and len(spaced_words) >= 3:
                if is_permitted(event.user_id, 1):
                    if spaced_words[1] == spaced_words[2]:
                        bot.send_message('peer_id', event.peer_id, "Нельзя добавить эхо-комманду")
                    elif spaced_words[1] in list(i['name'] for i in commands):
                        bot.send_message('peer_id', event.peer_id, "Нельзя добавить существуюую комманду")
                    else:
                        print(spaced_words[-1])
                        if ('http' in spaced_words[2] or 'https' in spaced_words[2]) \
                                and ('jpeg' in spaced_words[2] or 'jpg' in spaced_words[2] or 'png' in spaced_words[2]):
                            print(spaced_words[-1])
                            if 'photo' not in spaced_words[2]:
                                if 'video' not in spaced_words[2]:
                                    if 'graffiti' not in spaced_words[2:]:
                                        if ''.join(' '.join(response.split()[:1])) != 'vto.pe' \
                                                or 'vkmix.com' \
                                                or 'Синий кит' \
                                                or 'Сова никогда не спит':
                                            if spaced_words[3:] == None:
                                                pic = bot.send_photo(spaced_words[2])
                                                command_worker.insert(10, spaced_words[1], ' ', pic)
                                                commands.insert(0, {
                                                    'access_level': 1,
                                                    'name': spaced_words[1],
                                                    'value': ' ',
                                                    'attachment': pic})

                                                bot.send_message('peer_id', event.peer_id,
                                                                 "Комманда " + spaced_words[1] + " добавлена!")
                                            if spaced_words[3:] != None:
                                                pic = bot.send_photo(spaced_words[2])
                                                command_worker.insert(10, spaced_words[1], ' '.join(spaced_words[3:]), pic)
                                                commands.insert(0, {
                                                    'access_level': 1,
                                                    'name': spaced_words[1],
                                                    'value': ' '.join(spaced_words[3:]),
                                                    'attachment': pic})

                                                bot.send_message('peer_id', event.peer_id,
                                                                 "Комманда " + spaced_words[1] + " добавлена!")
                                        else:
                                            bot.send_message(event.peer_id,
                                                         'Пошел вон отсюда не приходи сюда больше')
                        if ('photo' in spaced_words[2] or 'video' in spaced_words[2]
                            or 'http' not in spaced_words[2]
                            or 'https' not in spaced_words[2]) \
                                and ('video' in spaced_words[2]
                                     or 'photo' in spaced_words[2]
                                     or 'jpeg' not in spaced_words[2]
                                     or 'jpg' not in spaced_words[2]
                                     or 'png' not in spaced_words[2]):
                            if 'photo' not in spaced_words[2]:
                                if 'video' not in spaced_words[2]:
                                    if 'graffiti' not in spaced_words[2:]:
                                        if ''.join(' '.join(response.split()[:1])) != 'vto.pe' \
                                                or 'vkmix.com' \
                                                or 'Синий кит' \
                                                or 'Сова никогда не спит':
                                            command_worker.insert(10, spaced_words[1], ' '.join(spaced_words[2:]), ' ')
                                            commands.insert(0, {
                                                'access_level': 1,
                                                'name': spaced_words[1],
                                                'value': ' '.join(spaced_words[2:]),
                                                'attachment': ''})

                                            bot.send_message('peer_id', event.peer_id,
                                                             "Комманда " + spaced_words[1] + " добавлена!")
                                        else:
                                            bot.send_message('peer_id', event.peer_id, 'А нафиг пойти не? не добавлю')
                            if 'graffiti' in spaced_words[2:]:
                                if event.attachments['attach1_type'] == 'photo':
                                    if spaced_words[3:] == None:
                                        id_photo = bot.get_photo_id(event.message_id, 1)
                                        command_worker.insert(10, spaced_words[1], ' ', id_photo)
                                        commands.insert(0, {
                                            'access_level': 1,
                                            'name': spaced_words[1],
                                            'value': ' ',
                                            'attachment': id_photo})
                                        bot.send_message('peer_id', event.peer_id,
                                                         "Комманда " + spaced_words[1] + " добавлена!")
                                    if spaced_words[3:] != None:
                                        if ''.join(' '.join(response.split()[:1])) != 'vto.pe' \
                                                or 'vkmix.com' \
                                                or 'Синий кит' \
                                                or 'Сова никогда не спит':
                                            id_photo = bot.get_photo_id(event.message_id, 1)
                                            command_worker.insert(10, spaced_words[1], ' '
                                                                  .join(spaced_words[3:]), id_photo)
                                            commands.insert(0, {
                                                'access_level': 1,
                                                'name': spaced_words[1],
                                                'value': ' '.join(spaced_words[3:]),
                                                'attachment': id_photo})
                                            bot.send_message('peer_id', event.peer_id,
                                                             "Комманда " + spaced_words[1] + " добавлена!")
                            if 'photo' in spaced_words[2]:
                                if event.attachments['attach1_type'] == 'photo':
                                    if spaced_words[3:] == None:
                                        id_photo = bot.get_photo_id(event.message_id)
                                        command_worker.insert(10, spaced_words[1], ' ', id_photo)
                                        commands.insert(0, {
                                            'access_level': 1,
                                            'name': spaced_words[1],
                                            'value': ' ',
                                            'attachment': id_photo})
                                        bot.send_message('peer_id', event.peer_id,
                                                         "Комманда " + spaced_words[1] + " добавлена!")
                                    if spaced_words[3:] != None:
                                        if ''.join(' '.join(response.split()[:1])) != 'vto.pe' \
                                                or 'vkmix.com' \
                                                or 'Синий кит' \
                                                or 'Сова никогда не спит':
                                            id_photo = bot.get_photo_id(event.message_id)
                                            command_worker.insert(10, spaced_words[1], ' '
                                                                  .join(spaced_words[3:]), id_photo)
                                            commands.insert(0, {
                                                'access_level': 1,
                                                'name': spaced_words[1],
                                                'value': ' '.join(spaced_words[3:]),
                                                'attachment': id_photo})
                                            bot.send_message('peer_id', event.peer_id,
                                                             "Комманда " + spaced_words[1] + " добавлена!")
                            if 'video' in spaced_words[2]:
                                if event.attachments['attach1_type'] == 'video':
                                    if spaced_words[3:] == None:
                                        id_photo = 'video' + event.attachments['attach1']
                                        command_worker.insert(10, spaced_words[1], ' '.join(spaced_words[3:]), id_photo)
                                        commands.insert(0, {
                                                'access_level': 1,
                                                'name': spaced_words[1],
                                                'value': ' ',
                                                'attachment': id_photo})
                                        bot.send_message('peer_id', event.peer_id,
                                                         "Комманда " + spaced_words[1] + " добавлена!")
                                    if spaced_words[3:] != None:
                                        if ''.join(' '.join(response.split()[:1])) != 'vto.pe' \
                                                or 'vkmix.com' \
                                                or 'Синий кит' \
                                                or 'Сова никогда не спит':
                                            id_photo = 'video' + event.attachments['attach1']
                                            command_worker.insert(10, spaced_words[1], ' ', id_photo)
                                            commands.insert(0, {
                                                'access_level': 1,
                                                'name': spaced_words[1],
                                                'value': ' '.join(spaced_words[3:]),
                                                'attachment': id_photo})
                                            bot.send_message('peer_id', event.peer_id,
                                                             "Комманда " + spaced_words[1] + " добавлена!")
                else:
                    bot.send_message('chat_id', event.chat_id, "Permission denied, required level to access: 5")
                    #TODO level is not text idiot
            if spaced_words[0] == '!delcom' and len(spaced_words) == 2:
                if is_permitted(event.user_id, 1):
                    for item in commands:
                        if item['name'] == spaced_words[1]:
                            command_worker.delete(spaced_words[1])
                            index = list(i['name'] for i in commands).index(spaced_words[1])
                            commands.pop(index)
                            bot.send_message('peer_id', event.peer_id,
                                         "Комманда " + spaced_words[1] + " удалена!")
                            break
                else:
                    bot.send_message('chat_id', event.chat_id, "Permission denied, required level to access: 5")


async def main():
    await longpool_handle()


asyncio.run(main())