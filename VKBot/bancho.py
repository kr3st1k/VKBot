def get_osu_token():
    return 'tokenhere'

class osu_api:
    key = None
    mode = None  # std_mode
    api_url = 'https://osu.ppy.sh/api/'

    def __init__(self, token_key: str, mode=0):
        self.key = token_key
        self.mode = mode

    def request_json(self, url: str, args: str):
        try:
            return requests.get(str(url) + 'k=' + self.key).json()
        except:
            return ""

    def mods(self, num):
        mods_osu = {}
        modes = []
        opt = {'HalfTime': 256, 'NoFail': 1, 'Easy': 2, 'HardRock': 16,
               'Hidden': 8, 'FlashLight': 1024, 'SpunOut': 4096, 'TouchDevice': 4,
               'Relax': 128, 'Autoplay': 2048, 'Relax2': 8192, 'ScoreV2': 536870912}
        for key, value in opt.items():
            if value & num == value:
                mods_osu[key] = value
        num_s = 0

        for key in mods_osu:
            num_s = num_s + mods_osu[key]
        if num_s != num:
            if 576 + num_s == num:
                mods_osu['NightCore'] = 576
            if 32 + num_s == num:
                mods_osu['SuddenDeath'] = 32
            if 64 + num_s == num:
                mods_osu['DoubleTime'] = 64
            if 16416 + num_s == num:
                mods_osu['Perfect'] = 16416

            if 576 + 32 + num_s == num:
                mods_osu['NightCore'] = 576
                mods_osu['SuddenDeath'] = 32
            if 576 + 16416 + num_s == num:
                mods_osu['NightCore'] = 576
                mods_osu['Perfect'] = 16416

            if 64 + 32 + num_s == num:
                mods_osu['DoubleTime'] = 64
                mods_osu['SuddenDeath'] = 32
            if 64 + 16416 + num_s == num:
                mods_osu['DoubleTime'] = 64
                mods_osu['Perfect'] = 16416

        if mods_osu == {}:
            mods_osu['Нет'] = 'Нет'

        for key in mods_osu:
            modes.append(key)

        return ','.join(modes)

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
        result = requests.get(self.api_url + 'get_user_best?' + 'k=' + self.key + '&u=' + user_id + '&m=' + str(0) + '&limit=' + str(5)).json()
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
        r = self.get_recent_by_id(user_id)['beatmap_id']
        return requests.get(
            self.api_url + 'get_beatmaps?' + 'k=' + self.key + '&b=' + r + '&m=' + str(self.mode)).json()[0]
    def bb(self, user_id: str):
        return requests.get(
            self.api_url + 'get_beatmaps?' + 'k=' + self.key + '&b=' + self.get_recent_by_id(user_id)['beatmap_id'] + '&m=' + str(self.mode)).json()[0]

    def get_bg_rec(self, user_id: str):
        try:
            pic = 'https://assets.ppy.sh/beatmaps/{0}/covers/cover.jpg'.format(str(self.bb(user_id)['beatmapset_id']))
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
                   '\n\n' + 'Профиль: https://osu.ppy.sh/u/' + profile_data['username'] + \
                   '\n' + 'osu!Skills: http://osuskills.com/user/' + profile_data['username']

        except Exception:
            return "дурак, это кто?"

    def beatmap_get_send(self, beatmap_data: dict):
        info = beatmap_data['artist'] + ' - ' + beatmap_data['title'] + \
               '\n' + '[' + beatmap_data['version'] + ']' + ' Создатель: ' + beatmap_data['creator'] + \
               '\n' + 'Комбо:  ' + beatmap_data['max_combo'] + \
               '\n' + 'Длительность:  ' + str(int(beatmap_data['hit_length']) // 60) + ':' + str(
            int(beatmap_data['hit_length']) % 60) + \
               '\n' + 'AR ' + beatmap_data['diff_approach'] + ' | OD ' + beatmap_data['diff_overall'] + \
               ' | HP ' + beatmap_data['diff_overall'] + ' | CS ' + beatmap_data["diff_size"] + ' | ' + str(
            "%.2f" % float(beatmap_data['difficultyrating'])) + '*'
        return info

    def score_beatmap_get(self, usermap_info: dict, beatmap_data: dict, user_id: str):
        try:
            accur = int(usermap_info['count50']) * 50 + int(usermap_info['count100']) * 100 + int(usermap_info['count300']) * 300
            accur1 = int(usermap_info['count50']) + int(usermap_info['count100']) + int(usermap_info['count300']) + int(usermap_info['countmiss'])
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
            info = beatmap_data['artist'] + ' - ' + beatmap_data['title'] + \
                   '\n' + '[' + beatmap_data['version'] + ']' + ' Map Creator: ' + beatmap_data['creator'] + \
                   '\n' + 'Сыграно игроком: ' + user_id + \
                   '\n' + 'Очки: ' + usermap_info['score'] + \
                   '\n' + 'Аккуратность: ' + str(usermap_info["accuracy"]) + '%' + \
                   '\n' + 'Комбо: ' + usermap_info['maxcombo'] + '/' + beatmap_data['max_combo'] + \
                   '\n' + usermap_info['count300'] + '/' + usermap_info['count100'] + '/' + usermap_info['count50'] + \
                                             '\n' + 'Миссы: ' + usermap_info['countmiss'] + \
                   '\n' + 'Ранк: ' + usermap_info['rank'] + \
                   '\n' + 'Моды: ' + self.mods(int(usermap_info['enabled_mods'])) + \
                   '\n' + 'PP: ' + str("%.2f" % float(usermap_info['pp'])) + \
                   '\n' + 'AR ' + beatmap_data['diff_approach'] + ' | OD ' + beatmap_data['diff_overall'] + \
                   ' | HP ' + beatmap_data['diff_overall'] + ' | CS ' + beatmap_data["diff_size"] + ' | ' + str(
                "%.2f" % float(beatmap_data['difficultyrating'])) + '*'
            return info
        except:
            return 'это ху?'
    def score_beatmap_recent(self, usermap_info: dict, beatmap_data: dict, user_id: str):
        try:
            accur = int(usermap_info['count50']) * 50 + int(usermap_info['count100']) * 100 + int(usermap_info['count300']) * 300
            accur1 = int(usermap_info['count50']) + int(usermap_info['count100']) + int(usermap_info['count300']) + int(usermap_info['countmiss'])
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
            info = beatmap_data['artist'] + ' - ' + beatmap_data['title'] + \
                       '\n' + '[' + beatmap_data['version'] + ']'  + ' Map Creator: ' + beatmap_data['creator'] + \
                       '\n' + 'Player: ' + user_id + \
                       '\n' + 'Очки: ' + usermap_info['score'] + \
                       '\n' + 'Аккуратность: ' + str(usermap_info["accuracy"]) + '%' + \
                       '\n' + 'Комбо: ' + usermap_info['maxcombo'] + '/' + beatmap_data['max_combo'] + \
                       '\n' + usermap_info['count300'] + '/' + usermap_info['count100'] + '/' + usermap_info['count50'] + \
                                                 '\n' + 'Миссы: ' + usermap_info['countmiss'] + \
                       '\n' + 'Ранк: ' + usermap_info['rank'] + \
                       '\n' + 'Моды: ' + self.mods(int(usermap_info['enabled_mods'])) + \
                       '\n' + 'Ссылка: https://osu.ppy.sh/b/' + beatmap_data['beatmap_id'] + \
                       '\n' + 'AR ' + beatmap_data['diff_approach'] + ' | OD ' + beatmap_data['diff_overall'] + \
                       ' | HP ' + beatmap_data['diff_overall'] + ' | CS ' + beatmap_data["diff_size"] + ' | ' + str(
                    "%.2f" % float(beatmap_data['difficultyrating'])) + '*'
            return info
        except:
            return 'Ты вообще существуешь? или долго не играл, а?'

    def score_beatmap_top(self, user_id: str):
        try:
            res = self.top_play(user_id)
            datt = res['beatmap_data']
            fed = res['usermap_info']
            info = 'ТОП скоры игрока: ' + user_id + ' std!' + '\n'
            for i in range (1, 6):
                usermap_info = fed[f'top{str(i)}']
                beatmap_data = datt[f'beatmap{str(i)}']
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
                    usermap_info["accuracy"] = accur
                elif type(accur) == float:
                    accur = round(float(accur))
                    usermap_info["accuracy"] = accur
                info = info + '♫' + str(i) + ' скор♫' + '\n' + \
                    beatmap_data['artist'] + ' - ' + beatmap_data['title'] + ' [' + beatmap_data['version'] + ']' + \
                       '\n' + str(usermap_info["accuracy"]) + '%, ' + str("%.2f" % float(beatmap_data['difficultyrating'])) + '*, ' + 'Комбо: ' + usermap_info['maxcombo'] + '/' + \
                       beatmap_data['max_combo'] + \
                       '\n' + usermap_info['count300'] + '/' + usermap_info['count100'] + '/' + usermap_info['count50'] + '/' + usermap_info['countmiss'] + \
                       '\n' + 'Ранк: ' + usermap_info['rank'] + ', PP: ' + str("%.2f" % float(usermap_info['pp'])) + '\n'  + 'Ссылка: https://osu.ppy.sh/b/' + beatmap_data['beatmap_id'] + '\n'

            return info
        except:
            return 'Дуралей, либо неправильный ник, либо ты кто такой?'

osu_session = osu_api(get_osu_token(), 0)