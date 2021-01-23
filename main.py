from dotenv import load_dotenv
import os
from ucm_reader import UCMReader
import logging
from collections import defaultdict
import random
import asyncio
import datetime

from ucm_reader import User
from webexteamsasyncapi import WebexTeamsAsyncAPI, License, Location

from typing import List, Optional

# number of test users to provision
TEST_USERS_TO_PROVISION = 10

# number of parallel user provisioning tasks
PARALLEL_TASKS = 5


def from_env(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise KeyError(f'Make sure to set {key} either as environment variable or in the .env file')
    return value


load_dotenv()
AXL_HOST = from_env('AXL_HOST')
AXL_USER = from_env('AXL_USER')
AXL_PASSWORD = from_env('AXL_PASSWORD')
WEBEX_TOKEN = from_env('WEBEX_ACCESS_TOKEN')
GMAIL_ID = from_env('GMAIL_ID')


async def get_calling_license(api: WebexTeamsAsyncAPI) -> Optional[License]:
    # get all licenses
    licenses = [licence async for licence in api.licenses.list()]
    result = next(
        licence for licence in licenses if licence.name.startswith('Webex Calling - Standard Enterprise'))
    return result


def webex_email(user: User):
    time_stamp = datetime.datetime.utcnow().strftime('%Y%m%d%H')
    # get the user portion of the email
    email_user = user.mailid.split('@')[0]
    # now construct an email address to be used in Webex. We add a timestamp so that they are unique
    email = f'{GMAIL_ID}+{time_stamp}-{email_user}@gmail.com'
    return email


def webex_display_name(user: User):
    display_name = f'{user.firstName} {user.lastName}'
    return display_name


def webex_extension(user: User) -> str:
    """
    For a given UCM user determine the extension to be used in Webex Calling
    Here we simply take the last four digit of the user's phone number
    :param user: UCM user
    :return: four digit extension
    """
    # last four digits
    return user.telephoneNumber.strip()[-4:]


async def get_locations(api: WebexTeamsAsyncAPI) -> List[Location]:
    """
    Get list of all Webex Calling locations
    :param api:
    :return:
    """
    return [location async for location in api.locations.list()]


async def provision_single_user(sema: asyncio.Semaphore,
                                api: WebexTeamsAsyncAPI,
                                calling_license: License,
                                location: Location,
                                user: User):
    """
    Provision a single Webex calling user
    :param sema: semaphore to control parallel execution of user provisioning tasks
    :param api: Webex API
    :param calling_license: the calling license to user for each user
    :param location: Webex calling location to assign the user to
    :param user: UCM user information
    :return:
    """
    # limit the number of concurrent provisioning tasks
    async with sema:
        email = webex_email(user)
        people_list = [p async for p in api.people.list(email=email)]
        if people_list:
            print(f'{user.mailid}: user exists')
            return
        print(f'{user.mailid}: user does not exist')
        print(f'{user.mailid}: creating user')
        new_user = await api.people.create(emails=[email],
                                           display_name=webex_display_name(user),
                                           first_name=user.firstName,
                                           last_name=user.lastName)
        print(f'{user.mailid}: created user, id: {new_user.id}')
        licenses = new_user.licenses
        licenses.append(calling_license.id)

        # now we still need to add the calling license to the user and set the extension
        extension = webex_extension(user)
        print(f'{user.mailid}: adding calling license and extension {extension}')
        updated = await api.people.update(person_id=new_user.id,
                                          first_name=new_user.first_name,
                                          last_name=new_user.last_name,
                                          display_name=new_user.display_name,
                                          extension=extension,
                                          location_id=location.id,
                                          licenses=licenses,
                                          calling_data=True)
        print(f'{user.mailid}: added calling license and extension, phone numbers: {updated.phone_numbers}')


async def user_provisioning(users: List[User]):
    """
    Provision a bunch of UCM users in Webex Calling
    :param users: list of UCM users
    :return:
    """
    sema = asyncio.Semaphore(PARALLEL_TASKS)
    async with WebexTeamsAsyncAPI(access_token=WEBEX_TOKEN,
                                  concurrent_requests=10) as api:
        print('Getting calling license')
        licence = await get_calling_license(api)
        print(f'Got calling license, id: {licence.id}')

        print('Getting locations')
        locations = await get_locations(api=api)
        print('Got list of locations')
        # We are looking for a location 'SJC' that's where we wan to put our users
        sjc_location = next((location
                             for location in locations
                             if location.name == 'SJC'), None)
        if sjc_location is None:
            print('Failed to get location "SJC"')
            return
        print(f'location "SJC", id: {sjc_location.id}')
        tasks = [provision_single_user(sema=sema,
                                       api=api,
                                       calling_license=licence,
                                       location=sjc_location,
                                       user=user)
                 for user in users]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for user, result in zip(users, results):
            if isinstance(result, Exception):
                print(f'Provisioning of user {user.mailid} failed: {result}')


def main():
    print('Preparing UCMReader...')
    with UCMReader(host=AXL_HOST, user=AXL_USER, password=AXL_PASSWORD) as ucm_reader:
        # get all users from UCM
        print('Getting users from UCM...')
        users = ucm_reader.user.list()

        # Let's check for consistent phone numbers and primary extensions
        users_ok = []
        users_nok = []
        for user in users:
            if user.mailid and \
                    user.primaryExtension and \
                    user.primaryExtension.pattern and \
                    user.primaryExtension.pattern.strip('\\') == user.telephoneNumber:
                users_ok.append(user)
            else:
                users_nok.append(user)

        # group users by 1st five digits of their phone number
        users_per_npa = defaultdict(list)
        for user in users_ok:
            users_per_npa[user.telephoneNumber[:5]].append(user)
        for npa in users_per_npa:
            print(f'NPA {npa}: {len(users_per_npa[npa])} users')

        # let's focus on users in NPA 408
        users = users_per_npa['+1408']

        # b/c we only have limited licenses we pick some random users
        users = random.sample(users, TEST_USERS_TO_PROVISION)
        # we want to use asyncio to be able to provision multiple users "in parallel" b/c a single transaction
        # can take a while...
        asyncio.run(user_provisioning(users=users))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('asyncio').setLevel(logging.INFO)
    logging.getLogger('ucmaxl').setLevel(logging.INFO)
    logging.getLogger('urllib3').setLevel(logging.INFO)
    logging.getLogger('zeep').setLevel(logging.INFO)
    logging.getLogger('zeep.transports').setLevel(logging.INFO)
    logging.getLogger('webexteamsasyncapi.rest').setLevel(logging.INFO)
    logging.getLogger('webexteamsasyncapi.api').setLevel(logging.INFO)
    main()
