from vk_api.longpoll import VkLongPoll, VkEventType
import vk_api
from subprocess import Popen, PIPE
import subprocess
from datetime import datetime
import time
import random
from StartupLoader.StartupLoader import StartupLoader
from VkBot import VkBot
config_loader = StartupLoader('config.JSON')

vk_session = vk_api.VkApi(token=config_loader.get_vk_token())
session_api = vk_session.get_api()
longpoll = VkLongPoll(vk_session)
bot = VkBot(vk_session, session_api)
#TODO redo functions

while True:
    try:
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                print('Время: ' + str(datetime.strftime(datetime.now(), "%H:%M:%S")))
                print('Текст человека: ' + str(event.text))
                print(event.attachments)
                try:
                    print(event.user_id)
                except:
                    print(event.peer_id)
                response = event.text

                if ' '.join(response.split()[:1]) == "!cmd" and ' '.join(response.split()[1:]):
                    try:
                        out = subprocess.run(' '.join(response.split()[1:]), shell=True, stdout=subprocess.PIPE,
                                                 stderr=subprocess.PIPE, encoding='utf-8')
                        if out.returncode == 0:
                            print(out.stdout)
                            bot.send_message('peer_id', event.peer_id,out.stdout[0:900])
                            bot.send_message('peer_id', event.peer_id,out.stdout[1000:1500])
                            bot.send_message('peer_id', event.peer_id,out.stdout[1500:2000])
                        else:
                            if out.stderr == ' ':
                                bot.send_message('peer_id', event.peer_id,'all done..')
                            else:
                                print(out.stderr)
                                bot.send_message('peer_id', event.peer_id,out.stderr[0:500])
                                bot.send_message('peer_id', event.peer_id,out.stderr[500:1000])
                    except BaseException as e:
                        if e == ' ':
                            bot.send_message(vk_session, 'all done..')
                        else:
                            print(e)
                            bot.send_message('peer_id', event.peer_id,'all done..' + e[0:500])
                            bot.send_message('peer_id', event.peer_id,'all done..' + e[500:1000])
                            bot.send_message('peer_id', event.peer_id,'all done..' + e[1000:1500])
                            bot.send_message('peer_id', event.peer_id,'all done..' + e[1500:2000])
                if response == '!botstatus':
                    try:
                        out = subprocess.run('sudo pm2 list', shell=True, stdout=subprocess.PIPE,
                                                 stderr=subprocess.PIPE, encoding='utf-8')
                        if out.returncode == 0:
                            print(out.stdout)
                            bot.send_message('peer_id', event.peer_id,out.stdout[548:636])
                        else:
                            if out.stderr != ' ':
                                print(out.stderr)
                                bot.send_message('peer_id', event.peer_id,out.stderr)
                    except BaseException as e:
                        if e == ' ':
                            bot.send_message('peer_id', event.peer_id,'all done..')
                        else:
                            print(e)
                            bot.send_message('peer_id', event.peer_id,'all done..' + e[326:800])
                            bot.send_message('peer_id', event.peer_id,'all done..' + e[800:1000])
                            bot.send_message('peer_id', event.peer_id,'all done..' + e[1000:1500])
                            bot.send_message('peer_id', event.peer_id,'all done..' + e[1500:2000])
                if response == '!restart':
                    out = subprocess.run('sudo pm2 restart vkbot', shell=True, stdout=subprocess.PIPE,
                                                 stderr=subprocess.PIPE, encoding='utf-8')
                    if out.returncode == 0:
                            bot.send_message('peer_id', event.peer_id,'Бот перезагружен!')
                if response == '!stop':
                    out = subprocess.run('sudo pm2 stop vkbot', shell=True, stdout=subprocess.PIPE,
                                                 stderr=subprocess.PIPE, encoding='utf-8')
                    if out.returncode == 0:
                            bot.send_message('peer_id', event.peer_id,'Бот остановлен, но может перезапуститься автоматом!')
                if response == '!start':
                    out = subprocess.run('sudo pm2 start vkbot', shell=True, stdout=subprocess.PIPE,
                                                 stderr=subprocess.PIPE, encoding='utf-8')
                    if out.returncode == 0:
                            bot.send_message('peer_id', event.peer_id,'Бот запущен!')
    except BaseException as error:
        print(error)
