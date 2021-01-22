from ucm_reader.base import AXLObject, StringAndUUID, ObjApi
from pydantic import BaseModel
from typing import Optional, List

__all__ = ['PrimaryExtension', 'User', 'UserApi']


class PrimaryExtension(BaseModel):
    pattern: Optional[str]
    routePartitionName: Optional[str]


class User(AXLObject):
    firstName: Optional[str]
    middleName: Optional[str]
    lastName: Optional[str]
    userid: Optional[str]
    mailid: Optional[str]
    department: Optional[str]
    manager: Optional[str]
    #userLocale: Optional[str]
    primaryExtension: PrimaryExtension
    #associatedPc: Optional[str]
    #enableCti: Optional[str]
    #subscribeCallingSearchSpaceName: StringAndUUID
    #enableMobility: Optional[str]
    #enableMobileVoiceAccess: Optional[str]
    #maxDeskPickupWaitTime: Optional[str]
    #remoteDestinationLimit: Optional[str]
    #status: Optional[str]
    #enableEmcc: Optional[str]
    #patternPrecedence: Optional[str]
    #numericUserId: Optional[str]
    #mlppPassword: Optional[str]
    #homeCluster: Optional[str]
    #imAndPresenceEnable: Optional[str]
    #serviceProfile: StringAndUUID
    directoryUri: Optional[str]
    telephoneNumber: Optional[str]
    title: Optional[str]
    mobileNumber: Optional[str]
    homeNumber: Optional[str]
    pagerNumber: Optional[str]
    #calendarPresence: Optional[str]
    userIdentity: Optional[str]
    uuid: str


class UserApi(ObjApi):
    def __init__(self, zeep_service):
        super(UserApi, self).__init__(zeep_service)
        self._list = None

    def list(self, refresh=False) -> List[User]:
        if refresh or self._list is None:
            self._list = User.do_list(self.service.listUser, 'userid')
        return self._list
