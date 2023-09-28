import random
import time
from random import choice

import requests
import pyuseragents

from core.utils import str_to_file, logger, CaptchaService
from string import ascii_lowercase, digits

from core.utils import MailUtils
from core.utils.custom_faker import CustomFaker
from data.config import MOBILE_PROXY, MOBILE_PROXY_CHANGE_IP_LINK


class Arkham(MailUtils, CustomFaker):
    referral = None

    def __init__(self, email: str, imap_pass: str, address: str, proxy: str = None):
        CustomFaker.__init__(self)
        super().__init__(email, imap_pass)

        self.address = address.lower()
        self.proxy = Arkham.get_proxy(proxy)

        self.password = Arkham.generate_password(random.randint(7, 12))
        self.username = self.get_username()

        self.headers = {
            'authority': 'api.arkhamintelligence.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/json',
            'origin': 'https://platform.arkhamintelligence.com',
            'referer': 'https://platform.arkhamintelligence.com/',
            'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': pyuseragents.random(),
        }

        self.session = requests.Session()

        self.session.headers.update(self.headers)
        self.session.proxies.update({'https': self.proxy, 'http': self.proxy})

    @staticmethod
    def get_proxy(proxy: str):
        if MOBILE_PROXY:
            Arkham.change_ip()
            proxy = MOBILE_PROXY

        if proxy is not None:
            return f"http://{proxy}"

    @staticmethod
    def change_ip():
        requests.get(MOBILE_PROXY_CHANGE_IP_LINK)

    def send_verify_code(self):
        url = 'https://api.arkhamintelligence.com/signup/send_verify_code'

        json_data = {
            'email': self.email,
            'captcha': Arkham.__bypass_captcha(),
        }

        response = self.send_request("post", url, json_data=json_data)

        return self.email == response.text.strip().strip('"')

    def get_verify_code(self):
        result = self.get_msg(subject='Arkham Email Verification', from_='accounts@arkhamintelligence.com',
                              to=self.email, limit=2)
        return str(result["msg"]).split("signup process:")[1].split("If you did not")[0].strip()

    def register(self, verify_code: str):
        url = 'https://api.arkhamintelligence.com/signup'

        json_data = {
            'email': self.email,
            'password': self.password,
            'username': self.username,
            'displayName': self.name,
            'referrer': Arkham.referral,
            '_botpoison': '',
            'verificationCode': verify_code,
        }

        response = self.send_request("post", url, json_data=json_data)

        return response.json()

    def sign_up(self, verify_code: str):
        is_register = self.register(verify_code)

        self.session.headers["authorization"] = self.get_auth_token()["idToken"]

        return is_register

    def get_auth_token(self):
        url = 'https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword'

        headers = {
            'authority': 'www.googleapis.com',
            'accept': '*/*',
            'accept-language': 'uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/json',
            'origin': 'https://platform.arkhamintelligence.com',
            'referer': 'https://platform.arkhamintelligence.com/',
            'user-agent': pyuseragents.random(),
            'x-client-version': 'Chrome/JsCore/8.10.1/FirebaseCore-web',
        }

        params = {
            'key': 'AIzaSyA9EERCXQ0gQstZRwcQ_Ws8XAELd2FUaXM',
        }

        json_data = {
            'email': self.email,
            'password': self.password,
            'returnSecureToken': True,
        }

        response = self.send_request("post", url, headers=headers, params=params, json_data=json_data)

        return response.json()

    def connect_wallet(self):
        url = 'https://api.arkhamintelligence.com/user/address'

        json_data = [
            {
                'address': self.address,
                'chainType': 'evm',
            },
        ]

        response = self.send_request("post", url, json_data=json_data)

        return response.status_code == 200 and response.text == ""

    def send_request(self, method, url, headers=None, json_data=None, params=None, data=None, proxies=None,
                     allow_redirects=True, timeout=40):
        if not headers:
            headers = self.headers.copy()

        if proxies is None:
            proxies = {"http": self.proxy, "https": self.proxy}

        endpoint = url.split('/')[-1]

        for _ in range(4):
            try:
                time.sleep(random.uniform(2, 10))
                resp = getattr(self.session, method)(url, headers=headers, json=json_data, params=params,
                                                     proxies=proxies,
                                                     data=data, allow_redirects=allow_redirects, timeout=timeout
                                                     )

                logger.debug(f"{resp.status_code} | {endpoint} | {resp.text}")
                if resp.ok:
                    return resp

            except Exception as e:
                logger.error(f"Request Error: {e}")

        raise Exception(f"Failed to send request | {endpoint}")

    def logs(self, file_name: str, msg_result: str = ""):
        log_message = f"{self.email}{msg_result}"
        getattr(logger, "success" if file_name == "success" else "error")(log_message)

        str_to_file(f"./logs/{file_name}.txt", f"{self.email}|{self.username}|{self.proxy}")

    @staticmethod
    def __bypass_captcha():
        captcha_service = CaptchaService()
        return captcha_service.get_captcha_token()

    @staticmethod
    def generate_password(k=10):
        return ''.join([choice(ascii_lowercase + digits) for i in range(k)])
