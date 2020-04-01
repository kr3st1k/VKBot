from vk_api.longpoll import VkLongPoll, VkEventType
import vk_api
from datetime import datetime
import random
import get_pictures
import get_pictures2
import get_hentai
import get_itpedia
import get_fateprikol
import get_fateart
import get_3d
import get_kuk
import get_rin
import get_rin18
import get_erish
import get_ishtar
import cumshot
import settings


vk_session = vk_api.VkApi(token=settings.get_token())
session_api = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

def send_message(vk_session, id_type, id, message=None, attachment=None, keyboard=None):
    vk_session.method('messages.send',{id_type: id, 'message': message, 'random_id': random.randint(-2147483648, +2147483648), "attachment": attachment, 'keyboard': keyboard})

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        print('Время: ' + str(datetime.strftime(datetime.now(), "%H:%M:%S")))
        print('Текст ПИДОРАСА: ' + str(event.text))
        print(event.user_id)
        response = event.text


        if event.text.lower() == "!камни":
                send_message(vk_session, 'chat_id', event.chat_id, '🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿')
        if event.text.lower() == "!vkbot":
                send_message(vk_session, 'chat_id', event.chat_id, 'Комманды бота Ильи: \n >>>>>>>>>>>>>>>>>>>> \n <<КОМАНДЫ>> \n  \n •!шанс ---->узнать шанс чего-либо \n •!шар --->вопрос, после чего будет выдан ответ \n  \n <<РАНДОМ АНИМЕ АРТЫ>> \n  \n •!лоли \n •!юри \n •!ахегао \n •!фейт прикол \n •!фейт арт \n •!камшот \n \n <<3Д ТЯНКИ И НЕ ТОЛЬКО>> \n  \n •!3д мусор \n •!кукла \n \n <<ТОСАКА РИН>> \n \n •!тосака \n •!тосака2 ---> хентай \n •!иштар \n •!эриш  \n \n <<ПРОЧЕЕ ГОВНО>> \n \n •!камни \n •!палата шевцова \n •!хуесосина \n •!колда \n •!музыка \n •!радмир \n •!клоун', attachment='photo564230346_457239307')
        if event.text.lower() == "!лоли":
                attachment = get_pictures.get(vk_session, -127518015, session_api)
                vk_session.method('messages.send', {'chat_id': event.chat_id, 'message': 'Держи девочку!', 'random_id': 0, "attachment": attachment})
        if event.text.lower() == "!юри":
                attachment = get_pictures2.get(vk_session, -153284406, session_api)
                vk_session.method('messages.send', {'chat_id': event.chat_id, 'message': 'держи лесбух!', 'random_id': 0, "attachment": attachment})
        if event.text.lower() == "!ахегао":
                attachment = get_hentai.get(vk_session, -128535882, session_api)
                vk_session.method('messages.send', {'chat_id': event.chat_id, 'message': 'держи ахегао, конченый извращенец!', 'random_id': 0, "attachment": attachment})
        if event.text.lower() == "!палата шевцова":
                attachment = get_itpedia.get(vk_session, -88245281, session_api)
                vk_session.method('messages.send', {'chat_id': event.chat_id, 'message': 'держи мем из палаты Шевцова!', 'random_id': 0, "attachment": attachment})
        if event.text.lower() == "!фейт прикол":
                attachment = get_fateprikol.get(vk_session, -183563128, session_api)
                vk_session.method('messages.send', {'chat_id': event.chat_id, 'message': 'держи мем из группы Fate/GrandПрикол!', 'random_id': 0, "attachment": attachment})
        if event.text.lower() == "!фейт арт":
                attachment = get_fateart.get(vk_session, -191752227, session_api)
                vk_session.method('messages.send', {'chat_id': event.chat_id, 'message': 'держи арт из группы far side of the moon!', 'random_id': 0, "attachment": attachment})
        if event.text.lower() == "!3д мусор":
                attachment = get_3d.get(vk_session, -70232735, session_api)
                vk_session.method('messages.send', {'chat_id': event.chat_id, 'message': 'держи свой 3д мусор!', 'random_id': 0, "attachment": attachment})
        if event.text.lower() == "!кукла":
                attachment = get_kuk.get(vk_session, -186765691, session_api)
                vk_session.method('messages.send', {'chat_id': event.chat_id, 'message': 'держи свою куклу, куклоёб!', 'random_id': 0, "attachment": attachment})
        if event.text.lower() == "!хуесосина":
                send_message(vk_session, 'chat_id', event.chat_id, attachment='video210923765_456239281')
        if event.text.lower() == "!колда":
                send_message(vk_session, 'chat_id', event.chat_id, attachment='video537612639_456239020')
        if event.text.lower() == "!музыка":
                send_message(vk_session, 'chat_id', event.chat_id, attachment='audio564230346_456239018,audio564230346_456239019,audio564230346_456239017')
        if event.text.lower() == "!тосака":
                attachment = get_rin.get(vk_session, -119603422, session_api)
                vk_session.method('messages.send', {'chat_id': event.chat_id, 'message': 'держи Тосаку!', 'random_id': 0, "attachment": attachment})
        if event.text.lower() == "!тосака2":
            attachment = get_rin18.get(vk_session, -119603422, session_api)
            vk_session.method('messages.send', {'chat_id': event.chat_id, 'message': 'держи хентайную Тосаку!', 'random_id': 0, "attachment": attachment})
        if event.text.lower() == "!иштар":
            attachment = get_ishtar.get(vk_session, -119603422, session_api)
            vk_session.method('messages.send', {'chat_id': event.chat_id, 'message': 'держи Иштар!', 'random_id': 0, "attachment": attachment})
        if event.text.lower() == "!эриш":
            attachment = get_erish.get(vk_session, -119603422, session_api)
            vk_session.method('messages.send', {'chat_id': event.chat_id, 'message': 'держи Эрешкигаль!', 'random_id': 0, "attachment": attachment})
        if event.text.lower() == "!радмир":
                send_message(vk_session, 'chat_id', event.chat_id, attachment='photo564230346_457239374')
        if event.text.lower() == "!клоун":
            send_message(vk_session, 'chat_id', event.chat_id, attachment='photo564230346_457239422')
        spaced_words = str(response).split(' ')
        if (spaced_words[0] == '!шанс'):
            vk_session.method('messages.send', {'chat_id': event.chat_id, 'message': 'Шанс того, что ' + ' '.join(spaced_words[1:]) + ' - ' + str(random.randint(1, 100)) + '%','random_id': 0})
        spaced_words = str(response).split(' ')
        if (spaced_words[0] == '!шар'):
            vk_session.method('messages.send', {'chat_id': event.chat_id, 'message': 'Мойт ответ - ' + str(random.choice(["Да", "Нет", "Скорее всего, но это не точно", "В душе не ебу если честно", "Да, это прям 100%", "нет,ты чё шизоид?"])) + ' ','random_id': 0})
        if event.text.lower() == "!камшот":
            attachment = cumshot.get(vk_session, -2343758, session_api)
            vk_session.method('messages.send', {'chat_id': event.chat_id, 'message': 'держи рандом скриншот!', 'random_id': 0, "attachment": attachment})


