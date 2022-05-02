#!/usr/bin/env python
import asyncio
import datetime
import logging
import os
import random
import time
from collections import defaultdict
from typing import List, Optional

from dotenv import load_dotenv
from wxc_sdk.all_types import License, Location, Person, PhoneNumber
from wxc_sdk.as_api import AsWebexSimpleApi
from wxc_sdk.people import PhoneNumberType
from wxc_sdk.telephony import NumberListPhoneNumber, NumberOwner

from ucm_reader import UCMReader
from ucm_reader import User

# number of test users to provision
TEST_USERS_TO_PROVISION = 60

# number of parallel user provisioning tasks
PARALLEL_TASKS = 10

# don't actually provision users
READONLY = True

TIMESTAMP_IN_USER_EMAILS = False

log = logging.getLogger(__name__)


def from_env(key: str) -> str:
    """
    Try to get a value from an environment variable and raise KeyError of the environment variable is not set
    """
    value = os.getenv(key)
    if value is None:
        raise KeyError(f'Make sure to set {key} either as environment variable or in the .env file')
    return value


# get some info from environment variables .. load .env file 1st
load_dotenv()
AXL_HOST = from_env('AXL_HOST')
AXL_USER = from_env('AXL_USER')
AXL_PASSWORD = from_env('AXL_PASSWORD')
WEBEX_TOKEN = from_env('WEBEX_ACCESS_TOKEN')
GMAIL_ID = from_env('GMAIL_ID')


async def get_calling_licenses(*, api: AsWebexSimpleApi) -> list[License]:
    """
    Get list of calling licenses
    :param api: API to use
    :return: list of calling licenses with professional licenses first
    """
    # get all calling licenses
    licenses = [lic async for lic in api.licenses.list_gen()
                if lic.webex_calling_basic or lic.webex_calling_professional]

    def lic_key(lic: License) -> str:
        """
        Sort WxC licenses; bring professional licenses to the front
        """
        return f'{"0" if lic.webex_calling_professional else "1"}{lic.license_id}'

    licenses.sort(key=lic_key)
    return licenses


def allocate_calling_license(*, calling_license_list: list[License]) -> Optional[License]:
    """
    Allocate a calling license and return the license used for the allocation
    :param calling_license_list: list of calling licenses to chose allocation from
    :return: calling license; None if no calling license is available
    """
    license_with_available_allocation = next((lic for lic in calling_license_list
                                              if lic.consumed_units < lic.total_units), None)
    if license_with_available_allocation is None:
        return None
    license_with_available_allocation.consumed_units += 1
    return license_with_available_allocation


def webex_email(*, user: User):
    """
    For a given UCM user determine the email address be used in Webex Calling
    Here we create dummy email addresses under a given GMAIL address
    In reality one would use the actual email address of the UCM user
    :param user: UCM user
    :return: email address
    """
    time_stamp = datetime.datetime.utcnow().strftime('%Y%m%d%H')
    # get the user portion of the email
    email_user = user.mailid.split('@')[0]
    # now construct an email address to be used in Webex. We add a timestamp so that they are unique
    if TIMESTAMP_IN_USER_EMAILS:
        email = f'{GMAIL_ID}+{time_stamp}-{email_user}@gmail.com'
    else:
        email = f'{GMAIL_ID}+{email_user}@gmail.com'
    return email


def webex_display_name(*, user: User):
    """
    For a given UCM user determine the display name to be used in Webex Calling
    Here we simply take the concatenation of first and last name
    :param user: UCM user
    :return: display name
    """
    display_name = f'{user.firstName} {user.lastName}'
    return display_name


def webex_extension(*, user: User) -> str:
    """
    For a given UCM user determine the extension to be used in Webex Calling
    Here we simply take the last four digit of the user's phone number
    :param user: UCM user
    :return: four digit extension
    """
    # last four digits
    return user.telephoneNumber.strip()[-4:]


def webex_did(*, user: User) -> str:
    """
    For a given UCM user determine the DID to be used in Webex Calling. NANP numbers are 10D on the public API
    :param user: UCM user
    :return: DID
    """
    r = user.telephoneNumber
    if r.startswith('+1'):
        r = r[2:]
    return r


async def user_provisioning(*, users: List[User]):
    """
    Provision a bunch of UCM users in Webex Calling
    :param users: list of UCM users
    :return:
    """

    async def provision_single_user(location: Location,
                                    user: User):
        """
        Provision a single Webex calling user
        :param location: Webex calling location to assign the user to
        :param user: UCM user information
        :return:
        """
        email = webex_email(user=user)
        people_list = await api.people.list(email=email)
        if people_list:
            log.info(f'{user.mailid}: user exists')
            return
        log.info(f'{user.mailid}: user does not exist')

        # check if the phone number of the user is available
        user_webex_did = webex_did(user=user)
        user_tn_plus_e164 = user.telephoneNumber
        if next((tn for tn in available_tns if tn.phone_number == user_tn_plus_e164), None) is None:
            log.info(f'{user.mailid}: TN {user_tn_plus_e164} is not available for provisioning in Webex Calling. '
                     f'Make sure the number has been added and is not assigned yet.')
            return

        user_extension = webex_extension(user=user)
        owner = owners.get(location.location_id, dict()).get(user_extension, None)
        owner: Optional[NumberOwner]
        if owner:
            log.info(f'{user.mailid}: extension {user_extension} is not available for provisioning in Webex Calling. '
                     f'Extension assigned to {owner.owner_type}: {owner.first_name} {owner.last_name}.')
            return

        if READONLY:
            log.info(f'{user.mailid}: Skipping provisioning b/c READONLY is set to True')
            return

        calling_license = allocate_calling_license(calling_license_list=calling_licenses)
        if calling_license is None:
            log.info(f'{user.mailid}: no calling license allocation available')
            return

        log.info(f'{user.mailid}: creating user')
        start = time.perf_counter()
        settings = Person(emails=[email],
                          display_name=webex_display_name(user=user),
                          first_name=user.firstName,
                          last_name=user.lastName)
        new_user = await api.people.create(settings=settings)
        log.info(f'{user.mailid}: creating user took {(time.perf_counter() - start) * 1000:.3f} ms')
        log.info(f'{user.mailid}: created user, id: {new_user.person_id}')
        licenses = new_user.licenses
        licenses.append(calling_license.license_id)

        # now we still need to add the calling license to the user and set the extension and DID
        phone_numbers = [PhoneNumber(number_type=PhoneNumberType.work, value=user_webex_did)]
        log.info(f'{user.mailid}: adding calling license ({calling_license.name}) and extension {user_extension}')
        start = time.perf_counter()
        # update user
        new_user.extension = user_extension
        new_user.location_id = location.location_id
        new_user.licenses = licenses
        phone_numbers = phone_numbers
        settings = Person(person_id=new_user.person_id,
                          display_name=new_user.display_name,
                          first_name=new_user.first_name,
                          last_name=new_user.last_name,
                          extension=user_extension,
                          location_id=location.location_id,
                          licenses=licenses,
                          phone_numbers=phone_numbers)
        updated = await api.people.update(person=settings, calling_data=True)
        if updated.errors:
            log.warning(f'{user.mailid}: errors: '
                        f'{", ".join(f"{error}/{code_and_reason.code}({code_and_reason.reason})" for error, code_and_reason in updated.errors.items())}')
        log.info(
            f'{user.mailid}: adding calling license and extension took {(time.perf_counter() - start) * 1000:.3f} ms')
        log.info(f'{user.mailid}: added calling license and extension, phone numbers: {updated.phone_numbers}')

    # provision the users
    async with AsWebexSimpleApi(tokens=WEBEX_TOKEN,
                                concurrent_requests=PARALLEL_TASKS) as api:
        start = time.perf_counter()

        # get calling license
        # get get_locations starting with 'SJC'
        # get TNs. TNs are +E.164
        calling_licenses, locations, numbers = await asyncio.gather(
            get_calling_licenses(api=api),
            api.locations.list(name='SJC'),
            api.telephony.phone_numbers()
        )
        calling_licenses: list[License]
        locations: list[Location]
        numbers: list[NumberListPhoneNumber]

        available_tns = [tn for tn in numbers
                         if tn.owner is None]

        log.info(f'Got {len(calling_licenses)} calling licenses with '
                 f'{sum(lic.total_units - lic.consumed_units for lic in calling_licenses)} available allocations')

        # extension_owners by location and extension
        owners: dict[str, dict[str, NumberOwner]] = defaultdict(dict)
        for extension in (tn for tn in numbers if tn.extension):
            owners[extension.location.location_id][extension.extension]=extension.owner

        # We are looking for a location 'SJC' that's where we want to put our users
        sjc_location = next((location
                             for location in locations
                             if location.name == 'SJC'), None)
        if sjc_location is None:
            log.info('Failed to get location "SJC"')
            return
        log.info(f'location "SJC", id: {sjc_location.location_id}')

        # try to figure out which phone numbers are missing
        available_tn_set = set(tn.phone_number for tn in available_tns)
        missing_user_tns = set(user.telephoneNumber for user in users
                               if user.telephoneNumber not in available_tn_set)
        if missing_user_tns:
            log.info(f'missing TNs: {", ".join(tn for tn in sorted(missing_user_tns))}')
            log.info(f'{len(missing_user_tns)} users with missing TNs:')
            log.info('\n'.join(
                f'  {user.firstName} {user.lastName} ({user.mailid}): {user.telephoneNumber}' for user in users
                if user.telephoneNumber in missing_user_tns))

        # filter out users where the TN is missing
        users = [user for user in users
                 if user.telephoneNumber not in missing_user_tns]
        if not users:
            log.info('Nothing left to do (no users)')
            return

        # b/c we only have limited licenses we pick some random users
        random.shuffle(users)
        users = users[:TEST_USERS_TO_PROVISION]
        users.sort(key=lambda u: f'{u.lastName:40}/{u.firstName:40}{u.mailid}')

        # Prepare list of provisioning tasks
        tasks = [provision_single_user(location=sjc_location,
                                       user=user)
                 for user in users]

        # schedule all tasks for execution and gather results
        results = await asyncio.gather(*tasks, return_exceptions=False)
        stop = time.perf_counter()
        log.info(f'Time to process {len(tasks)} user provisioning tasks: {(stop - start) * 1000:.3f}ms')

        for user, result in zip(users, results):
            if isinstance(result, Exception):
                log.info(f'Provisioning of user {user.mailid} failed: {result}')


async def validate_access_token():
    """
    Check whether the Webex access token is valid by tring to list users
    :return:
    """
    async with AsWebexSimpleApi(tokens=WEBEX_TOKEN) as api:
        try:
            await api.people.list(display_name='xyz')
        except Exception as e:
            log.info(f'Trying to get a list of users failed: {e}')
            log.info("""Make sure to obtain a valid access token from 
            https://developer.webex.com/docs/api/getting-started 
and put that token in your .env file in the main directory.""")
            exit(1)


def main():
    asyncio.run(validate_access_token())
    if READONLY:
        log.info(
            f'If you actually want this script to create users then you need to set READONLY to False in {__file__}')
    log.info('Preparing UCMReader...')
    with UCMReader(host=AXL_HOST, user=AXL_USER, password=AXL_PASSWORD) as ucm_reader:
        # get all users from UCM
        log.info('Getting users from UCM...')
        users = ucm_reader.user.list()

        # Let's check for consistent phone numbers and primary extensions
        users_ok = []
        users_nok = []
        for user in users:
            # user ok if
            # - user has a mail id
            # - the primary extension is set
            # - the pattern on the primary extension exists
            # - the primary extension pattern matches the user's phone number in +E.164; strip leading '\'
            if user.mailid and \
                    user.primaryExtension and \
                    user.primaryExtension.pattern and \
                    user.primaryExtension.pattern.strip('\\') == user.telephoneNumber:
                users_ok.append(user)
            else:
                users_nok.append(user)

        # group users by 1st five characters of their phone number
        users_per_npa = defaultdict(list)
        for user in users_ok:
            users_per_npa[user.telephoneNumber[:5]].append(user)
        for npa in users_per_npa:
            log.info(f'NPA {npa}: {len(users_per_npa[npa])} users')

        # let's focus on users in NPA 408
        users = users_per_npa['+1408']

    # we want to use asyncio to be able to provision multiple users "in parallel" b/c a single transaction
    # can take a while...
    asyncio.run(user_provisioning(users=users))


if __name__ == '__main__':
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # log to console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)

    # also log to file
    log_path = f'{os.path.splitext(__file__)[0]}.log'
    file_handler = logging.FileHandler(filename=log_path, mode='w')
    file_handler.setLevel(logging.DEBUG)
    file_fmt = logging.Formatter(fmt='%(asctime)s %(levelname)s %(name)s: %(message)s')
    file_fmt.converter = time.gmtime
    file_handler.setFormatter(file_fmt)
    root_logger.addHandler(file_handler)

    # set level for some loggers
    logging.getLogger('asyncio').setLevel(logging.INFO)
    logging.getLogger('ucmaxl').setLevel(logging.INFO)
    logging.getLogger('urllib3').setLevel(logging.INFO)
    logging.getLogger('zeep').setLevel(logging.INFO)
    logging.getLogger('zeep.transports').setLevel(logging.INFO)  # set this to DEBUG for SOAP messages
    logging.getLogger('ucm_reader.base').setLevel(logging.INFO)  # set this to DEBUG for ucm_reader transactions
    logging.getLogger('wxc_sdk.as_rest').setLevel(logging.DEBUG)  # set this to DEBUG for REST message details
    logging.getLogger('wxc_sdk.as_api').setLevel(logging.DEBUG)

    main()
