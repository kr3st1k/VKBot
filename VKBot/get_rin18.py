import random
import time

def get(vk_session, id_group,vk):
    try:
        attachment = ''
        max_num = vk.photos.get(owner_id=-119603422, album_id='234179541', count=0)['count']
        num = random.randint(1, max_num)
        pictures = vk.photos.get(owner_id=str(-119603422), album_id='234179541', count=1, offset=num)['items']
        buf = []
        for element in pictures:
            buf.append('photo' + str(-119603422) + '_' + str(element['id']))
        print(buf)
        attachment = ','.join(buf)
        print(type(attachment))
        print(attachment)
        return attachment
    except:
        return get(vk_session, -119603422, vk)