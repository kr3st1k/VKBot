import json
from datetime import datetime
import requests
from subprocess import Popen, PIPE
import subprocess
import vk_api
import oppadc
from StartupLoader.StartupLoader import StartupLoader
from PIL import Image, ImageDraw, ImageFont, ImageColor
import re
import numpy as np
import colorsys


config_loader = StartupLoader('config.JSON')

vk_session = vk_api.VkApi(token=config_loader.get_vk_token())
session_api = vk_session.get_api()
#TODO перенеси в main бг

def get_osu_token():
    return config_loader.get_osu_token()


class OsuApi:
    key = None
    mode = None  # TODO in DB
    api_url = 'https://osu.ppy.sh/api/'

    def __init__(self, token_key: str, mode: str):
        self.key = token_key
        self.mode = 0


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
#TODO enum for status_map
    def map_osu(self, beatmap_id: str):
        pas = requests.get('https://osu.ppy.sh/osu/' + beatmap_id)
        out = open('map.osu', "wb")
        out.write(pas.content)
        out.close()

    def perfectpp(self, beatmap_id: str, mods=None):
        if mods == None:
            self.map_osu(beatmap_id)
            Map = oppadc.OsuMap(file_path='map.osu')
            PP = Map.getPP()
            print(round(PP.total_pp, 1))
            return round(PP.total_pp, 1)
        else:
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

    def pippi(self, beatmap_id: str, n300: int, n100: int, n50: int, miss: int, combo: int, mods=None):
        if mods == None:
            self.map_osu(beatmap_id)
            Map = oppadc.OsuMap(file_path='map.osu')
            PP = Map.getPP(n300=n300, n100=n100, n50=n50, misses=miss, combo=combo)
            print(round(PP.total_pp, 1))
            return round(PP.total_pp, 1)
        else:
            self.map_osu(beatmap_id)
            Map = oppadc.OsuMap(file_path='map.osu')
            PP = Map.getPP(mods, n300=n300, n100=n100, n50=n50, misses=miss, combo=combo)
            print(round(PP.total_pp, 1))
            return round(PP.total_pp, 1)

    def fullpp(self, beatmap_id: str, n300: int, n100: int, n50: int, mods=None):
        if mods == None:
            self.map_osu(beatmap_id)
            Map = oppadc.OsuMap(file_path='map.osu')
            PP = Map.getPP(n300=n300, n100=n100, n50=n50)
            print(round(PP.total_pp, 1))
            return round(PP.total_pp, 1)
        else:
            self.map_osu(beatmap_id)
            Map = oppadc.OsuMap(file_path='map.osu')
            PP = Map.getPP(mods, n300=n300, n100=n100, n50=n50)
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

    def get_profile_by_id(self, user_id: str):
        try:
            return requests.get(
                self.api_url + 'get_user?' + 'k=' + self.key + '&u=' + user_id + '&m=' + str(self.mode)).json()[0]
        except:
            return "1"
            # TODO WTF

    def get_beatmap_by_id(self, beatmap_id: str):
        return requests.get(
            self.api_url + 'get_beatmaps?' + 'k=' + self.key + '&b=' + beatmap_id + '&m=' + str(self.mode)).json()[0]

    def get_score_by_id(self, user_id: str, beatmap_id: str):
        return requests.get(
            self.api_url + 'get_scores?' + 'k=' + self.key + '&b=' + beatmap_id + '&u=' + user_id + '&m=' + str(
                self.mode)).json()[0]

    def top_play(self, user_id):
        res_dict = {}
        top_dict = {}
        beatmap_dict = {}
        result = requests.get(
            self.api_url + 'get_user_best?' + 'k=' + self.key + '&u=' + user_id + '&m=' + str(self.mode) + '&limit=' + str(
                5)).json()
        for item in result:
            beatmap_dict[f'beatmap{str(int(result.index(item)) + 1)}'] = self.get_beatmap_by_id(item['beatmap_id'])
            top_dict[f'top{str(int(result.index(item)) + 1)}'] = item
        res_dict['usermap_info'] = top_dict
        res_dict['beatmap_data'] = beatmap_dict
        return res_dict

    def get_recent_by_id(self, user_id: str):
        return requests.get(
            self.api_url + 'get_user_recent?' + 'k=' + self.key + '&u=' + user_id + '&m=' + str(self.mode)).json()[0]

    def get_id_by_recent(self, user_id: str):
        return requests.get(
            self.api_url + 'get_beatmaps?' + 'k=' + self.key + '&b=' + self.get_recent_by_id(user_id)[
                'beatmap_id'] + '&m=' + str(self.mode)).json()[0]

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

    def osu_profile_tostring(self, profile_data: dict):
        try:
            pp = profile_data['pp_raw'].split(".")
            if len(pp) == 2:
                rawpp = int(pp[0])
                if float(pp[1]) > 0.5:
                    rawpp + 1
            else:
                rawpp = int(pp[0])
            return 'Ник: ' + profile_data['username'] + \
                   '\n' + 'Количество игр: ' + profile_data['playcount'] + \
                   '\n' + 'Мировой ранг: #' + profile_data['pp_rank'] + \
                   '\n' + 'Ранг по стране: #' + profile_data['pp_country_rank'] + \
                   '\n' + 'PP: ' + str(rawpp) + \
                   '\n' + 'Часов в игре: ' + str(int(int(profile_data['total_seconds_played']) / 3600)) + 'h' + \
                   '\n' + 'Точность: ' + str("%.2f" % float(profile_data['accuracy'])) + '%' + \
                   '\n' + 'Профиль: https://osu.ppy.sh/u/' + str(profile_data['user_id']) + \
                   '\n' + 'osu!Skills: http://osuskills.com/user/' + profile_data['username']

        except Exception:
            return "дурак, это кто?"
    def osu_profile_pic(self, profile_data: dict, pho: str, color= None):
        pp = profile_data['pp_raw'].split(".")
        if len(pp) == 2:
            rawpp = int(pp[0])
            if float(pp[1]) > 0.5:
                rawpp + 1
        else:
            rawpp = int(pp[0])
        base = Image.open('/home/ubuntu/VKBot/VKBot/profilenobg.png').convert('RGBA')
        pas = requests.get('https://a.ppy.sh/' + str(profile_data['user_id']))
        out = open('avatarka.jpg', "wb")
        out.write(pas.content)
        out.close()
        txt = Image.new('RGBA', base.size, (255, 255, 255, 0))
        fnt = ImageFont.truetype('/home/ubuntu/VKBot/VKBot/exo2.ttf', 16)
        avaF = Image.open('avatarka.jpg')
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
        txt.paste(ava, (20, 20))

        d.multiline_text((160,60), str(profile_data['username'] + ' | ') + str(profile_data['country']), font=(ImageFont.truetype('/home/ubuntu/VKBot/VKBot/exo2.ttf', 20)), fill=(255, 255, 255, 255))
        d.multiline_text((160, 81), 'Accuracy   ' + str("%.2f" % float(profile_data['accuracy'])) + '%', align='right',
                         font=(ImageFont.truetype('/home/ubuntu/VKBot/VKBot/exo2.ttf', 20)), fill=(255, 255, 255, 255))
        d.multiline_text((640, 5), re.sub(r"\B(?=(\d{3})+(?!\d))", ' ', str(profile_data['playcount'])), align='right',
                         font=(ImageFont.truetype('/home/ubuntu/VKBot/VKBot/exo2.ttf', 13)), fill=(255, 255, 255, 255))
        d.multiline_text((640, 32), re.sub(r"\B(?=(\d{3})+(?!\d))", ' ', str(profile_data['ranked_score'])), align='right',
                         font=(ImageFont.truetype('/home/ubuntu/VKBot/VKBot/exo2.ttf', 13)), fill=(255, 255, 255, 255))
        d.multiline_text((640, 58), re.sub(r"\B(?=(\d{3})+(?!\d))", ' ', str(profile_data['total_score'])), align='right',
                         font=(ImageFont.truetype('/home/ubuntu/VKBot/VKBot/exo2.ttf', 13)), fill=(255, 255, 255, 255))
        d.multiline_text((640, 85), re.sub(r"\B(?=(\d{3})+(?!\d))", ' ', str(int(profile_data['count300']) + int(profile_data['count100']) + int(profile_data['count50']))), align='right',
                         font=(ImageFont.truetype('/home/ubuntu/VKBot/VKBot/exo2.ttf', 13)), fill=(255, 255, 255, 255))
        huh = str(profile_data['level']).split('.')
        levelxp = (float(float("%.2f" % float(profile_data['level'])) - float(huh[0])) * 100)
        coord = float(2.33) * levelxp
        d.rectangle((512, 138) + (745, 141), fill=(0, 0, 0, 255))
        if color != None:
            d.rectangle((512, 138) + (512 + coord, 141), fill='hsb('+ str(color) + ',100%,100%)')
            d.rectangle((20, 173) + (103,174), fill='hsb('+ str(color) + ',100%,100%)')
            d.rectangle((533, 173) + (616, 174), fill='hsb('+ str(color) + ',100%,100%)')
            d.rectangle((650, 173) + (742, 174), fill='hsb('+ str(color) + ',100%,100%)')
        if color == None:
            d.rectangle((512, 138) + (512 + coord, 141), fill=(200, 154, 167, 255))
            d.rectangle((20, 173) + (103, 174), fill=(201, 153, 167, 255))
            d.rectangle((533, 173) + (616, 174), fill=(201, 153, 167, 255))
            d.rectangle((650, 173) + (742, 174), fill=(201, 153, 167, 255))
        d.multiline_text((640, 114), str("%.0f" % float(huh[0])), align='right',
                         font=(ImageFont.truetype('/home/ubuntu/VKBot/VKBot/exo2.ttf', 13)), fill=(255, 255, 255, 255))
        d.multiline_text((725, 142), str("%.0f" % float(levelxp)) + '%', align='right',
                         font=(ImageFont.truetype('/home/ubuntu/VKBot/VKBot/exo2.ttf', 10)), fill=(255, 255, 255, 255))
        d.multiline_text((20, 190),str(int(int(profile_data['total_seconds_played']) / 86400))  + str(datetime.fromtimestamp(int(profile_data['total_seconds_played'])).strftime('d %Ih %Mm')),font=fnt,
               fill=(255, 255, 255, 255))
        d.multiline_text((142, 190), re.sub(r"\B(?=(\d{3})+(?!\d))", ' ', str(rawpp)), font=fnt, fill=(255, 255, 255, 255))
        d.multiline_text((533, 190), re.sub(r"\B(?=(\d{3})+(?!\d))", ' ', str('#' +profile_data['pp_rank'])), font=fnt, fill=(255, 255, 255, 255))
        d.multiline_text((650, 190), re.sub(r"\B(?=(\d{3})+(?!\d))", ' ', str('#' +profile_data['pp_country_rank'])), font=fnt, fill=(255, 255, 255, 255))
        if len(profile_data['count_rank_ssh']) == 1:
            width = d.multiline_textsize(str(profile_data['count_rank_ssh']), font=fnt)
            d.multiline_text((253 + int(width[0]), 197), str(profile_data['count_rank_ssh']), align='center',font=fnt, fill=(255, 255, 255, 255))
        if len(profile_data['count_rank_ssh']) == 2:
            width = d.multiline_textsize(str(profile_data['count_rank_ssh']), font=fnt)
            width = width[0] / 2
            d.multiline_text((253 + int(width), 197), str(profile_data['count_rank_ssh']), align='center', font=fnt,
                         fill=(255, 255, 255, 255))
        if len(profile_data['count_rank_ssh']) > 2:
            d.multiline_text((253, 197), str(profile_data['count_rank_ssh']), align='center', font=fnt,fill=(255, 255, 255, 255))
        if len(profile_data['count_rank_ss']) == 1:
            width = d.multiline_textsize(str(profile_data['count_rank_ss']), font=fnt)
            d.multiline_text((304 + int(width[0]), 197), str(profile_data['count_rank_ss']), align='center',font=fnt, fill=(255, 255, 255, 255))
        if len(profile_data['count_rank_ss']) == 2:
            width = d.multiline_textsize(str(profile_data['count_rank_ss']), font=fnt)
            width = width[0] / 2
            d.multiline_text((304 + int(width), 197), str(profile_data['count_rank_ss']), align='center', font=fnt,
                         fill=(255, 255, 255, 255))
        if len(profile_data['count_rank_ss']) > 2:
            d.multiline_text((304, 197), str(profile_data['count_rank_ss']), align='center', font=fnt,fill=(255, 255, 255, 255))
        if len(profile_data['count_rank_sh']) == 1:
            width = d.multiline_textsize(str(profile_data['count_rank_ssh']), font=fnt)
            d.multiline_text((354 + int(width[0]), 197), str(profile_data['count_rank_sh']), align='center',font=fnt, fill=(255, 255, 255, 255))
        if len(profile_data['count_rank_sh']) == 2:
            width = d.multiline_textsize(str(profile_data['count_rank_sh']), font=fnt)
            width = width[0] / 2
            d.multiline_text((354 + int(width), 197), str(profile_data['count_rank_sh']), align='center', font=fnt,
                         fill=(255, 255, 255, 255))
        if len(profile_data['count_rank_sh']) > 2:
            d.multiline_text((354, 197), str(profile_data['count_rank_sh']), align='center', font=fnt,fill=(255, 255, 255, 255))
        if len(profile_data['count_rank_s']) == 1:
            width = d.multiline_textsize(str(profile_data['count_rank_s']), font=fnt)
            d.multiline_text((405 + int(width[0]), 197), str(profile_data['count_rank_s']), align='center',font=fnt, fill=(255, 255, 255, 255))
        if len(profile_data['count_rank_s']) == 2:
            width = d.multiline_textsize(str(profile_data['count_rank_s']), font=fnt)
            width = width[0] / 2
            d.multiline_text((405 + int(width), 197), str(profile_data['count_rank_s']), align='center', font=fnt,
                         fill=(255, 255, 255, 255))
        if len(profile_data['count_rank_s']) > 2:
            d.multiline_text((405, 197), str(profile_data['count_rank_s']), align='center', font=fnt,fill=(255, 255, 255, 255))
        if len(profile_data['count_rank_a']) == 1:
            width = d.multiline_textsize(str(profile_data['count_rank_a']), font=fnt)
            d.multiline_text((455 + int(width[0]), 197), str(profile_data['count_rank_a']), align='center',font=fnt, fill=(255, 255, 255, 255))
        if len(profile_data['count_rank_a']) == 2:
            width = d.multiline_textsize(str(profile_data['count_rank_a']), font=fnt)
            width = width[0] / 2
            d.multiline_text((455 + int(width), 197), str(profile_data['count_rank_a']), align='center', font=fnt,
                         fill=(255, 255, 255, 255))
        if len(profile_data['count_rank_a']) > 2:
            d.multiline_text((455, 197), str(profile_data['count_rank_a']), align='center', font=fnt,fill=(255, 255, 255, 255))

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
        info = beatmap_data['artist'] + ' - ' + beatmap_data['title'] + \
               ' [' + beatmap_data['version'] + ']' + ' by ' + beatmap_data['creator'] + \
               '\n' + 'Комбо: ' + beatmap_data['max_combo'] + \
               '\n' + 'Длительность: ' + str(int(beatmap_data['hit_length']) // 60) + ':' + str(int(beatmap_data['hit_length']) % 60) + \
               '\n' + '100% - ' +  str(self.perfectpp(str(beatmap_data['beatmap_id']))) + \
               '\n' + 'AR ' + beatmap_data['diff_approach'] + ' | OD ' + beatmap_data['diff_overall'] + \
               ' | HP ' + beatmap_data['diff_drain'] + ' | CS ' + beatmap_data["diff_size"] + ' | BPM ' + str(
            "%.0f" % float(beatmap_data["bpm"])) + ' | ' + str("%.2f" % float(beatmap_data['difficultyrating'])) + '*'
        return info
    # TODO PP recount redo

    def score_beatmap_get(self, usermap_info: dict, beatmap_data: dict, user_id: str):
        accur = int(usermap_info['count50']) * 50 + int(usermap_info['count100']) * 100 + int(
            usermap_info['count300']) * 300
        accur1 = int(usermap_info['count50']) + int(usermap_info['count100']) + int(usermap_info['count300']) + int(
            usermap_info['countmiss'])
        accur2 = 300 * accur1
        accur = accur / accur2
        count = len(str(accur))
        usermap_info["accuracy"] = accur
        if count > 3:
            accur = accur * 100
            accur = round(float(accur), 2)
            #TODO ACCURACY
            usermap_info["accuracy"] = accur
        elif type(accur) == float:
            accur = round(float(accur))
            usermap_info["accuracy"] = accur
        if usermap_info['rank'] == 'F':
            totalhits = int(usermap_info['count300']) + int(usermap_info['count100']) + int(usermap_info['count50']) + int(usermap_info['countmiss'])
            allhits = int(beatmap_data['count_normal']) + int(beatmap_data['count_slider']) + int(beatmap_data['count_spinner'])
            usermap_info['rank'] +=  ' ('+ str("%.2f" % float((int(totalhits) / int(allhits)) * 100)) + '%)'
        if self.mods(int(usermap_info['enabled_mods'])) == 'NoMod':
            beatmap_data['difficultyratin'] = str("%.2f" % float(beatmap_data['difficultyrating']))
            usermap_info['fullpp'] = self.fullpp(str(beatmap_data['beatmap_id']), int(usermap_info['count300']),
                                                 int(usermap_info['count100']), int(usermap_info['count50']))
            usermap_info['sspp'] = self.perfectpp(str(beatmap_data['beatmap_id']))
            usermap_info['pp'] = self.pippi(str(beatmap_data['beatmap_id']), int(usermap_info['count300']),
                                            int(usermap_info['count100']), int(usermap_info['count50']),
                                            int(usermap_info['countmiss']),
                                            int(usermap_info['maxcombo']))
        else:
            mods = self.mods(int(usermap_info['enabled_mods']))
            usermap_info['fullpp'] = self.fullpp(str(beatmap_data['beatmap_id']), int(usermap_info['count300']),
                                                    int(usermap_info['count100']), int(usermap_info['count50']),
                                                    mods)
            beatmap_data['difficultyratin'] = self.diff(beatmap_data['beatmap_id'], mods)
            usermap_info['sspp'] = self.perfectpp(str(beatmap_data['beatmap_id']), mods)
            usermap_info['pp'] = self.pippi(str(beatmap_data['beatmap_id']), int(usermap_info['count300']),
                                               int(usermap_info['count100']), int(usermap_info['count50']),
                                               int(usermap_info['countmiss']), int(usermap_info['maxcombo']), mods)
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
               ' ' + '[' + beatmap_data['version'] + ']' + ' by ' + beatmap_data['creator'] + \
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

    def score_beatmap_top(self, user_id: str):
        res = self.top_play(user_id)
        datt = res['beatmap_data']
        fed = res['usermap_info']
        info = 'ТОП скоры игрока: ' + user_id + ' std!' + '\n'
        for i in range(1, 6):
            usermap_info = fed[f'top{str(i)}']
            beatmap_data = datt[f'beatmap{str(i)}']
            ehh = self.get_score_by_id(user_id, beatmap_data['beatmap_id'])['enabled_mods']
            accur = int(usermap_info['count50']) * 50 + int(usermap_info['count100']) * 100 + int(
                usermap_info['count300']) * 300
            accur1 = int(usermap_info['count50']) + int(usermap_info['count100']) + int(
                usermap_info['count300']) + int(
                usermap_info['countmiss'])
            accur2 = 300 * accur1
            accur = accur / accur2
            count = len(str(accur))
            usermap_info["accuracy"] = accur
            if count > 3:
                accur = accur * 100
                accur = round(float(accur), 2)
                usermap_info["accuracy"] = accur
            elif type(accur) == float:
                accur = round(float(accur))
                usermap_info["accuracy"] = accur
            if self.mods(int(ehh)) != 'NoMod':
                beatmap_data['difficultyrating'] = self.diff(beatmap_data['beatmap_id'], self.mods(int(ehh)))
            info = info + '♫' + str(i) + ' скор♫' + '\n' + \
                   beatmap_data['artist'] + ' - ' + beatmap_data['title'] + ' [' + beatmap_data['version'] + ']' + \
                   '\n' + str(usermap_info["accuracy"]) + '%, ' + str(
                "%.2f" % float(beatmap_data['difficultyrating'])) + '* ' + 'Комбо: ' + usermap_info['maxcombo'] + '/' + \
                   beatmap_data['max_combo'] + \
                   '\n' + usermap_info['count300'] + '/' + usermap_info['count100'] + '/' + usermap_info[
                       'count50'] + '/' + usermap_info['countmiss'] + ' +' + self.mods(int(ehh)) + \
                   '\n' + 'Ранк: ' + usermap_info['rank'] + ', PP: ' + str(
                "%.2f" % float(usermap_info['pp'])) + '\n' + 'Ссылка: https://osu.ppy.sh/b/' + beatmap_data[
                       'beatmap_id'] + '\n'
        return info


osu_session = OsuApi(get_osu_token(), 0)