import vk_api


def captcha_handler(captcha):

    key = input("Enter captcha code {0}: ".format(captcha.get_url())).strip()

    return captcha.try_again(key)
