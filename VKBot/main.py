from vk_api.longpoll import VkLongPoll, VkEventType
import vk_api
from datetime import datetime
import random
import time
import logging
from Database.CommandDbWorker import CommandWorker

# load all commands

command_worker = CommandWorker()
commands = command_worker.select_all()

vk_session = vk_api.VkApi(token="huh?")
session_api = vk_session.get_api()
longpoll = VkLongPoll(vk_session)


def send_message(vk_session, id_type, id, message=None, attachment=None, keyboard=None):
	vk_session.method('messages.send',
					  {id_type: id, 'message': message, 'random_id': random.randint(-2147483648, +2147483648),
					   "attachment": attachment, 'keyboard': keyboard})
def send_sticker(vk_session, sticker_id):
	vk_session.method('messages.sendSticker', {'peer_id': event.peer_id, 'random_id': 0,
											   "sticker_id": sticker_id})

def get_pictures(vk_session, id_group, vk):
    try:
        attachment = ''
        max_num = vk.photos.get(owner_id=id_group, album_id='wall', count=0)['count']
        num = random.randint(1, max_num)
        pictures = vk.photos.get(owner_id=str( id_group), album_id='wall', count=1, offset=num)['items']
        buf = []
        for element in pictures:
            buf.append('photo' + str( id_group) + '_' + str(element['id']))
        print(buf)
        attachment = ','.join(buf)
        print(type(attachment))
        print(attachment)
        return attachment
    except:
        return get_pictures(vk_session,  id_group, vk)


def get_random_audio(owner_id, vk_session, message):
	try:
		list = []
		num = random.randint(1, 100)
		huy = vk_session.method('wall.get', {'owner_id': owner_id, 'count': 1, 'offset': num})['items'][0]['attachments']
		for item in huy:
			if item['type'] == "audio":
				list.append((str(item['audio']['owner_id']) + '_' + str(item['audio']['id'])))
		qwert = random.choice(list)
		send_message(vk_session, 'peer_id', event.peer_id, message, attachment='audio' + qwert)
	except:
		logging.info("error has occurred because of offset" + str(num))
		get_random_audio(owner_id, vk_session)


for event in longpoll.listen():
	if event.type == VkEventType.MESSAGE_NEW:
		print('Время: ' + str(datetime.strftime(datetime.now(), "%H:%M:%S")))
		print('Текст человека: ' + str(event.text))
		print(event.attachments)
		response = event.text

		for item in commands:
			if item['name'] == event.text:
				# from chat
				send_message(vk_session, 'peer_id', event.peer_id, item['value'])
		if event.text.lower() == "!stone":
			send_message(vk_session, 'peer_id', event.peer_id, '🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿')

		if event.text.lower() == ".monday":
			send_message(vk_session, 'peer_id', event.peer_id, 'Понедельник: ОБЖ каб.321, Физика каб.320, Информатика каб.416, Обществознание Каб.111')
		if event.text.lower() == ".tuesday1":
			send_message(vk_session, 'peer_id', event.peer_id, 'Вторник: Физкультура, Физика каб.320, Информатика каб.416')
		if event.text.lower() == ".tuesday2":
			send_message(vk_session, 'peer_id', event.peer_id, 'Вторник: Физкультура, Физика каб.320, Информатика каб.416, Обществознание каб.111')
		if event.text.lower() == ".wednesday1":
			send_message(vk_session, 'peer_id', event.peer_id, 'Среда: Ко второй паре, Матика каб.303, Литература каб.314, Англ (Леонова) каб.315')
		if event.text.lower() == ".wednesday2":
			send_message(vk_session, 'peer_id', event.peer_id, 'Среда: Ко второй паре, Матика каб.303, Литература каб.314, ОБЖ каб.321')
		if event.text.lower() == ".thursday1":
			send_message(vk_session, 'peer_id', event.peer_id, 'Четверг: Литература Каб.314, История Каб.230, История каб.230')
		if event.text.lower() == ".thursday2":
			send_message(vk_session, 'peer_id', event.peer_id, 'Четверг: Физкультура, История каб.230, Обществознание каб.111')
		if event.text.lower() == ".friday1":
			send_message(vk_session, 'peer_id', event.peer_id, 'Пятница: Иностранный язык (Сакерина) каб.304, Матика каб.303, Английский каб.304 (Сакерина) каб.315 (Леонова), Русский каб.314')
		if event.text.lower() == ".friday2":
			send_message(vk_session, 'peer_id', event.peer_id, 'Пятница: Астрономия каб.422, Матика каб.303, Английский каб.304 (Сакерина) каб.315 (Леоновa), Русский каб.314 Каб.111')
		if event.text.lower() == ".saturday1":
			send_message(vk_session, 'peer_id', event.peer_id, 'Суббота: Матика каб.303, Химия каб.422')
		if event.text.lower() == ".saturday2":
			send_message(vk_session, 'peer_id', event.peer_id, 'Суббота: Матика каб.303, Химия каб.422, Биология каб.403, Экология каб.403')


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
			hug = [456241533, 456241532, 456241531, 456241530, 456241529, 456241528, 456241527, 456241526, 456241525, 456241524, 456241523, 456241522, 456241521, 456241520, 456241519, 456241518, 456241517, 456241516, 456241515, 456241514, 456241513, 456241512, 456241511]
			send_message(vk_session, 'peer_id', event.peer_id, attachment='audio' + str(161959141) + '_' + str(random.choice(hug)))

		if event.text.lower() == "!1канал":
			send_message(vk_session, 'peer_id', event.peer_id, attachment='audio161959141_456241503')
		if event.text.lower() == "!шашлык":
			vk_session.method('messages.send', {'peer_id': event.peer_id, 'message': 'Шашлычок ту-ту-ту-ду-ду и лучок ту-ту-ту-ду-ду\nНа природе ту-ту-ту-ду-ду, при погоде ту-ту-ту-ду-ду\nИз свинИны ту-ту-ту-ду-ду, из баранИны ту-ту-ту-ду-ду\nСлюнки текут ту-ту-ту-ду-ду, а гости ждут.', 'random_id': 0,
												"attachment": 'audio161959141_456241535'})
		if event.text.lower() == "прикалюха":
			send_message(vk_session, 'peer_id', event.peer_id, attachment='video161959141_456240830')
		if event.text.lower() == "!банан":
			send_message(vk_session, 'peer_id', event.peer_id, attachment='video210923765_456239281')
		if event.text == "!кто":
			if event.from_chat:
				vaal = random.choice((vk_session.method('messages.getChat', {'chat_id': event.chat_id}))['users'])
				send_message(vk_session, 'peer_id', event.peer_id, "@id" + str(vaal) + "(он!!!)")
		if event.text.lower() == "!gvn":
			huy = vk_session.method('video.get',{'owner_id':'-164489758', 'count':200, 'offset':1})['items']
			qwert = random.choice(list(i for i in huy))
			send_message(vk_session, 'peer_id', event.peer_id, 'Держи gvn!',attachment='video' + str(-164489758) + '_' + str(qwert['id']))
		if event.text.lower() == "!webm":
			huy = vk_session.method('video.get',{'owner_id':'-30316056', 'count':200, 'offset':1})['items']
			qwert = random.choice(list(i for i in huy))
			send_message(vk_session, 'peer_id', event.peer_id, 'Держи webm!', attachment='video' + str(-30316056) + '_' + str(qwert['id']))
		if event.text.lower() == "!mashup":
			get_random_audio(str(-39786657), vk_session, 'Держи mashup!')
		spaced_words = str(response).split(' ')
		if spaced_words[0] == "!s" and len(spaced_words) == 2:
			try:
				print(send_sticker(vk_session, int(spaced_words[1])))
			except:
				print(send_message(vk_session, 'peer_id', event.peer_id, 'Не существует этого стикера или у автора не куплен!', attachment='video161959141_456240839'))
		if event.text.lower() == "!silvagun":
			get_random_audio(str(-144211359), vk_session, 'Держи SilvaGunner!')
		spaced_words = str(response).split(' ')
		if spaced_words[0] == "!p" and len(spaced_words) == 2:
			try:
				send_message(vk_session, 'peer_id', event.peer_id, attachment='photo161959141' + '_' + str(spaced_words[1]))
			except:
				send_message(vk_session, 'peer_id', event.peer_id, attachment='video161959141_456240839')

		if event.text.lower() == ".help":
			send_message(vk_session, 'peer_id', event.peer_id, 'Расписание: .monday, .tuesday1, .tuesday2, .wednesday1, .wednesday2, .thursday1, .thursday2, .friday1, .friday2, .saturday1, .saturday2\nКартиночки: !лоличан, !murnelis, !ll\nВидео: !банан, !gvn, !webm\nМузло: !rx4d, !1канал, !mashup\nhreni: !тварь, !шанс, !шар, !кто')
		if event.text.lower() == "!тварь":
			val = random.choice((vk_session.method('messages.getChat', {'chat_id': event.chat_id}))['users'])
			send_message(vk_session, 'peer_id', event.peer_id, "@id" + str(val) + "(тварына!!!)")
		if event.text.lower() == "!everyone":
			varl = (vk_session.method('messages.getChat', {'chat_id': event.chat_id})['users'])
			send_message(vk_session, 'peer_id', event.peer_id, "[kristian5336|@bruhsoziv][id" + "[id".join(str(i) +"|\u2063]" for i in varl))
		if spaced_words[0] == '!шанс' and len(spaced_words) > 1:
			send_message(vk_session, 'peer_id', event.peer_id,
						 'Шанс того, что ' + ' '.join(spaced_words[1:]) + ' - '
														   + str(random.randint(1, 100)) + '%')
		if event.text == '!pic':
			if event.attachments['attach1_type'] == 'photo':
				id_photo = event.attachments['attach1']
				print(id_photo)
				send_message(vk_session, 'peer_id', event.peer_id, attachment='photo' + id_photo)
		if spaced_words[0] == '!шар':
			send_message(vk_session, 'peer_id', event.peer_id, 'Мой ответ - ' +
														   str(random.choice(["Да",
																			  "Нет",
																			  "Скорее всего, но это не точно",
																			  "В душе не ебу если честно",
																			  "Да, это прям 100%",
																			  "нет,ты чё шизоид?"]))+ ' ')

		""" Добавление и редактирование в список пользователей """
		if spaced_words[0] == '!regme' and len(spaced_words) == 2:
			if spaced_words[1] not in list(i['association'] for i in users):
				user_worker.insert(1, event.extra['from'], spaced_words[1])
				commands.insert(0, {
					'access_level': 1,
					'vk_id': event.extra['from'],
					'value': spaced_words[1]})
			else:
				send_message(vk_session, 'chat_id', event.chat_id, "Ассоциация занята")

		""" Добавление и удаление комманд """
        # TODO добавить уровни и контроль юзеров
        if spaced_words[0] == '!addcom' and len(spaced_words) >= 3:
            if spaced_words[1] == spaced_words[2]:
                send_message(vk_session, 'chat_id', event.chat_id, "Нельзя добавить эхо-комманду")
            elif spaced_words[1] in list(i['name'] for i in commands):
                send_message(vk_session, 'chat_id', event.chat_id, "Нельзя добавить существуюую комманду")
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
