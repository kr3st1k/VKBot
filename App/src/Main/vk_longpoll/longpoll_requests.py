from App.src.Main.vk_api.vk_api_methods import VKApi
import requests


class LongpollApiRequests(VKApi):
    access_token = None
    ts = None
    pts = None
    key = None
    server_name = None
    server_im = None
    vk_session = None
    def __init__(self, access_token):
        self.access_token = access_token
        self.vk_session = VKApi(access_token)

    def get_longpoll_server(self, need_pts: bool, version):
        requested = self.vk_session.vk_method('messages.getLongPollServer?', 'lp_version=' + str(version), True)
        print(requested)






req = LongpollApiRequests('')
req.get_longpoll_server(False, 3)