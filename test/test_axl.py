import os
from unittest import TestCase

from dotenv import load_dotenv

from ucmaxl import AXLHelper


def clean_none(data):
    if isinstance(data, dict):
        return {k: clean_none(v) for k, v in data.items() if v is not None}
    else:
        return data


class TestPhone(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        # read .env from parent directory
        path = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', '.env'))
        load_dotenv(path)
        cls.axl = AXLHelper(ucm_host=os.getenv('AXL_HOST'),
                            auth=(os.getenv('AXL_USER'), os.getenv('AXL_PASSWORD')),
                            verify=False)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.axl.close()
        cls.axl = None

    def setUp(self) -> None:
        pass
        # logging.basicConfig(level=logging.DEBUG)

    def test_list_phone(self):
        r = self.axl.listPhone(searchCriteria={'name': '%'},
                               returnedTags={'name': '', 'description': '', 'currentConfig': ''})
        self.assertIsNotNone(r['return'])
        self.assertIsInstance(r['return']['phone'], list)
        self.assertTrue(r['return']['phone'])
