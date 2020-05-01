import telebot
import vk_api
from StartupLoader.StartupLoader import StartupLoader
from VkBot import VkBot

config_loader = StartupLoader('config.JSON')
telega = telebot.TeleBot(config_loader.get_tel_api())
vk_session = vk_api.VkApi(token=config_loader.get_vk_token())
session_api = vk_session.get_api()
bot = VkBot(vk_session, session_api)

@telega.message_handler(content_types=['text'])
def send_text(message):
    if '!vk' in message.text:
        spaced_words = str(message.text).replace('!vk', '')
        bot.send_message('peer_id', 2000000116,message.from_user.first_name + ':' + spaced_words)
@telega.message_handler(content_types=['sticker'])
def sticker_id(message):
    print(message)
telega.polling()