import requests

from loguru import logger

from .base import POCTemplate


class Xiongmai60001(POCTemplate):

    def __init__(self, config):
        super().__init__(config)
        self.name = self.get_file_name(__file__)
        self.product = config.product['xiongmai']
        self.product_version = ''
        self.ref = ''
        self.level = POCTemplate.level.low
        self.desc = """"""
        self.headers = {'Connection': 'close', 'User-Agent': self.config.user_agent}

    def verify(self, ip, port=60001):
        try:
            r = requests.get(f"http://{ip}:{port}/", headers=self.headers, timeout=self.config.timeout, verify=False)
            r1 = requests.get(f"http://{ip}:{port}/view2.html", headers=self.headers, timeout=self.config.timeout, verify=False)
            if r.status_code == 200 and r1.status_code == 200:
                if ('onDblClick' in r.text) and ('Network video client' in r.text) and ('view2.js' in r1.text):
                    return ip, str(port), self.product, '', '', self.name
        except Exception as e:
            logger.error(e)
        return None

    def exploit(self, results):
        pass


POCTemplate.register_poc(Xiongmai60001)
