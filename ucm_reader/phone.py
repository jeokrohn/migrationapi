from ucm_reader.base import AXLObject, StringAndUUID, ObjApi, GetRequired
from pydantic import BaseModel, Field
from typing import Optional, List, Any

__all__ = ['CurrentConfig', 'Phone', 'PhoneApi']


# noinspection SpellCheckingInspection
class CurrentConfig(BaseModel):
    userHoldMohAudioSourceId: Optional[str]
    phoneTemplateName: Optional[StringAndUUID]
    mlppDomainId: Optional[str]
    mlppIndicationStatus: Optional[str]
    preemption: Optional[str]
    softkeyTemplateName: Optional[StringAndUUID]
    ignorePresentationIndicators: Optional[str]
    singleButtonBarge: Optional[str]
    joinAcrossLines: Optional[str]
    callInfoPrivacyStatus: Optional[str]
    dndStatus: Optional[str]
    dndRingSetting: Optional[str]
    dndOption: Optional[str]
    alwaysUsePrimeLine: Optional[str]
    alwaysUsePrimeLineForVoiceMessage: Optional[str]
    emccCallingSearchSpaceName: Optional[StringAndUUID]
    deviceName: Optional[str]
    model: Optional[str]
    product: Optional[str]
    deviceProtocol: Optional[str]
    class_: str = Field(None, alias='class')
    addressMode: Optional[str]
    allowAutoConfig: Optional[str]
    remoteSrstOption: Optional[str]
    remoteSrstIp: Optional[str]
    remoteSrstPort: Optional[str]
    remoteSipSrstIp: Optional[str]
    remoteSipSrstPort: Optional[str]
    geolocationInfo: Optional[str]
    remoteLocationName: Optional[str]


class LoadInformation(BaseModel):
    special: bool


class ConfidentialAccess(BaseModel):
    confidentialAccessMode: Optional[str]
    confidentialAccessLevel: Optional[int]


class AssociatedEndUser(BaseModel):
    userId: str


# noinspection SpellCheckingInspection
class AssociatedEndUserContainer(BaseModel):
    enduser: List[AssociatedEndUser]


class CallInfoDisplay(BaseModel):
    callerName: bool
    callerNumber: bool
    redirectedNumber: bool
    dialedNumber: bool


class DN(BaseModel):
    pattern: str
    routePartitionName: StringAndUUID
    uuid: str


# noinspection SpellCheckingInspection
class Line(BaseModel):
    index: int
    label: Optional[str]
    display: Optional[str]
    dirn: DN
    # ringSetting: Optional[str]
    # consecutiveRingSetting: Optional[str]
    # ringSettingIdlePickupAlert: Optional[str]
    # ringSettingActivePickupAlert: Optional[str]
    displayAscii: Optional[str]
    e164Mask: Optional[str]
    # dialPlanWizardId: Optional[str]
    # mwlPolicy: Optional[str]
    # maxNumCalls: int
    # busyTrigger: int
    # callInfoDisplay: CallInfoDisplay
    # recordingProfileName: StringAndUUID
    # monitoringCssName: StringAndUUID
    # recordingFlag: Optional[str]
    # audibleMwi: Optional[str]
    speedDial: Optional[str]
    partitionUsage: Optional[str]
    associatedEndusers: Optional[AssociatedEndUserContainer]
    # missedCallLogging: bool
    # recordingMediaSource: Optional[str]


class LineContainer(BaseModel):
    line: List[Line]


# noinspection SpellCheckingInspection
class SpeedDial(BaseModel):
    dirn: str
    label: str
    index: int


# noinspection SpellCheckingInspection
class SpeedDialContainer(BaseModel):
    speeddial: List[SpeedDial]


# noinspection SpellCheckingInspection
class Phone(AXLObject):
    _axl_search = 'name'
    _axl_type = 'phone'

    name: Optional[str]
    description: Optional[str]
    product: Optional[str]
    model: Optional[str]
    class_: str = Field(None, alias='class')
    protocol: Optional[str]
    # protocolSide: Optional[str]
    callingSearchSpaceName: StringAndUUID
    devicePoolName: StringAndUUID
    commonDeviceConfigName: StringAndUUID
    commonPhoneConfigName: StringAndUUID
    networkLocation: Optional[str]
    locationName: StringAndUUID
    mediaResourceListName: StringAndUUID
    # networkHoldMohAudioSourceId: Optional[str]
    # userHoldMohAudioSourceId: Optional[str]
    # automatedAlternateRoutingCssName: StringAndUUID
    # aarNeighborhoodName: StringAndUUID
    # loadInformation: Optional[LoadInformation]
    # traceFlag: Optional[str]
    # mlppIndicationStatus: Optional[str]
    # preemption: Optional[str]
    # useTrustedRelayPoint: Optional[str]
    # retryVideoCallAsAudio: Optional[str]
    # securityProfileName: StringAndUUID
    sipProfileName: StringAndUUID
    cgpnTransformationCssName: StringAndUUID
    useDevicePoolCgpnTransformCss: Optional[str]
    # geoLocationName: StringAndUUID
    # geoLocationFilterName: StringAndUUID
    # sendGeoLocation: Optional[str]
    numberOfButtons: Optional[str]
    phoneTemplateName: StringAndUUID
    primaryPhoneName: StringAndUUID
    # ringSettingIdleBlfAudibleAlert: Optional[str]
    # ringSettingBusyBlfAudibleAlert: Optional[str]
    # userLocale: Optional[str]
    # networkLocale: Optional[str]
    # idleTimeout: Optional[str]
    # authenticationUrl: Optional[str]
    # directoryUrl: Optional[str]
    # idleUrl: Optional[str]
    # informationUrl: Optional[str]
    # messagesUrl: Optional[str]
    # proxyServerUrl: Optional[str]
    # servicesUrl: Optional[str]
    softkeyTemplateName: StringAndUUID
    loginUserId: Optional[str]
    defaultProfileName: StringAndUUID
    enableExtensionMobility: Optional[str]
    currentProfileName: StringAndUUID
    loginTime: Optional[str]
    loginDuration: Optional[str]
    # currentConfig: Optional[CurrentConfig]
    # singleButtonBarge: Optional[str]
    # joinAcrossLines: Optional[str]
    # builtInBridgeStatus: Optional[str]
    # callInfoPrivacyStatus: Optional[str]
    # hlogStatus: Optional[str]
    ownerUserName: StringAndUUID
    # ignorePresentationIndicators: Optional[str]
    # packetCaptureMode: Optional[str]
    # packetCaptureDuration: Optional[str]
    subscribeCallingSearchSpaceName: StringAndUUID
    rerouteCallingSearchSpaceName: StringAndUUID
    # allowCtiControlFlag: Optional[str]
    presenceGroupName: StringAndUUID
    # unattendedPort: Optional[str]
    # requireDtmfReception: Optional[str]
    # rfc2833Disabled: Optional[str]
    # certificateOperation: Optional[str]
    # authenticationMode: Optional[str]
    # keySize: Optional[str]
    # keyOrder: Optional[str]
    # ecKeySize: Optional[str]
    # authenticationString: Optional[str]
    # certificateStatus: Optional[str]
    # upgradeFinishTime: Optional[str]
    # deviceMobilityMode: Optional[str]
    # roamingDevicePoolName: StringAndUUID
    # remoteDevice: Optional[str]
    # dndOption: Optional[str]
    # dndRingSetting: Optional[str]
    # dndStatus: Optional[str]
    # isActive: Optional[str]
    # isDualMode: Optional[str]
    # mobilityUserIdName: StringAndUUID
    # phoneSuite: Optional[str]
    # phoneServiceDisplay: Optional[str]
    # isProtected: Optional[str]
    # mtpRequired: Optional[str]
    # mtpPreferedCodec: Optional[str]
    # dialRulesName: StringAndUUID
    # sshUserId: Optional[str]
    # digestUser: Optional[str]
    # outboundCallRollover: Optional[str]
    # hotlineDevice: Optional[str]
    # secureInformationUrl: Optional[str]
    # secureDirectoryUrl: Optional[str]
    # secureMessageUrl: Optional[str]
    # secureServicesUrl: Optional[str]
    # secureAuthenticationUrl: Optional[str]
    # secureIdleUrl: Optional[str]
    # alwaysUsePrimeLine: Optional[str]
    # alwaysUsePrimeLineForVoiceMessage: Optional[str]
    # featureControlPolicy: StringAndUUID
    # deviceTrustMode: Optional[str]
    # earlyOfferSupportForVoiceCall: Optional[str]
    # requireThirdPartyRegistration: Optional[str]
    # blockIncomingCallsWhenRoaming: Optional[str]
    # homeNetworkId: Optional[str]
    # AllowPresentationSharingUsingBfcp: Optional[str]
    # confidentialAccess: Optional[ConfidentialAccess]
    # requireOffPremiseLocation: Optional[str]
    # allowiXApplicableMedia: Optional[str]
    # enableCallRoutingToRdWhenNoneIsActive: Optional[str]
    # enableActivationID: Optional[str]
    # mraServiceDomain: StringAndUUID
    # allowMraMode: Optional[str]
    ctiid: Optional[str]
    uuid: Optional[str]

    # the following attributed require an AXL get
    lines: Optional[LineContainer] = GetRequired
    speeddials: Optional[SpeedDialContainer] = GetRequired
    busyLampFields: Any = GetRequired
    blfDirectedCallParks: Any = GetRequired


class PhoneApi(ObjApi):
    def __init__(self, zeep_service):
        super(PhoneApi, self).__init__(zeep_service)
        self._list = None

    def list(self, refresh=False) -> List[Phone]:
        if refresh or self._list is None:
            self._list = Phone.do_list(obj_api=self)
        return self._list
