import vk_api
import random

vk_session = vk_api.VkApi(token="cb5793ad0a6f4ac5730a102091c70b5f512cd0ecbc65a4cba092bee967503c67eb44eb9e583b93906de00")
session_api = vk_session.get_api()

huy = vk_session.method('video.get',{'owner_id':'-164489758', 'count':10, 'offset':1})['items']

qwert = random.choice(list(i for i in huy))
print(qwert['id'])