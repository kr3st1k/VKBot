from vk_api.longpoll import VkLongPoll, VkEventType
import vk_api
from subprocess import Popen, PIPE
import subprocess
from datetime import datetime
import time
import random

vk_session = vk_api.VkApi(token="cb5793ad0a6f4ac5730a102091c70b5f512cd0ecbc65a4cba092bee967503c67eb44eb9e583b93906de00")
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
                            send_message(vk_session, out.stdout)
                        else:
                            if out.stderr == ' ':
                                send_message(vk_session, 'all done..')
                            else:
                                print(out.stderr)
                                send_message(vk_session, 'all done.. :' + out.stderr)
                    except BaseException as e:
                        if e == ' ':
                            send_message(vk_session, 'all done..')[0:500]
                            send_message(vk_session, 'all done..')[500:1000]
                        else:
                            print(e)
                            send_message(vk_session, 'all done..' + e)[0:500]
                            send_message(vk_session, 'all done..' + e)[500:1000]
    except BaseException as error:
        print(error)
