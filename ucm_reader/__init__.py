from ucmaxl import AXLHelper
import urllib3
from pydantic import BaseModel, Field

from typing import List, Iterable, Optional
import zeep.helpers
import zeep.exceptions
import re


class AXLObject(BaseModel):

    @classmethod
    def tags(cls) -> Iterable[str]:
        """
        Iterable over names of all atrtibutes of the class
        :return:
        """
        return (field.name for field in cls.__fields__.values())

    @classmethod
    def list(cls, list_call, search_attribute: str, first=None, skip=None):
        try:
            zeep_response = list_call(searchCriteria={search_attribute: '%'},
                                      returnedTags={t: '' for t in cls.tags()},
                                      first=first,
                                      skip=skip)
        except zeep.exceptions.Fault as e:
            # check if we need to restrict the query to smaller sets
            # Error to look for is something like:
            # 'Query request too large. Total rows matched: 1277 rows. Suggestive Row Fetch: less than 953 rows'
            message = e.message
            if (m := re.match(r'Query request too large\. Total rows matched: (\d+) rows\. '
                              r'Suggested row fetch: less than (\d+) rows',
                              message)):
                total_rows = int(m.group(1))
                batch_size = int(m.group(2))
                batch_size = int(batch_size * 0.7)
                result = []
                for skip in range(0, total_rows, batch_size):
                    batch = cls.list(list_call, search_attribute, first=batch_size, skip=skip)
                    result.extend(batch)
                return result
            else:
                raise
        if zeep_response['return'] is None:
            return []
        zeep_response = zeep_response['return'][next((r for r in zeep_response['return']))]
        result = []
        for zeep_object in zeep_response:
            d = zeep.helpers.serialize_object(zeep_object)
            filtered = {tag: d[tag] for tag in cls.tags()}
            # create object from values
            o = cls.parse_obj(filtered)
            result.append(o)
        return result


class StringAndUUID(BaseModel):
    value: str = Field(None, alias='_value_1')
    uuid: Optional[str]


class PrimaryExtension(BaseModel):
    pattern: Optional[str]
    routePartitionName: Optional[str]


class UCMUser(AXLObject):
    firstName: Optional[str]
    middleName: Optional[str]
    lastName: Optional[str]
    userid: Optional[str]
    mailid: Optional[str]
    department: Optional[str]
    manager: Optional[str]
    userLocale: Optional[str]
    primaryExtension: PrimaryExtension
    associatedPc: Optional[str]
    enableCti: Optional[str]
    subscribeCallingSearchSpaceName: StringAndUUID
    enableMobility: Optional[str]
    enableMobileVoiceAccess: Optional[str]
    maxDeskPickupWaitTime: Optional[str]
    remoteDestinationLimit: Optional[str]
    status: Optional[str]
    enableEmcc: Optional[str]
    patternPrecedence: Optional[str]
    numericUserId: Optional[str]
    mlppPassword: Optional[str]
    homeCluster: Optional[str]
    imAndPresenceEnable: Optional[str]
    serviceProfile: StringAndUUID
    directoryUri: Optional[str]
    telephoneNumber: Optional[str]
    title: Optional[str]
    mobileNumber: Optional[str]
    homeNumber: Optional[str]
    pagerNumber: Optional[str]
    calendarPresence: Optional[str]
    userIdentity: Optional[str]
    uuid: str


class UCMReader:
    def __init__(self, host: str, user: str, password: str):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self._axl = AXLHelper(ucm_host=host, auth=(user, password), verify=False)
        self._users = None

    @property
    def users(self) -> List[UCMUser]:
        if self._users is None:
            self._users = UCMUser.list(self._axl.service.listUser, 'userid')
        return self._users

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
