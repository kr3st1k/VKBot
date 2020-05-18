import json
import datetime
from datetime import datetime, timedelta
from datetime import date , time, timedelta
import requests
from subprocess import Popen, PIPE
import subprocess
import vk_api
import oppadc
from StartupLoader.StartupLoader import StartupLoader
from PIL import Image, ImageDraw, ImageFont, ImageColor, ImageEnhance
import re
import numpy as np
import colorsys


config_loader = StartupLoader('config.JSON')

vk_session = vk_api.VkApi(token=config_loader.get_vk_token())
session_api = vk_session.get_api()
#TODO перенеси в main бг

class GatariApi:
    key = None
    mode = None  # TODO in DB
    api_url = 'https://api.gatari.pw'

    def __init__(self):
        self.mode = 0
    def acc(self, threehundred: int, onehundred: int, fivezero: int, miss: int):
        accur = fivezero * 50 + onehundred * 100 + threehundred * 300
        accur1 = fivezero + onehundred + threehundred + miss
        accur2 = 300 * accur1
        accur = accur / accur2
        count = len(str(accur))
        if count > 3:
            accur = accur * 100
            accur = round(float(accur), 2)
            return accur
        elif type(accur) == float:
            accur = round(float(accur))
            return accur
        return accur


    def mods(self, num):
        mods_osu = {}
        modes = []
        opt = {'HT': 256, 'NF': 1, 'Easy': 2, 'HR': 16,
               'HD': 8, 'FL': 1024, 'SO': 4096, 'TD': 4,
               'Relax': 128, 'Autoplay': 2048, 'Relax2': 8192, 'ScoreV2': 536870912}
        for key, value in opt.items():
            if value & num == value:
                mods_osu[key] = value
        num_s = 0

        for key in mods_osu:
            num_s = num_s + mods_osu[key]
        if num_s != num:
            if 576 + num_s == num:
                mods_osu['NC'] = 576
            if 32 + num_s == num:
                mods_osu['SD'] = 32
            if 64 + num_s == num:
                mods_osu['DT'] = 64
            if 16416 + num_s == num:
                mods_osu['PF'] = 16416

            if 576 + 32 + num_s == num:
                mods_osu['NC'] = 576
                mods_osu['SD'] = 32
            if 576 + 16416 + num_s == num:
                mods_osu['NC'] = 576
                mods_osu['PF'] = 16416

            if 64 + 32 + num_s == num:
                mods_osu['DT'] = 64
                mods_osu['SD'] = 32
            if 64 + 16416 + num_s == num:
                mods_osu['DT'] = 64
                mods_osu['PF'] = 16416

        if mods_osu == {}:
            mods_osu['NoMod'] = 'NoMod'

        for key in mods_osu:
            modes.append(key)

        return ''.join(modes)

    def map_osu(self, beatmap_id: str):
        pas = requests.get('https://osu.ppy.sh/osu/' + beatmap_id)
        out = open('map.osu', "wb")
        out.write(pas.content)
        out.close()

    def d_h_m(self, seconds: int):
        days = int(seconds) // 86400
        s = int(seconds) - (days * 86400)
        hours = s // 3600
        s = s - (hours * 3600)
        minutes = s // 60
        return str(days) + 'd ' + str(hours) + 'h ' +  str(minutes) + 'm'

    def get_basic_info(self, user_id: str):
        return requests.get(
            self.api_url + '/users/get?u=' + user_id).json()['users'][0]

            # TODO WTF

    def get_stats(self, user_id: str, mode: int):
        return requests.get(
            self.api_url + '/user/stats?u=' + user_id + '&mode=' + mode).json()['stats']


    def get_beatmap_by_id(self, beatmap_id: str):
        return requests.get(
            self.api_url + 'beatmaps/get?bb=' + beatmap_id).json()['data']

    def get_score_by_id(self, user_id: str, beatmap_id: str):
        return requests.get(
            self.api_url + 'get_scores?' + 'k=' + self.key + '&b=' + beatmap_id + '&u=' + user_id + '&m=' + str(
                self.mode)).json()[0]

    def top_play(self, user_id):
        res_dict = {}
        top_dict = {}
        beatmap_dict = {}
        result = requests.get(
            self.api_url + 'user/scores/best?id=' + user_id + '&mode=' + str(self.mode) + '&l=' + str(
                5)).json()['score']
        for item in result:
            beatmap_dict[f'beatmap{str(int(result.index(item)) + 1)}'] = self.get_beatmap_by_id(item['beatmap_id'])
            top_dict[f'top{str(int(result.index(item)) + 1)}'] = item
        res_dict['usermap_info'] = top_dict
        res_dict['beatmap_data'] = beatmap_dict
        return res_dict


    def osu_profile_tostring(self, profile_data: dict, stats_data: dict):
        try:
            return 'Ник: ' + profile_data['username'] + \
                   '\n' + 'Количество игр: ' + str(stats_data['playcount']) + \
                   '\n' + 'Мировой ранг: #' + str(stats_data['rank']) + \
                   '\n' + 'Ранг по стране: #' + str(stats_data['country_rank']) + \
                   '\n' + 'PP: ' + str(stats_data['pp']) + \
                   '\n' + 'Часов в игре: ' + str(int(int(stats_data['playtime']) / 3600)) + 'h' + \
                   '\n' + 'Точность: ' + str("%.2f" % float(stats_data['avg_accuracy'])) + '%' + \
                   '\n' + 'Профиль: https://osu.gatari.pw/u/' + str(profile_data['id'])

        except Exception as e:
            print(e)
            return "дурак, это кто?"
    def osu_profile_pic(self, profile_data: dict, stats_data: dict, pho: str, procent: int, color=None, bg=None):
        if bg == None:
            fff = Image.new('RGBA', (750, 220), (255, 255, 255, 0))
            jopa = ImageDraw.Draw(fff)
            jopa.rectangle(((0, 0) + (749, 162)), fill=(43, 34, 37, 255))
            fff.save('pillowstuff/background.png')
            bgg = Image.open('/home/ubuntu/VKBot/VKBot/pillowstuff/background.png').convert('RGBA')
        if bg != None:
            per = procent / 100
            if '.jpg' in bg or '.jpeg' in bg:
                pas = requests.get(bg)
                out = open('pillowstuff/background.jpg', "wb")
                out.write(pas.content)
                out.close()
                ds = Image.open('/home/ubuntu/VKBot/VKBot/pillowstuff/background.jpg').convert('RGBA')
                width, height = ds.size
                if per != 1:
                    heightt = int(float(height) * float(per))
                    mm = ds.crop((0, heightt, width, height - heightt))
                    mm.save('pillowstuff/backkground.png')
                else:
                    mm = ds.crop((0, 0, width, height / 2))
                    mm.save('pillowstuff/backkground.png')

            if '.png' in bg:
                pas = requests.get(bg)
                out = open('pillowstuff/background.png', "wb")
                out.write(pas.content)
                out.close()
                ds = Image.open('/home/ubuntu/VKBot/VKBot/pillowstuff/background.jpg').convert('RGBA')
                width, height = ds.size
                if per != 1:
                    heightt = int(float(height) * float(per))
                    mm = ds.crop((0, heightt, width, height - heightt))
                    mm.save('pillowstuff/backkground.png')
                else:
                    mm = ds.crop((0, 0, width, height / 2))
                    mm.save('pillowstuff/backkground.png')
            ds = Image.open('/home/ubuntu/VKBot/VKBot/pillowstuff/backkground.png').convert('RGBA')
            width, height = ds.size
            shis = ds.crop(((width / 2) - 375, 0, (width / 2) + 375, height / 2))
            shish = shis.resize((750, 220))
            enhacer = ImageEnhance.Brightness(shish)
            output = enhacer.enhance(0.5)
            out = Image.alpha_composite(shish, output)
            out.save('pillowstuff/background.png')
            bgg = Image.open('/home/ubuntu/VKBot/VKBot/pillowstuff/background.png').convert('RGBA')
            base = Image.open('/home/ubuntu/VKBot/VKBot/pillowstuff/profilenobg.png').convert('RGBA')
            out = Image.alpha_composite(bgg, base)
            out.save('pillowstuff/profilebg.png')
        base = Image.open('/home/ubuntu/VKBot/VKBot/pillowstuff/profilenobg.png').convert('RGBA')
        out = Image.alpha_composite(bgg, base)
        out.save('pillowstuff/profilebg.png')
        base = Image.open('/home/ubuntu/VKBot/VKBot/pillowstuff/profilebg.png').convert('RGBA')
        flag = 'https://osu.gatari.pw/static/images/flags/' + str(profile_data['country']) + '.png'
        pas = requests.get(flag)
        out = open('pillowstuff/flag.png', "wb")
        out.write(pas.content)
        out.close()
        try:
            flag = Image.open('/home/ubuntu/VKBot/VKBot/pillowstuff/flag.png')
            flagg = flag.resize((35, 23))
            flagg.save('pillowstuff/flag.png')
            flag = Image.open('/home/ubuntu/VKBot/VKBot/pillowstuff/flag.png')
        except:
            flag = Image.open('/home/ubuntu/VKBot/VKBot/pillowstuff/AQ.png')
            flagg = flag.resize((35, 23))
            flagg.save('pillowstuff/flag.png')
            flag = Image.open('/home/ubuntu/VKBot/VKBot/pillowstuff/AQ.png')
        pas = requests.get('https://a.gatari.pw/' + str(profile_data['id']))
        out = open('pillowstuff/avatarka.jpg', "wb")
        out.write(pas.content)
        out.close()
        txt = Image.new('RGBA', base.size, (255, 255, 255, 0))
        fnt = ImageFont.truetype('/home/ubuntu/VKBot/VKBot/pillowstuff/Torus-Regular.otf', 16)
        tnf = ImageFont.truetype('/home/ubuntu/VKBot/VKBot/pillowstuff/Torus-Regular.otf', 19)
        avaF = Image.open('pillowstuff/avatarka.jpg').convert('RGBA')
        avaFr = avaF.resize((128, 128), Image.ANTIALIAS)
        avaFr.save('pillowstuff/ava.png')
        im = Image.open('pillowstuff/ava.png')
        circle = Image.new('L', (35 * 2, 35 * 2), 0)
        draw = ImageDraw.Draw(circle)
        draw.ellipse((0, 0, 35 * 2, 35 * 2), fill=255)
        alpha = Image.new('L', im.size, 255)
        w, h = im.size
        alpha.paste(circle.crop((0, 0, 35, 35)), (0, 0))
        alpha.paste(circle.crop((0, 35, 35, 35 * 2)), (0, h - 35))
        alpha.paste(circle.crop((35, 0, 35 * 2, 35)), (w - 35, 0))
        alpha.paste(circle.crop((35, 35, 35 * 2, 35 * 2)), (w - 35, h - 35))
        im.putalpha(alpha)
        im.save('pillowstuff/ava.png')
        ava = Image.open('pillowstuff/ava.png')
        d = ImageDraw.Draw(txt)
        txt.paste(base, (0, 0))
        txt.paste(ava, (20, 20))
        txt.paste(flag, (160, 90))
        year1 = datetime.fromtimestamp(profile_data['registered_on'])
        year = year1.strftime('%Y')
        now = datetime.now()
        if str(int(now.year) - int(year)) == 1:
            xtt = ' year ago'
        else:
            xtt = ' years ago'
        d.multiline_text((160, 58), str(profile_data['username']), font=tnf, fill=(255, 255, 255, 255))
        d.multiline_text((200, 90), 'Joined ' + str(int(now.year) - int(year)) + xtt, font=tnf,
                         fill=(255, 255, 255, 255))
        width = d.multiline_textsize(re.sub(r"\B(?=(\d{3})+(?!\d))", ',', str(stats_data['playcount'])),
                                     font=(ImageFont.truetype('/home/ubuntu/VKBot/VKBot/pillowstuff/Torus.otf', 13)))
        d.multiline_text((741 - width[0], 5), re.sub(r"\B(?=(\d{3})+(?!\d))", ',', str(stats_data['playcount'])),
                         font=(ImageFont.truetype('/home/ubuntu/VKBot/VKBot/pillowstuff/Torus.otf', 13)), fill=(255, 255, 255, 255))
        width = d.multiline_textsize(re.sub(r"\B(?=(\d{3})+(?!\d))", ',', str(stats_data['ranked_score'])),
                                     font=(ImageFont.truetype('/home/ubuntu/VKBot/VKBot/pillowstuff/Torus.otf', 13)))
        d.multiline_text((741 - width[0], 32), re.sub(r"\B(?=(\d{3})+(?!\d))", ',', str(stats_data['ranked_score'])),
                         font=(ImageFont.truetype('/home/ubuntu/VKBot/VKBot/pillowstuff/Torus.otf', 13)), fill=(255, 255, 255, 255))
        width = d.multiline_textsize(re.sub(r"\B(?=(\d{3})+(?!\d))", ',', str(stats_data['total_score'])),
                                     font=(ImageFont.truetype('/home/ubuntu/VKBot/VKBot/pillowstuff/Torus.otf', 13)))
        d.multiline_text((741 - width[0], 58), re.sub(r"\B(?=(\d{3})+(?!\d))", ',', str(stats_data['total_score'])),
                         font=(ImageFont.truetype('/home/ubuntu/VKBot/VKBot/pillowstuff/Torus.otf', 13)), fill=(255, 255, 255, 255))
        width = d.multiline_textsize(str("%.2f" % float(stats_data['avg_accuracy'])) + '%',
                                     font=(ImageFont.truetype('/home/ubuntu/VKBot/VKBot/pillowstuff/Torus.otf', 13)))
        d.multiline_text((741 - width[0], 85), str("%.2f" % float(stats_data['avg_accuracy'])) + '%',
                         font=(ImageFont.truetype('/home/ubuntu/VKBot/VKBot/pillowstuff/Torus.otf', 13)), fill=(255, 255, 255, 255))
        profile_data['level'] = str(stats_data['level']) + '.' + str(stats_data['level_progress'])
        huh = str(profile_data['level']).split('.')
        levelxp = (float(float("%.2f" % float(profile_data['level'])) - float(huh[0])) * 100)
        coord = float(2.32) * levelxp
        d.rectangle((509, 138) + (741, 141), fill=(0, 0, 0, 255))
        if color != None:
            d.rectangle((509, 138) + (509 + coord, 141), fill='hsb(' + str(color) + ',100%,100%)')
            d.rectangle((20, 173) + (103, 174), fill='hsb(' + str(color) + ',100%,100%)')
            d.rectangle((156, 83) + (331, 84), fill='hsb(' + str(color) + ',100%,100%)')
            d.rectangle((533, 173) + (616, 174), fill='hsb(' + str(color) + ',100%,100%)')
            d.rectangle((650, 173) + (742, 174), fill='hsb(' + str(color) + ',100%,100%)')
        if color == None:
            d.rectangle((509, 138) + (509 + coord, 141), fill=(200, 154, 167, 255))
            d.rectangle((20, 173) + (103, 174), fill=(201, 153, 167, 255))
            d.rectangle((156, 83) + (331, 84), fill=(201, 153, 167, 255))
            d.rectangle((533, 173) + (616, 174), fill=(201, 153, 167, 255))
            d.rectangle((650, 173) + (742, 174), fill=(201, 153, 167, 255))
        width = d.multiline_textsize(str("%.0f" % float(huh[0])),
                                     font=(ImageFont.truetype('/home/ubuntu/VKBot/VKBot/pillowstuff/Torus.otf', 13)))
        d.multiline_text((741 - width[0], 112), str("%.0f" % float(huh[0])),
                         font=(ImageFont.truetype('/home/ubuntu/VKBot/VKBot/pillowstuff/Torus.otf', 13)), fill=(255, 255, 255, 255))
        width = d.multiline_textsize(str("%.0f" % float(levelxp)) + '%',
                                     font=(ImageFont.truetype('/home/ubuntu/VKBot/VKBot/pillowstuff/Torus.otf', 10)))
        d.multiline_text((741 - width[0], 142), str("%.0f" % float(levelxp)) + '%', align="right",
                         font=(ImageFont.truetype('/home/ubuntu/VKBot/VKBot/pillowstuff/Torus.otf', 10)), fill=(255, 255, 255, 255))
        d.multiline_text((20, 190), str(self.d_h_m(stats_data['playtime'])), font=fnt,
                         fill=(255, 255, 255, 255))
        d.multiline_text((142, 190), re.sub(r"\B(?=(\d{3})+(?!\d))", ',', str(stats_data['pp'])), font=fnt, fill=(255, 255, 255, 255))
        d.multiline_text((533, 190), re.sub(r"\B(?=(\d{3})+(?!\d))", ',', str('#' + str(stats_data['rank']))), font=fnt,
                         fill=(255, 255, 255, 255))
        d.multiline_text((650, 190), re.sub(r"\B(?=(\d{3})+(?!\d))", ',', str('#' + str(stats_data['country_rank']))),
                         font=fnt, fill=(255, 255, 255, 255))
        width = d.multiline_textsize(str(stats_data['xh_count']), font=fnt)
        width = (281 - 253 - width[0]) / 2
        d.multiline_text([width + 253, 197], str(stats_data['xh_count']), font=fnt,
                         fill=(255, 255, 255, 255))
        width = d.multiline_textsize(str(stats_data['x_count']), font=fnt)
        width = (332 - 304 - width[0]) / 2
        d.multiline_text([width + 304, 197], str(stats_data['x_count']), font=fnt,
                         fill=(255, 255, 255, 255))
        width = d.multiline_textsize(str(stats_data['sh_count']), font=fnt)
        width = (382 - 354 - width[0]) / 2
        d.multiline_text([width + 354, 197], str(stats_data['sh_count']), font=fnt,
                         fill=(255, 255, 255, 255))
        width = d.multiline_textsize(str(stats_data['s_count']), font=fnt)
        width = (433 - 405 - width[0]) / 2
        d.multiline_text([width + 405, 197], str(stats_data['s_count']), font=fnt,
                         fill=(255, 255, 255, 255))
        width = d.multiline_textsize(str(stats_data['a_count']), font=fnt)
        width = (483 - 455 - width[0]) / 2
        d.multiline_text([width + 455, 197], str(stats_data['a_count']), font=fnt,
                         fill=(255, 255, 255, 255))
        out = Image.alpha_composite(base, txt)
        out.save('pillowstuff/profileee.png')
        if pho == 1:
            url = vk_session.method('photos.getMessagesUploadServer', {'peer_id': 595719899})
            file = open('pillowstuff/profileee.png', 'rb')
            files = {'photo': file}
            nani = requests.post(url['upload_url'], files=files)
            result = json.loads(nani.text)
            hell = vk_session.method('photos.saveMessagesPhoto',
                                     {'photo': result['photo'], 'server': result["server"], 'hash': result['hash']})
            return 'photo' + str(hell[0]['owner_id']) + '_' + str(hell[0]['id'])
        if pho == 2:
            url = vk_session.method("docs.getMessagesUploadServer", {
                'peer_id': 595719899,
                'type': 'graffiti'})
            file = [('file', ('pillowstuff/profileee.png', open('pillowstuff/profileee.png', 'rb')))]
            nani = requests.post(url['upload_url'], files=file)
            result = json.loads(nani.text)
            print(result)
            hell = vk_session.method('docs.save',
                                     {'file': result['file']})
            return 'graffiti' + str(hell['graffiti']['owner_id']) + '_' + str(hell['graffiti']['id'])
gatari_session = GatariApi()
print(gatari_session.get_basic_info('kr3st1k'))
print(gatari_session.get_stats('kr3st1k', str(0)))