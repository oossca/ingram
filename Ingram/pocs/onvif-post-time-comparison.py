import time
import requests

from loguru import logger

from .base import POCTemplate


class OnvifPostTimeComparison(POCTemplate):

    def __init__(self, config):
        super().__init__(config)
        self.name = self.get_file_name(__file__)
        self.product = config.product['cam']
        self.product_version = ''
        self.ref = ''
        self.level = POCTemplate.level.low
        self.desc = """"""
        self.headers = {
            'Connection': 'close',
            'Content-Type': 'application/soap+xml; charset=utf-8; action="http://www.onvif.org/ver10/device/wsdl/GetSystemDateAndTime"',
            'User-Agent': self.config.user_agent,
        }

    def _extract(self, text, tag):
        start = text.find(f"<{tag}>")
        end = text.find(f"</{tag}>")
        if start == -1 or end == -1:
            return None
        return text[start + len(tag) + 2:end]

    def verify(self, ip, port=80):
        url = f"http://{ip}:{port}/onvif/device_service"
        try:
            r = requests.post(url, data='', headers=self.headers, timeout=self.config.timeout, verify=False)
            if r.status_code not in [200, 401]:
                return None
            body = r.text or ''
            year = self._extract(body, 'Year')
            month = self._extract(body, 'Month')
            day = self._extract(body, 'Day')
            hour = self._extract(body, 'Hour')
            minute = self._extract(body, 'Minute')
            second = self._extract(body, 'Second')
            if not all([year, month, day, hour, minute, second]):
                return None
            ipc_time = time.mktime((int(year), int(month), int(day), int(hour), int(minute), int(second), 0, 0, -1))
        except Exception as e:
            logger.error(e)
            return None

        try:
            diff_time = abs(time.time() - ipc_time)
            if diff_time >= 5 * 60:
                return ip, str(port), self.product, '', f"diff_time:{int(diff_time)}", self.name
        except Exception as e:
            logger.error(e)
        return None

    def exploit(self, results):
        pass


POCTemplate.register_poc(OnvifPostTimeComparison)
