import random
import time


def get(vk_session, id_group,vk):
    try:
        attachment = ''
        videos = vk_session.method('video.get',{'owner_id':'-164489758', 'count':10, 'offset':1})['items']
        qwert = random.choice(list(i for i in videos))
        buf = []
        for element in video:
            buf.append('video' + str(-164489758) + '_' + str(qwert['id'])) 
        print(buf)
        attachment = ','.join(buf)
        print(type(attachment))
        print(attachment)
        return attachment
    except:
        return get(vk_session, -164489758, vk)