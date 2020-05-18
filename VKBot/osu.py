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

def get_osu_token():
    return config_loader.get_osu_token()


class Osu:
    key = None
    mode = None  # TODO in DB

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
    def status(self, value: int):
        if value == 0:
            return '(Pending)'
        if value == 1:
            return '(Ranked)'
        if value == 2:
            return '(Approved)'
        if value == 3:
            return '(Qualified)'
        if value == 4:
            return '(Loved)'
        if value == -1:
            return '(WIP)'
        if value == -2:
            return '(Graveyard)'

    def map_osu(self, beatmap_id: str):
        pas = requests.get('https://osu.ppy.sh/osu/' + beatmap_id)
        out = open('map.osu', "wb")
        out.write(pas.content)
        out.close()

    def perfectpp(self, beatmap_id: str, modss):
        if modss == 0:
            try:
                shish = requests.get('https://osu.gatari.pw/api/v1/pp?b=' + beatmap_id + '&a=100').json()
                return str(round(shish['pp'][0], 1))
            except:
                self.map_osu(beatmap_id)
                Map = oppadc.OsuMap(file_path='map.osu')
                PP = Map.getPP()
                print(round(PP.total_pp, 1))
                return round(PP.total_pp, 1)
        else:
            try:
                shish = requests.get('https://osu.gatari.pw/api/v1/pp?b=' + beatmap_id + '&a=100&m=' + modss).json()
                return str(round(shish['pp'][0], 1))
            except:
                mods = self.mods(int(modss))
                self.map_osu(beatmap_id)
                Map = oppadc.OsuMap(file_path='map.osu')
                PP = Map.getPP(mods)
                print(round(PP.total_pp, 1))
                return round(PP.total_pp, 1)
    def diff(self, beatmap_id: str, mods: None):
        if mods == None:
            self.map_osu(beatmap_id)
            Map = oppadc.OsuMap(file_path='map.osu')
            Stats = Map.getStats()
            return str(round(Stats.total, 2))
        else:
            self.map_osu(beatmap_id)
            Map = oppadc.OsuMap(file_path='map.osu')
            Stats = Map.getStats(mods)
            return str(round(Stats.total, 2))

    def info_diff_mod(self, beatmap_id: str, mods):
        self.map_osu(beatmap_id)
        Map = oppadc.OsuMap(file_path='map.osu')
        PP = Map.getPP(mods)
        Stats = Map.getStats()
        Diff = Map.getDifficulty()
        return Diff

    def pippi(self, beatmap_id: str, n300: int, n100: int, n50: int, miss: int, combo: int, mods):
        if mods == 0:
            try:
                acc = self.acc(n300, n100, n50, miss)
                shish = requests.get('https://osu.gatari.pw/api/v1/pp?b=' + beatmap_id + '&a='+ str(acc) +'&x=' + str(miss) + '&c=' + str(combo)).json()
                return str(round(shish['pp'][0], 1))
            except:
                self.map_osu(beatmap_id)
                Map = oppadc.OsuMap(file_path='map.osu')
                PP = Map.getPP(n300=n300, n100=n100, n50=n50, misses=miss, combo=combo)
                print(round(PP.total_pp, 1))
                return round(PP.total_pp, 1)
        else:
            try:
                acc = self.acc(n300, n100, n50, miss)
                shish = requests.get('https://osu.gatari.pw/api/v1/pp?b=' + beatmap_id + '&a=' + str(acc) + '&x=' + str(miss) + '&c=' + str(combo) + '&m=' + mods).json()
                return str(round(shish['pp'][0], 1))
            except:
                modss = self.mods(int(modss))
                self.map_osu(beatmap_id)
                Map = oppadc.OsuMap(file_path='map.osu')
                PP = Map.getPP(modss, n300=n300, n100=n100, n50=n50, misses=miss, combo=combo)
                print(round(PP.total_pp, 1))
                return round(PP.total_pp, 1)

    def fullpp(self, beatmap_id: str, n300: int, n100: int, n50: int, mods):
        if mods == 0:
            try:
                acc = self.acc(n300, n100, n50, 0)
                shish = requests.get('https://osu.gatari.pw/api/v1/pp?b=' + beatmap_id + '&a=' + str(acc)).json()
                return str(round(shish['pp'][0], 1))
            except:
                self.map_osu(beatmap_id)
                Map = oppadc.OsuMap(file_path='map.osu')
                PP = Map.getPP(n300=n300, n100=n100, n50=n50)
                print(round(PP.total_pp, 1))
                return round(PP.total_pp, 1)
        else:
            try:
                acc = self.acc(n300, n100, n50, 0)
                shish = requests.get('https://osu.gatari.pw/api/v1/pp?b=' + beatmap_id + '&a=' + str(acc) + '&m=' + mods).json()
                return str(round(shish['pp'][0], 1))
            except:
                modss = self.mods(int(modss))
                self.map_osu(beatmap_id)
                Map = oppadc.OsuMap(file_path='map.osu')
                PP = Map.getPP(modss, n300=n300, n100=n100, n50=n50)
                print(round(PP.total_pp, 1))
                return round(PP.total_pp, 1)

    def get_bg(self, beatmap_data: dict):
        pic = 'https://assets.ppy.sh/beatmaps/{0}/covers/cover.jpg'.format(str(beatmap_data['beatmapset_id']))
        url = vk_session.method('photos.getMessagesUploadServer', {'peer_id': 161959141})
        pas = requests.get(pic)
        out = open('photo.jpg', "wb")
        out.write(pas.content)
        out.close()
        file = open('photo.jpg', 'rb')
        files = {'photo': file}
        nani = requests.post(url['upload_url'], files=files)
        result = json.loads(nani.text)
        hell = vk_session.method('photos.saveMessagesPhoto',
                                 {'photo': result['photo'], 'server': result["server"], 'hash': result['hash']})
        return 'photo' + str(hell[0]['owner_id']) + '_' + str(hell[0]['id'])

    def get_bg_rec(self, user_id: str):
        try:
            pic = 'https://assets.ppy.sh/beatmaps/{0}/covers/cover.jpg'.format(str(self.get_id_by_recent(user_id)['beatmapset_id']))
            url = vk_session.method('photos.getMessagesUploadServer', {'peer_id': 161959141})
            pas = requests.get(pic)
            out = open('rec.jpg', "wb")
            out.write(pas.content)
            out.close()
            file = open('rec.jpg', 'rb')
            files = {'photo': file}
            nani = requests.post(url['upload_url'], files=files)
            result = json.loads(nani.text)
            hell = vk_session.method('photos.saveMessagesPhoto',
                                     {'photo': result['photo'], 'server': result["server"], 'hash': result['hash']})
            return 'photo' + str(hell[0]['owner_id']) + '_' + str(hell[0]['id'])
        except:
            return 'video161959141_456240839'

    def d_h_m(self, seconds: int):
        days = int(seconds) // 86400
        s = int(seconds) - (days * 86400)
        hours = s // 3600
        s = s - (hours * 3600)
        minutes = s // 60
        return str(days) + 'd ' + str(hours) + 'h ' +  str(minutes) + 'm'

    def osu_profile_tostring(self, profile_data: dict, stats_data: dict = None,server: str = None):
        if server == 'gatari':
            profile_data['pp_rank'] = int(stats_data['rank'])
            profile_data['pp_country_rank'] = stats_data['country_rank']
            profile_data['pp_raw'] = stats_data['pp']
            profile_data['playcount'] = stats_data['playcount']
            profile_data['total_seconds_played'] = stats_data['playtime']
            profile_data['accuracy'] = stats_data['avg_accuracy']
            profile_data['links'] = '\n' + 'Профиль: https://osu.gatari.pw/u/' + str(profile_data['id'])
        if server != 'gatari':
            profile_data['links'] = '\n' + 'Профиль: https://osu.ppy.sh/u/' + str(profile_data['user_id']) + \
            '\n' + 'osu!Skills: http://osuskills.com/user/' + profile_data['username']
        try:
            pp = str(profile_data['pp_raw']).split(".")
            if len(pp) == 2:
                rawpp = int(pp[0])
                if float(pp[1]) > 0.5:
                    rawpp + 1
            else:
                rawpp = int(pp[0])
            return 'Ник: ' + profile_data['username'] + \
                   '\n' + 'Количество игр: ' + str(profile_data['playcount']) + \
                   '\n' + 'Мировой ранг: #' + str(profile_data['pp_rank']) + \
                   '\n' + 'Ранг по стране: #' + str(profile_data['pp_country_rank']) + \
                   '\n' + 'PP: ' + str(rawpp) + \
                   '\n' + 'Часов в игре: ' + str(int(int(profile_data['total_seconds_played']) / 3600)) + 'h' + \
                   '\n' + 'Точность: ' + str("%.2f" % float(profile_data['accuracy'])) + '%' + \
                   profile_data['links']

        except Exception as e:
            print(e)
            return "дурак, это кто?"
    def osu_profile_pic(self, profile_data: dict, pho: str, procent: int, color= None, bg= None):
        pp = profile_data['pp_raw'].split(".")
        if len(pp) == 2:
            rawpp = int(pp[0])
            if float(pp[1]) > 0.5:
                rawpp + 1
        else:
            rawpp = int(pp[0])
        if bg == None:
            fff = Image.new('RGBA', (750, 220), (255, 255, 255, 0))
            jopa = ImageDraw.Draw(fff)
            jopa.rectangle(((0, 0) + (749, 162)), fill=(43, 34, 37, 255))
            fff.save('background.png')
            bgg = Image.open('/home/ubuntu/VKBot/VKBot/background.png').convert('RGBA')
        if bg != None:
            per = procent / 100
            if '.jpg' in bg or '.jpeg' in bg:
                pas = requests.get(bg)
                out = open('background.jpg', "wb")
                out.write(pas.content)
                out.close()
                ds = Image.open('/home/ubuntu/VKBot/VKBot/background.jpg').convert('RGBA')
                width, height = ds.size
                if per != 1:
                    heightt = int(float(height) * float(per))
                    mm = ds.crop((0, heightt, width, height - heightt))
                    mm.save('backkground.png')
                else:
                    mm = ds.crop((0, 0, width, height / 2))
                    mm.save('backkground.png')
                    
            if '.png' in bg:
                pas = requests.get(bg)
                out = open('background.png', "wb")
                out.write(pas.content)
                out.close()
                ds = Image.open('/home/ubuntu/VKBot/VKBot/background.jpg').convert('RGBA')
                width, height = ds.size
                if per != 1:
                    heightt = int(float(height) * float(per))
                    mm = ds.crop((0, heightt, width, height - heightt))
                    mm.save('backkground.png')
                else:
                    mm = ds.crop((0, 0, width, height / 2))
                    mm.save('backkground.png')
            ds = Image.open('/home/ubuntu/VKBot/VKBot/backkground.png').convert('RGBA')
            width, height = ds.size
            shis = ds.crop(((width / 2) - 375, 0, (width / 2) + 375, height / 2))
            shish = shis.resize((750, 220))
            enhacer = ImageEnhance.Brightness(shish)
            output = enhacer.enhance(0.5)
            out = Image.alpha_composite(shish, output)
            out.save('background.png')
            bgg = Image.open('/home/ubuntu/VKBot/VKBot/background.png').convert('RGBA')
            base = Image.open('/home/ubuntu/VKBot/VKBot/profilenobg.png').convert('RGBA')
            out = Image.alpha_composite(bgg, base)
            out.save('profilebg.png')
        base = Image.open('/home/ubuntu/VKBot/VKBot/profilenobg.png').convert('RGBA')
        out = Image.alpha_composite(bgg, base)
        out.save('profilebg.png')
        base = Image.open('/home/ubuntu/VKBot/VKBot/profilebg.png').convert('RGBA')
        flag = 'https://osu.ppy.sh/images/flags/' + str(profile_data['country']) + '.png'
        pas = requests.get(flag)
        out = open('flag.png', "wb")
        out.write(pas.content)
        out.close()
        try:
            flag = Image.open('/home/ubuntu/VKBot/VKBot/flag.png')
            flagg = flag.resize((35, 23))
            flagg.save('flag.png')
            flag = Image.open('/home/ubuntu/VKBot/VKBot/flag.png')
        except:
            flag = Image.open('/home/ubuntu/VKBot/VKBot/AQ.png')
            flagg = flag.resize((35, 23))
            flagg.save('flag.png')
            flag = Image.open('/home/ubuntu/VKBot/VKBot/AQ.png')
        pas = requests.get('https://a.ppy.sh/' + str(profile_data['user_id']))
        out = open('avatarka.jpg', "wb")
        out.write(pas.content)
        out.close()
        txt = Image.new('RGBA', base.size, (255, 255, 255, 0))
        fnt = ImageFont.truetype('/home/ubuntu/VKBot/VKBot/Torus-Regular.otf', 16)
        tnf = ImageFont.truetype('/home/ubuntu/VKBot/VKBot/Torus-Regular.otf', 19)
        avaF = Image.open('avatarka.jpg').convert('RGBA')
        avaFr = avaF.resize((128, 128), Image.ANTIALIAS)
        avaFr.save('ava.png')
        im = Image.open('ava.png')
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
        im.save('ava.png')
        ava = Image.open('ava.png')
        d = ImageDraw.Draw(txt)
        txt.paste(base, (0, 0))
        txt.paste(ava, (20, 20))
        txt.paste(flag, (160, 90))
        year = list(str(profile_data['join_date']).split('-')[:1])
        now = datetime.now()
        if str(int(now.year) - int(year[0])) == 1:
            xtt = ' year ago'
        else:
            xtt = ' years ago'
        d.multiline_text((160,58), str(profile_data['username']) , font=tnf, fill=(255, 255, 255, 255))
        d.multiline_text((200, 90), 'Joined '+ str(int(now.year) - int(year[0])) + xtt, font=tnf, fill=(255, 255, 255, 255))
        width = d.multiline_textsize(re.sub(r"\B(?=(\d{3})+(?!\d))", ',', str(profile_data['playcount'])), font=(ImageFont.truetype('/home/ubuntu/VKBot/VKBot/Torus.otf', 13)))
        d.multiline_text((741 - width[0], 5), re.sub(r"\B(?=(\d{3})+(?!\d))", ',', str(profile_data['playcount'])),
                         font=(ImageFont.truetype('/home/ubuntu/VKBot/VKBot/Torus.otf', 13)), fill=(255, 255, 255, 255))
        width = d.multiline_textsize(re.sub(r"\B(?=(\d{3})+(?!\d))", ',', str(profile_data['ranked_score'])), font=(ImageFont.truetype('/home/ubuntu/VKBot/VKBot/Torus.otf', 13)))
        d.multiline_text((741 - width[0], 32), re.sub(r"\B(?=(\d{3})+(?!\d))", ',', str(profile_data['ranked_score'])),
                         font=(ImageFont.truetype('/home/ubuntu/VKBot/VKBot/Torus.otf', 13)), fill=(255, 255, 255, 255))
        width = d.multiline_textsize(re.sub(r"\B(?=(\d{3})+(?!\d))", ',', str(profile_data['total_score'])), font=(ImageFont.truetype('/home/ubuntu/VKBot/VKBot/Torus.otf', 13)))
        d.multiline_text((741 - width[0], 58), re.sub(r"\B(?=(\d{3})+(?!\d))", ',', str(profile_data['total_score'])),
                         font=(ImageFont.truetype('/home/ubuntu/VKBot/VKBot/Torus.otf', 13)), fill=(255, 255, 255, 255))
        width = d.multiline_textsize(str("%.2f" % float(profile_data['accuracy'])) + '%', font=(ImageFont.truetype('/home/ubuntu/VKBot/VKBot/Torus.otf', 13)))
        d.multiline_text((741 - width[0], 85), str("%.2f" % float(profile_data['accuracy'])) + '%',
                         font=(ImageFont.truetype('/home/ubuntu/VKBot/VKBot/Torus.otf', 13)), fill=(255, 255, 255, 255))
        huh = str(profile_data['level']).split('.')
        levelxp = (float(float("%.2f" % float(profile_data['level'])) - float(huh[0])) * 100)
        coord = float(2.32) * levelxp
        d.rectangle((509, 138) + (741, 141), fill=(0, 0, 0, 255))
        if color != None:
            d.rectangle((509, 138) + (509 + coord, 141), fill='hsb('+ str(color) + ',100%,100%)')
            d.rectangle((20, 173) + (103,174), fill='hsb('+ str(color) + ',100%,100%)')
            d.rectangle((156, 83) + (331,84), fill='hsb('+ str(color) + ',100%,100%)')
            d.rectangle((533, 173) + (616, 174), fill='hsb('+ str(color) + ',100%,100%)')
            d.rectangle((650, 173) + (742, 174), fill='hsb('+ str(color) + ',100%,100%)')
        if color == None:
            d.rectangle((509, 138) + (509 + coord, 141), fill=(200, 154, 167, 255))
            d.rectangle((20, 173) + (103, 174), fill=(201, 153, 167, 255))
            d.rectangle((156, 83) + (331,84), fill=(201, 153, 167, 255))
            d.rectangle((533, 173) + (616, 174), fill=(201, 153, 167, 255))
            d.rectangle((650, 173) + (742, 174), fill=(201, 153, 167, 255))
        width = d.multiline_textsize(str("%.0f" % float(huh[0])), font=(ImageFont.truetype('/home/ubuntu/VKBot/VKBot/Torus.otf', 13)))
        d.multiline_text((741 - width[0], 112), str("%.0f" % float(huh[0])),
                         font=(ImageFont.truetype('/home/ubuntu/VKBot/VKBot/Torus.otf', 13)), fill=(255, 255, 255, 255))
        d.multiline_text((727, 142), str("%.0f" % float(levelxp)) + '%', align="right",
                         font=(ImageFont.truetype('/home/ubuntu/VKBot/VKBot/Torus.otf', 10)), fill=(255, 255, 255, 255))
        total_time = self.d_h_m(profile_data['total_seconds_played'])
        d.multiline_text((20, 190),str(total_time),font=fnt,
               fill=(255, 255, 255, 255))
        d.multiline_text((142, 190), re.sub(r"\B(?=(\d{3})+(?!\d))", ',', str(rawpp)), font=fnt, fill=(255, 255, 255, 255))
        d.multiline_text((533, 190), re.sub(r"\B(?=(\d{3})+(?!\d))", ',', str('#' +profile_data['pp_rank'])), font=fnt, fill=(255, 255, 255, 255))
        d.multiline_text((650, 190), re.sub(r"\B(?=(\d{3})+(?!\d))", ',', str('#' +profile_data['pp_country_rank'])), font=fnt, fill=(255, 255, 255, 255))
        width = d.multiline_textsize(str(profile_data['count_rank_ssh']), font=fnt)
        width = (281 - 253 - width[0]) / 2
        d.multiline_text([width + 253, 197], str(profile_data['count_rank_ssh']), font=fnt,
                         fill=(255, 255, 255, 255))
        width = d.multiline_textsize(str(profile_data['count_rank_ss']), font=fnt)
        width = (332 - 304 - width[0]) / 2
        d.multiline_text([width + 304, 197], str(profile_data['count_rank_ss']),font=fnt,
                         fill=(255, 255, 255, 255))
        width = d.multiline_textsize(str(profile_data['count_rank_sh']), font=fnt)
        width = (382 - 354 - width[0]) / 2
        d.multiline_text([width + 354, 197], str(profile_data['count_rank_sh']), font=fnt,
                         fill=(255, 255, 255, 255))
        width = d.multiline_textsize(str(profile_data['count_rank_s']), font=fnt)
        width = (433 - 405 - width[0]) / 2
        d.multiline_text([width + 405, 197], str(profile_data['count_rank_s']), font=fnt,
                         fill=(255, 255, 255, 255))
        width = d.multiline_textsize(str(profile_data['count_rank_a']), font=fnt)
        width = (483 - 455 - width[0]) / 2
        d.multiline_text([width + 455, 197], str(profile_data['count_rank_a']), font=fnt,
                         fill=(255, 255, 255, 255))
        out = Image.alpha_composite(base, txt)
        out.save('profileee.png')
        if pho == 1:
            url = vk_session.method('photos.getMessagesUploadServer', {'peer_id': 595719899})
            file = open('profileee.png', 'rb')
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
            file = [('file', ('profileee.png', open('profileee.png', 'rb')))]
            nani = requests.post(url['upload_url'], files=file)
            result = json.loads(nani.text)
            print(result)
            hell = vk_session.method('docs.save',
                                  {'file': result['file']})
            return 'graffiti' + str(hell['graffiti']['owner_id']) + '_' + str(hell['graffiti']['id'])

    def beatmap_get_send(self, beatmap_data: dict):
        shish = requests.get('https://osu.gatari.pw/api/v1/pp?b=' + beatmap_data['beatmap_id']).json()
        status = self.status(int(beatmap_data['approved']))
        try:
            info = beatmap_data['artist'] + ' - ' + beatmap_data['title'] + \
                   ' [' + beatmap_data['version'] + ']' + ' by ' + beatmap_data['creator'] + ' ' + status + \
                   '\n' + 'Комбо: ' + beatmap_data['max_combo'] + \
                   '\n' + 'Длительность: ' + str(int(beatmap_data['hit_length']) // 60) + ':' + str(int(beatmap_data['hit_length']) % 60) + \
                   '\n' + '100% - ' +  str(round(shish['pp'][0], 1)) + ' | 99% - ' + str(round(shish['pp'][1], 1)) + \
                   '\n' + '98% - ' + str(round(shish['pp'][2], 1)) +' | 95% - ' + str(round(shish['pp'][3], 1)) + \
                   '\n' + 'AR ' + beatmap_data['diff_approach'] + ' | OD ' + beatmap_data['diff_overall'] + \
                   ' | HP ' + beatmap_data['diff_drain'] + ' | CS ' + beatmap_data["diff_size"] + ' | BPM ' + str(
                "%.0f" % float(beatmap_data["bpm"])) + ' | ' + str("%.2f" % float(beatmap_data['difficultyrating'])) + '*'
        except:
            info = beatmap_data['artist'] + ' - ' + beatmap_data['title'] + \
                   ' [' + beatmap_data['version'] + ']' + ' by ' + beatmap_data['creator'] + ' ' + status + \
                   '\n' + 'Комбо: ' + beatmap_data['max_combo'] + \
                   '\n' + 'Длительность: ' + str(int(beatmap_data['hit_length']) // 60) + ':' + str(
                int(beatmap_data['hit_length']) % 60) + \
                   '\n' + '100% - ' + str(self.perfectpp(str(beatmap_data['beatmap_id']), 0)) + \
                   '\n' + 'AR ' + beatmap_data['diff_approach'] + ' | OD ' + beatmap_data['diff_overall'] + \
                   ' | HP ' + beatmap_data['diff_drain'] + ' | CS ' + beatmap_data["diff_size"] + ' | BPM ' + str(
                "%.0f" % float(beatmap_data["bpm"])) + ' | ' + str(
                "%.2f" % float(beatmap_data['difficultyrating'])) + '*'
        return info
    # TODO PP recount redo

    def score_beatmap_get(self, usermap_info: dict, beatmap_data: dict, user_id: str):
        usermap_info["accuracy"] = self.acc(int(usermap_info['count300']), int(usermap_info['count100']), int(usermap_info['count50']), int(usermap_info['countmiss']))
        status = self.status(int(beatmap_data['approved']))
        if usermap_info['rank'] == 'F':
            totalhits = int(usermap_info['count300']) + int(usermap_info['count100']) + int(usermap_info['count50']) + int(usermap_info['countmiss'])
            allhits = int(beatmap_data['count_normal']) + int(beatmap_data['count_slider']) + int(beatmap_data['count_spinner'])
            usermap_info['rank'] +=  ' ('+ str("%.2f" % float((int(totalhits) / int(allhits)) * 100)) + '%)'
        if self.mods(int(usermap_info['enabled_mods'])) == 'NoMod':
            beatmap_data['difficultyratin'] = str("%.2f" % float(beatmap_data['difficultyrating']))
            usermap_info['fullpp'] = self.fullpp(str(beatmap_data['beatmap_id']), int(usermap_info['count300']),
                                                 int(usermap_info['count100']), int(usermap_info['count50']), 0)
            usermap_info['sspp'] = self.perfectpp(str(beatmap_data['beatmap_id']), 0)
            usermap_info['pp'] = self.pippi(str(beatmap_data['beatmap_id']), int(usermap_info['count300']),
                                            int(usermap_info['count100']), int(usermap_info['count50']),
                                            int(usermap_info['countmiss']),
                                            int(usermap_info['maxcombo']), 0)
        else:
            mods = self.mods(int(usermap_info['enabled_mods']))
            usermap_info['fullpp'] = self.fullpp(str(beatmap_data['beatmap_id']), int(usermap_info['count300']),
                                                    int(usermap_info['count100']), int(usermap_info['count50']),
                                                    usermap_info['enabled_mods'])
            beatmap_data['difficultyratin'] = self.diff(beatmap_data['beatmap_id'], mods)
            usermap_info['sspp'] = self.perfectpp(str(beatmap_data['beatmap_id']), usermap_info['enabled_mods'])
            usermap_info['pp'] = self.pippi(str(beatmap_data['beatmap_id']), int(usermap_info['count300']),
                                               int(usermap_info['count100']), int(usermap_info['count50']),
                                               int(usermap_info['countmiss']), int(usermap_info['maxcombo']), usermap_info['enabled_mods'])
            beatmap_data['diff_approach'] = \
                str(self.info_diff_mod(str(beatmap_data['beatmap_id']), mods)).split('ar=')[1].split(' ')[0]
            beatmap_data['diff_overall'] = \
                str(self.info_diff_mod(str(beatmap_data['beatmap_id']), mods)).split('od=')[1].split(' ')[0]
            beatmap_data['diff_drain'] = \
                str(self.info_diff_mod(str(beatmap_data['beatmap_id']), mods)).split('hp=')[1].split(' ')[0]
            beatmap_data["diff_size"] = \
                str(self.info_diff_mod(str(beatmap_data['beatmap_id']), mods)).split('cs=')[1].split(' ')[0]
            if 'DT' in mods:
                beatmap_data["bpm"] = float(beatmap_data["bpm"]) * 1.5
        info = beatmap_data['artist'] + ' - ' + beatmap_data['title'] + \
               ' ' + '[' + beatmap_data['version'] + ']' + ' by ' + beatmap_data['creator'] + ' ' + status  + \
               '\n' + 'Player: ' + user_id + \
               '\n' + 'Очки: ' + usermap_info['score'] + \
               '\n' + 'Аккуратность: ' + str(usermap_info["accuracy"]) + '%' + \
               '\n' + 'Комбо: ' + usermap_info['maxcombo'] + '/' + beatmap_data['max_combo'] + \
               '\n' + usermap_info['count300'] + '/' + usermap_info['count100'] + '/' + usermap_info['count50'] + \
               '\n' + 'Миссы: ' + usermap_info['countmiss'] + \
               '\n' + 'Ранк: ' + usermap_info['rank'] + \
               '\n' + 'Моды: ' + self.mods(int(usermap_info['enabled_mods'])) + \
               '\n' + 'PP: ' + str(usermap_info['pp']) + ' ⯈ FC: ' + str(usermap_info['fullpp']) + ' ⯈ SS: ' + str(
            usermap_info['sspp']) + \
               '\n' + 'Ссылка: https://osu.ppy.sh/b/' + beatmap_data['beatmap_id'] + \
               '\n' + 'AR ' + beatmap_data['diff_approach'] + ' | OD ' + beatmap_data['diff_overall'] + \
               ' | HP ' + beatmap_data['diff_drain'] + ' | CS ' + beatmap_data["diff_size"] + ' | BPM ' + str(
            "%.0f" % float(beatmap_data["bpm"])) + ' | ' + str(beatmap_data['difficultyratin']) + '*'
        return info

    def score_beatmap_top(self, user_id: str, res):
        datt = res['beatmap_data']
        fed = res['usermap_info']
        info = 'ТОП скоры игрока: ' + user_id + ' std!' + '\n'
        for i in range(1, 6):
            usermap_info = fed[f'top{str(i)}']
            beatmap_data = datt[f'beatmap{str(i)}']
            usermap_info["accuracy"] = self.acc(int(usermap_info['count300']), int(usermap_info['count100']), int(usermap_info['count50']), int(usermap_info['countmiss']))
            ehh = usermap_info["enabled_mods"]
            if self.mods(int(ehh)) != 'NoMod':
                beatmap_data['difficultyrating'] = self.diff(beatmap_data['beatmap_id'], self.mods(int(ehh)))
            info = info + '♫' + str(i) + ' скор♫' + '\n' + \
                   beatmap_data['artist'] + ' - ' + beatmap_data['title'] + ' [' + beatmap_data['version'] + ']' + \
                   '\n' + str(usermap_info["accuracy"]) + '%, ' + str(
                "%.2f" % float(beatmap_data['difficultyrating'])) + '*, ' + ' ' + usermap_info['maxcombo'] + '/' + \
                   beatmap_data['max_combo'] + \
                   '\n' + usermap_info['count300'] + '/' + usermap_info['count100'] + '/' + usermap_info[
                       'count50'] + '/' + usermap_info['countmiss'] + ' +' + self.mods(int(ehh)) + \
                   '\n' + 'Ранк: ' + usermap_info['rank'] + ', PP: ' + str(
                "%.2f" % float(usermap_info['pp'])) + '\n' + 'Ссылка: https://osu.ppy.sh/b/' + beatmap_data[
                       'beatmap_id'] + '\n'
        return info


osu_session = Osu()