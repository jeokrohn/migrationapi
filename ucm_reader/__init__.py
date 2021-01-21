from ucmaxl import AXLHelper
import urllib3
from dataclasses import dataclass, fields, Field, is_dataclass

from typing import List, Iterable
import zeep.helpers


@dataclass
class AXLObject:

    @classmethod
    def tags(cls) -> Iterable[str]:
        """
        Iterable over names of all atrtibutes of the class
        :return:
        """
        field: Field
        return (field.name for field in fields(cls))

    @classmethod
    def from_dict(cls, data):
        """
        Create an object from a dictionary. Allows attributes to be dataclasses
        :param data:
        :return:
        """
        init_values = {}
        for field in fields(cls):
            field: Field
            name = field.name
            value = data[name]
            if is_dataclass(field.type):
                value = field.type(**value)
            init_values[name] = value
            foo = 1
        return cls(**init_values)

    @classmethod
    def list(cls, list_call, search_attribute: str):
        zeep_response = list_call(searchCriteria={search_attribute: '%'},
                                  returnedTags={t: '' for t in cls.tags()})
        if zeep_response['return'] is None:
            return []
        zeep_response = zeep_response['return'][next((r for r in zeep_response['return']))]
        result = []
        for zeep_object in zeep_response:
            d = zeep.helpers.serialize_object(zeep_object)
            # create object from values
            o = cls.from_dict(d)
            result.append(o)
        return result



@dataclass
class StringAndUUID:
    _value_1:str
    uuid:str
    @property
    def value(self):
        return self._value_1

@dataclass
class PrimaryExtension:
    pattern: str
    routePartitionName: str

@dataclass
class UCMUser(AXLObject):
    firstName: str
    middleName: str
    lastName: str
    userid: str
    mailid: str
    department: str
    manager: str
    userLocale: str
    primaryExtension: PrimaryExtension
    associatedPc: str
    enableCti: str
    subscribeCallingSearchSpaceName: StringAndUUID
    enableMobility: str
    enableMobileVoiceAccess: str
    maxDeskPickupWaitTime: str
    remoteDestinationLimit: str
    status: str
    enableEmcc: str
    patternPrecedence: str
    numericUserId: str
    mlppPassword: str
    homeCluster: str
    imAndPresenceEnable: str
    serviceProfile: StringAndUUID
    directoryUri: str
    telephoneNumber: str
    title: str
    mobileNumber: str
    homeNumber: str
    pagerNumber: str
    calendarPresence: str
    userIdentity: str
    uuid: str


class UCMReader:
    def __init__(self, host: str, user: str, password: str):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self._axl = AXLHelper(ucm_host=host, auth=(user, password), verify=False)
        self._users = None

        pass

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
