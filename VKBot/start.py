from vk_api.longpoll import VkLongPoll, VkEventType
import vk_api
from subprocess import Popen, PIPE
import subprocess
from datetime import datetime
import time
import random
from StartupLoader.StartupLoader import StartupLoader
config_loader = StartupLoader('config.JSON')

vk_session = vk_api.VkApi(token=config_loader.get_vk_token())
session_api = vk_session.get_api()
longpoll = VkLongPoll(vk_session)


def send_message(vk_session, message=None, attachment=None, keyboard=None):
    vk_session.method('messages.send',
                      {"peer_id": event.peer_id, 'message': message,
                       'random_id': random.randint(-2147483648, +2147483648),
                       "attachment": attachment, 'keyboard': keyboard})


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
                            send_message(vk_session, out.stdout[0:500])
                            send_message(vk_session, out.stdout[500:1000])
                            send_message(vk_session, out.stdout[1000:1500])
                            send_message(vk_session, out.stdout[1500:2000])
                        else:
                            if out.stderr == ' ':
                                send_message(vk_session, 'all done..')
                            else:
                                print(out.stderr)
                                send_message(vk_session,out.stderr[0:500])
                                send_message(vk_session,out.stderr[500:1000])
                    except BaseException as e:
                        if e == ' ':
                            send_message(vk_session, 'all done..')
                        else:
                            print(e)
                            send_message(vk_session, 'all done..' + e[0:500])
                            send_message(vk_session, 'all done..' + e[500:1000])
                            send_message(vk_session, 'all done..' + e[1000:1500])
                            send_message(vk_session, 'all done..' + e[1500:2000])
                if response == '!botstatus':
                    try:
                        out = subprocess.run('sudo pm2 list', shell=True, stdout=subprocess.PIPE,
                                                 stderr=subprocess.PIPE, encoding='utf-8')
                        if out.returncode == 0:
                            print(out.stdout)
                            send_message(vk_session, out.stdout[548:636])
                        else:
                            if out.stderr != ' ':
                                print(out.stderr)
                                send_message(vk_session, out.stderr)
                    except BaseException as e:
                        if e == ' ':
                            send_message(vk_session, 'all done..')
                        else:
                            print(e)
                            send_message(vk_session, 'all done..' + e[326:800])
                            send_message(vk_session, 'all done..' + e[800:1000])
                            send_message(vk_session, 'all done..' + e[1000:1500])
                            send_message(vk_session, 'all done..' + e[1500:2000])
                if response == '!restart':
                    out = subprocess.run('sudo pm2 restart vkbot', shell=True, stdout=subprocess.PIPE,
                                                 stderr=subprocess.PIPE, encoding='utf-8')
                    if out.returncode == 0:
                            send_message(vk_session, 'Бот перезагружен!')
    except BaseException as error:
        print(error)
