import requests

from loguru import logger

from .base import POCTemplate


class OnvifAnonymousAccessDetect(POCTemplate):

    def __init__(self, config):
        super().__init__(config)
        self.name = self.get_file_name(__file__)
        self.product = config.product['cam']
        self.product_version = ''
        self.ref = ''
        self.level = POCTemplate.level.medium
        self.desc = """"""
        self.headers = {
            'Connection': 'close',
            'Content-Type': 'application/soap+xml; charset=utf-8; action="http://www.onvif.org/ver10/device/wsdl/GetScopes"',
            'User-Agent': self.config.user_agent,
        }
        self.body = (
            '<?xml version="1.0" encoding="utf-8"?>'
            '<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope" '
            'xmlns:tt="http://www.onvif.org/ver10/schema">'
            '<s:Body>'
            '<GetScopes xmlns="http://www.onvif.org/ver10/device/wsdl"/>'
            '</s:Body>'
            '</s:Envelope>'
        )

    def verify(self, ip, port=80):
        url = f"http://{ip}:{port}/onvif/device_service"
        try:
            r = requests.post(url, data=self.body, headers=self.headers, timeout=self.config.timeout, verify=False)
            if r.status_code == 200 and (('http://' in r.text) or ('urn:' in r.text)):
                return ip, str(port), self.product, '', '', self.name
        except Exception as e:
            logger.error(e)
        return None

    def exploit(self, results):
        pass


POCTemplate.register_poc(OnvifAnonymousAccessDetect)
