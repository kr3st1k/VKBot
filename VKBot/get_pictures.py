import random


def get(vk_session, id_group, vk):

    rand_group = random.choice([0, 1])

    if int(rand_group) == 0:
        return get_group_photo(vk_session, -127518015, 'wall', vk)
    else:
        return get_group_photo(vk_session, -157516431, 'wall', vk)



def get_group_photo(vk_session, id_group, wall, vk):
    try:
        attachment = ''
        max_num = vk.photos.get(owner_id=id_group, album_id=wall, count=0)['count']
        num = random.randint(1, max_num)
        pictures = vk.photos.get(owner_id=str(id_group), album_id=wall, count=1, offset=num)['items']
        buf = []
        for element in pictures:
            buf.append('photo' + str(id_group) + '_' + str(element['id']))
        print(buf)
        attachment = ','.join(buf)
        print(type(attachment))
        print(attachment)
        return attachment
    except:

        return get(vk_session, id_group, vk)


