from ucmaxl import AXLHelper
import urllib3

from typing import List
import logging

from ucm_reader.base import *
from ucm_reader.user import *
from ucm_reader.phone import *
from ucm_reader.locations import *

log = logging.getLogger(__name__)


class UCMReader:
    def __init__(self, host: str, user: str, password: str, verify=False):
        if not verify:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self._axl = AXLHelper(ucm_host=host, auth=(user, password), verify=verify)
        self.user = UserApi(self._axl.service)
        self.phone = PhoneApi(self._axl.service)
        self.location = LocationApi(self._axl.service)

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
