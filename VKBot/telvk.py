import telebot
import vk_api
from StartupLoader.StartupLoader import StartupLoader
from VkBot import VkBot

config_loader = StartupLoader('config.JSON')
telega = telebot.TeleBot(config_loader.get_tel_api())
vk_session = vk_api.VkApi(token=config_loader.get_vk_token())
session_api = vk_session.get_api()
admin_id_int = config_loader.get_admin_id()
bot = VkBot(vk_session, session_api, admin_id_int)

@telega.message_handler(content_types=['text'])
def send_text(message):
    spaced_words = str(message.text)
    bot.send_message('peer_id', 2000000001,'Telegram\n' + message.from_user.first_name + ': ' + spaced_words)
@telega.message_handler(content_types=['sticker'])
def sticker_id(message):
    print(message)
telega.polling()