from ucm_reader.base import AXLObject, StringAndUUID, ObjApi, GetRequired
from pydantic import BaseModel
from typing import Optional, List

__all__ = ['User', 'UserApi']


class PrimaryExtension(BaseModel):
    pattern: Optional[str]
    routePartitionName: Optional[str]


# noinspection SpellCheckingInspection
class User(AXLObject):
    _axl_search = 'userid'
    _axl_type = 'user'

    firstName: Optional[str]
    middleName: Optional[str]
    lastName: Optional[str]
    userid: Optional[str]
    mailid: Optional[str]
    department: Optional[str]
    manager: Optional[str]
    # userLocale: Optional[str]
    primaryExtension: Optional[PrimaryExtension]
    # associatedPc: Optional[str]
    # enableCti: Optional[str]
    # subscribeCallingSearchSpaceName: StringAndUUID
    # enableMobility: Optional[str]
    # enableMobileVoiceAccess: Optional[str]
    # maxDeskPickupWaitTime: Optional[str]
    # remoteDestinationLimit: Optional[str]
    # status: Optional[str]
    # enableEmcc: Optional[str]
    # patternPrecedence: Optional[str]
    # numericUserId: Optional[str]
    # mlppPassword: Optional[str]
    # homeCluster: Optional[str]
    # imAndPresenceEnable: Optional[str]
    # serviceProfile: StringAndUUID
    directoryUri: Optional[str]
    telephoneNumber: Optional[str]
    title: Optional[str]
    mobileNumber: Optional[str]
    homeNumber: Optional[str]
    pagerNumber: Optional[str]
    # calendarPresence: Optional[str]
    userIdentity: Optional[str]
    uuid: str

    # the following attributed require an AXL get
    convertUserAccount: Optional[StringAndUUID] = GetRequired


class UserApi(ObjApi):
    def __init__(self, zeep_service):
        super(UserApi, self).__init__(zeep_service)
        self._list: Optional[List[User]] = None

    def list(self, refresh=False) -> List[User]:
        """
        Get list of UCM users. Retrieve the list from UCM on 1st call
        :param refresh: if True then don't return cached list and instead re-read the list from UCM via AXl
        :return:
        """
        if refresh or self._list is None:
            self._list = User.do_list(obj_api=self)
        return self._list
