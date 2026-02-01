import socket

from loguru import logger

from .base import POCTemplate


class GB28181NoDetect(POCTemplate):

    def __init__(self, config):
        super().__init__(config)
        self.name = self.get_file_name(__file__)
        self.product = config.product['cam']
        self.product_version = ''
        self.ref = ''
        self.level = POCTemplate.level.low
        self.desc = """"""

    def _tcp_open(self, ip, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(self.config.timeout)
        try:
            return s.connect_ex((ip, int(port))) == 0
        except Exception as e:
            logger.error(e)
            return False
        finally:
            s.close()

    def _udp_active(self, ip, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(self.config.timeout)
        try:
            s.sendto(b"\r\n", (ip, int(port)))
            s.recvfrom(1024)
            return True
        except Exception:
            return False
        finally:
            s.close()

    def verify(self, ip, port=80):
        try:
            if self._tcp_open(ip, 554) and (not self._udp_active(ip, 5060)) and (not self._udp_active(ip, 5061)):
                return ip, str(port), self.product, '', '', self.name
        except Exception as e:
            logger.error(e)
        return None

    def exploit(self, results):
        pass


POCTemplate.register_poc(GB28181NoDetect)
