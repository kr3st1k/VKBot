import json

﻿from vk_api.longpoll import VkLongPoll, VkEventType
import vk_api
from datetime import datetime
import random
import time
import get_pictures
import get_murnelis
import get_idolhell
from Database.CommandDbWorker import CommandWorker

# load all commands

command_worker = CommandWorker()
commands = command_worker.select_all()

vk_session = vk_api.VkApi("")
session_api = vk_session.get_api()
longpoll = VkLongPoll(vk_session)


def send_message(vk_session, id_type, id, message=None, attachment=None, keyboard=None):
    vk_session.method('messages.send',
                      {id_type: id, 'message': message, 'random_id': random.randint(-2147483648, +2147483648),
                       "attachment": attachment, 'keyboard': keyboard})


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        print('Время: ' + str(datetime.strftime(datetime.now(), "%H:%M:%S")))
        print('Текст человека: ' + str(event.text))
        response = event.text

        for item in commands:
            if item['name'] == event.text:
                # from chat
                send_message(vk_session, 'chat_id', event.chat_id, item['value'])
if event.text.lower() == "!камни":
            send_message(vk_session, 'chat_id', event.chat_id, '🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿')
        if event.text.lower() == "камни":
            send_message(vk_session, 'user_id', event.user_id, '🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿')    
            
        if event.text.lower() == ".monday":
            send_message(vk_session, 'chat_id', event.chat_id, 'Понедельник: ОБЖ каб.321, Физика каб.320, Информатика каб.416, Обществознание Каб.111')                
        if event.text.lower() == ".tuesday1":            
            send_message(vk_session, 'chat_id', event.chat_id, 'Вторник: Физкультура, Физика каб.320, Информатика каб.416') 
        if event.text.lower() == ".tuesday2":            
            send_message(vk_session, 'chat_id', event.chat_id, 'Вторник: Физкультура, Физика каб.320, Информатика каб.416, Обществознание каб.111') 
        if event.text.lower() == ".wednesday1":           
            send_message(vk_session, 'chat_id', event.chat_id, 'Среда: Ко второй паре, Матика каб.303, Литература каб.314, Англ (Леонова) каб.315') 
        if event.text.lower() == ".wednesday2":            
            send_message(vk_session, 'chat_id', event.chat_id, 'Среда: Ко второй паре, Матика каб.303, Литература каб.314, ОБЖ каб.321') 
        if event.text.lower() == ".thursday1":            
            send_message(vk_session, 'chat_id', event.chat_id, 'Четверг: Литература Каб.314, История Каб.230, История каб.230')
        if event.text.lower() == ".thursday2":            
            send_message(vk_session, 'chat_id', event.chat_id, 'Четверг: Физкультура, История каб.230, Обществознание каб.111')
        if event.text.lower() == ".friday1":          
            send_message(vk_session, 'chat_id', event.chat_id, 'Пятница: Иностранный язык (Сакерина) каб.304, Матика каб.303, Английский каб.304 (Сакерина) каб.315 (Леонова), Русский каб.314')
        if event.text.lower() == ".friday2":            
            send_message(vk_session, 'chat_id', event.chat_id, 'Пятница: Астрономия каб.422, Матика каб.303, Английский каб.304 (Сакерина) каб.315 (Леоновa), Русский каб.314 Каб.111')
        if event.text.lower() == ".saturday1":   
            send_message(vk_session, 'chat_id', event.chat_id, 'Суббота: Матика каб.303, Химия каб.422')
        if event.text.lower() == ".saturday2":
            send_message(vk_session, 'chat_id', event.chat_id, 'Суббота: Матика каб.303, Химия каб.422, Биология каб.403, Экология каб.403')
        if event.text.lower() == "/monday":
            send_message(vk_session, 'user_id', event.user_id, 'Понедельник: ОБЖ каб.321, Физика каб.320, Информатика каб.416, Обществознание Каб.111')                
        if event.text.lower() == "/tuesday1":            
            send_message(vk_session, 'user_id', event.user_id, 'Вторник: Физкультура, Физика каб.320, Информатика каб.416') 
        if event.text.lower() == "/tuesday2":            
            send_message(vk_session, 'user_id', event.user_id, 'Вторник: Физкультура, Физика каб.320, Информатика каб.416, Обществознание каб.111') 
        if event.text.lower() == "/wednesday1":           
            send_message(vk_session, 'user_id', event.user_id, 'Среда: Ко второй паре, Матика каб.303, Литература каб.314, Англ (Леонова) каб.315') 
        if event.text.lower() == "/wednesday2":            
            send_message(vk_session, 'user_id', event.user_id, 'Среда: Ко второй паре, Матика каб.303, Литература каб.314, ОБЖ каб.321') 
        if event.text.lower() == "/thursday1":            
            send_message(vk_session, 'user_id', event.user_id, 'Четверг: Литература Каб.314, История Каб.230, История каб.230')
        if event.text.lower() == "/thursday2":            
            send_message(vk_session, 'user_id', event.user_id, 'Четверг: Физкультура, История каб.230, Обществознание каб.111')
        if event.text.lower() == "/friday1":          
            send_message(vk_session, 'user_id', event.user_id, 'Пятница: Иностранный язык (Сакерина) каб.304, Матика каб.303, Английский каб.304 (Сакерина) каб.315 (Леонова), Русский каб.314')
        if event.text.lower() == "/friday2":            
            send_message(vk_session, 'user_id', event.user_id, 'Пятница: Астрономия каб.422, Матика каб.303, Английский каб.304 (Сакерина) каб.315 (Леоновa), Русский каб.314 Каб.111')
        if event.text.lower() == "/saturday1":   
            send_message(vk_session, 'user_id', event.user_id, 'Суббота: Матика каб.303, Химия каб.422')
        if event.text.lower() == "/saturday2":
            send_message(vk_session, 'user_id', event.user_id, 'Суббота: Матика каб.303, Химия каб.422, Биология каб.403, Экология каб.403')    
        
        if event.text.lower() == "!лоличан":
            attachment = get_pictures.get(vk_session, -127518015, session_api)
            vk_session.method('messages.send', {'chat_id': event.chat_id, 'message': 'Держи девочку!', 'random_id': 0, "attachment": attachment})    
        if event.text.lower() == "/лоличан":
            attachment = get_pictures.get(vk_session, -127518015, session_api)
            vk_session.method('messages.send', {'user_id': event.user_id, 'message': 'Держи девочку!', 'random_id': 0, "attachment": attachment}) 
        if event.text.lower() == "!murnelis":
            attachment = get_murnelis.get(vk_session, -182090873, session_api)
            vk_session.method('messages.send', {'chat_id': event.chat_id, 'message': 'Держи мем!', 'random_id': 0, "attachment": attachment})    
        if event.text.lower() == "/murnelis":
            attachment = get_murnelis.get(vk_session, -182090873, session_api)
            vk_session.method('messages.send', {'user_id': event.user_id, 'message': 'Держи мем!', 'random_id': 0, "attachment": attachment}) 
        if event.text.lower() == "!ll":
            attachment = get_idolhell.get(vk_session, -119420102, session_api)
            vk_session.method('messages.send', {'chat_id': event.chat_id, 'message': 'Держи LoveLive!', 'random_id': 0, "attachment": attachment})    
        if event.text.lower() == "/ll":
            attachment = get_idolhell.get(vk_session, -119420102, session_api)
            vk_session.method('messages.send', {'user_id': event.user_id, 'message': 'Держи LoveLive!', 'random_id': 0, "attachment": attachment}) 
        if event.text.lower() == "/rx4d":
            send_message(vk_session, 'user_id', event.user_id, attachment='audio564230346_456239018,audio564230346_456239019,audio564230346_456239017')
        if event.text.lower() == "!rx4d":
            send_message(vk_session, 'chat_id', event.chat_id, attachment='audio564230346_456239018,audio564230346_456239019,audio564230346_456239017')
        if event.text.lower() == "/1канал":
            send_message(vk_session, 'user_id', event.user_id, attachment='audio161959141_456241503')
        if event.text.lower() == "!1канал":
            send_message(vk_session, 'chat_id', event.chat_id, attachment='audio161959141_456241503')
        if event.text.lower() == "!банан":
            send_message(vk_session, 'chat_id', event.chat_id, attachment='video210923765_456239281')
        if event.text.lower() == "банан":
            send_message(vk_session, 'user_id', event.user_id, attachment='video210923765_456239281')
        if event.text == "!кто":
            vaal = random.choice((vk_session.method('messages.getChat', {'chat_id': event.chat_id}))['users'])
            vk_session.method('messages.send',
                              {'chat_id': event.chat_id, 'message': "@id" + str(vaal) + "(он!!!)", 'random_id': 0})
        if event.text.lower() == "!gvn":
            huy = vk_session.method('video.get',{'owner_id':'-164489758', 'count':200, 'offset':1})['items']
            qwert = random.choice(list(i for i in huy))
            vk_session.method('messages.send', {'chat_id': event.chat_id, 'message': 'Держи gvn!', 'random_id': 0, "attachment": 'video' + str(-164489758) + '_' + str(qwert['id'])})    
        if event.text.lower() == "/gvn":
            huy = vk_session.method('video.get',{'owner_id':'-164489758', 'count':200, 'offset':1})['items']
            qwert = random.choice(list(i for i in huy))
            vk_session.method('messages.send', {'user_id': event.user_id, 'message': 'Держи gvn!', 'random_id': 0, "attachment": 'video' + str(-164489758) + '_' + str(qwert['id'])})             
        spaced_words = str(response).split(' ')
        if event.text.lower() == ".help":
            send_message(vk_session, 'chat_id', event.chat_id, 'Расписание: .monday, .tuesday1, .tuesday2, .wednesday1, .wednesday2, .thursday1, .thursday2, .friday1, .friday2, .saturday1, .saturday2\nКартиночки: !лоличан, !murnelis, !ll\nВидео: !банан\nМузло: !rx4d, !1канал')  
        if event.text.lower() == "/help":
            send_message(vk_session, 'user_id', event.user_id, 'Расписание: /monday, /tuesday1, /tuesday2, /wednesday1, /wednesday2, /thursday1, /thursday2, /friday1, /friday2, /saturday1, /saturday2\nКартиночки: /лоличан, /murnelis, /ll\nВидео: /банан\nМузло: /rx4d')  
        if event.text.lower() == "!тварь":
            val = random.choice((vk_session.method('messages.getChat', {'chat_id': event.chat_id}))['users'])
            vk_session.method('messages.send',
                              {'chat_id': event.chat_id, 'message': "@id" + str(val) + "(тварына!!!)", 'random_id': 0})
        if event.text.lower() == "!everyone":
            varl = (vk_session.method('messages.getChat', {'chat_id': event.chat_id})['users'])
            vk_session.method('messages.send',
                              {'chat_id': event.chat_id, 'message':"[kristian5336|@bruhsoziv][id" + "[id".join(str(i) +"|\u2063]" for i in varl), 'random_id': 0})
        if spaced_words[0] == '!шанс' and len(spaced_words) > 1:
            vk_session.method('messages.send', {'chat_id': event.chat_id,
                                                'message': 'Шанс того, что ' + ' '.join(spaced_words[1:]) + ' - '
                                                           + str(random.randint(1, 100)) + '%', 'random_id': 0})
        if spaced_words[0] == '!шар':
            vk_session.method('messages.send', {'chat_id': event.chat_id,
                                                'message': 'Мойт ответ - ' +
                                                           str(random.choice(["Да",
                                                                              "Нет",
                                                                              "Скорее всего, но это не точно",
                                                                              "В душе не ебу если честно",
                                                                              "Да, это прям 100%",
                                                                              "нет,ты чё шизоид?"]))
                                                           + ' ', 'random_id': 0})

        """ Добавление и удаление комманд """
        # TODO добавить уровни и контроль юзеров
        if spaced_words[0] == '!addcom' and len(spaced_words) >= 3:
            if spaced_words[1] == spaced_words[2]:
                send_message(vk_session, 'chat_id', event.chat_id, "Нельзя добавить эхо-комманду")
            else:
                command_worker.insert(10, spaced_words[1], ' '.join(spaced_words[2:]))
                commands.insert(0, {
                    'access_level': 10,
                    'name': spaced_words[1],
                    'value': ' '.join(spaced_words[2:])})

                send_message(vk_session, 'chat_id', event.chat_id, "Комманда " + spaced_words[1] + " добавлена!")

        if spaced_words[0] == '!delcom' and len(spaced_words) == 2:
            for item in commands:
                if item['name'] == spaced_words[1]:
                    command_worker.delete(spaced_words[1])
                    index = list(i['name'] for i in commands).index(spaced_words[1])
                    commands.pop(index)
                    send_message(vk_session, 'chat_id', event.chat_id, "Комманда " + spaced_words[1] + " удалена!")
                    break
