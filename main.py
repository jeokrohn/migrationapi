from dotenv import load_dotenv
from ucmaxl import AXLHelper
import os
import zeep.exceptions
import urllib3
from ucm_reader import UCMReader


def from_env(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise KeyError(f'Make sure to set {key} either as environment variable or in the .env file')
    return value


def main():
    load_dotenv()
    axl_host = from_env('AXL_HOST')
    axl_user = from_env('AXL_USER')
    axl_password = from_env('AXL_PASSWORD')

    with UCMReader(host=axl_host, user=axl_user, password=axl_password) as ucm_reader:
        users = ucm_reader.users

    axl = AXLHelper(ucm_host=axl_host, auth=(axl_user, axl_password), verify=False)

    rt = axl.client.get_type('ns0:LPhone')()
    for k in rt:
        rt[k] = ''
    phones = axl.service.listPhone(searchCriteria={'name': '*'}, returnedTags=rt)

    try:
        devices = axl.sql_query('select * from device')
    except zeep.exceptions.Fault as e:
        print(e)

    rt = axl.client.get_type('ns0:LUser')()
    for k in rt:
        rt[k] = ''
    users = axl.list_user(returnedTags=rt)
    print(f'retrieved {len(users)} users')

    pass


if __name__ == '__main__':
    main()
