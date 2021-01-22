from ucm_reader.base import AXLObject, StringAndUUID, ObjApi
from pydantic import BaseModel, Field
from typing import Optional, List, Any
import zeep.helpers

__all__ = ['CurrentConfig', 'Phone', 'PhoneApi']


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


class Phone(AXLObject):
    name: Optional[str]
    description: Optional[str]
    product: Optional[str]
    model: Optional[str]
    class_: str = Field(None, alias='class')
    protocol: Optional[str]
    #protocolSide: Optional[str]
    callingSearchSpaceName: StringAndUUID
    devicePoolName: StringAndUUID
    commonDeviceConfigName: StringAndUUID
    commonPhoneConfigName: StringAndUUID
    networkLocation: Optional[str]
    locationName: StringAndUUID
    mediaResourceListName: StringAndUUID
    #networkHoldMohAudioSourceId: Optional[str]
    #userHoldMohAudioSourceId: Optional[str]
    #automatedAlternateRoutingCssName: StringAndUUID
    #aarNeighborhoodName: StringAndUUID
    #loadInformation: Optional[LoadInformation]
    #traceFlag: Optional[str]
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


class AssociatedEndUser(BaseModel):
    userId: str


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


class PhoneDetails(Phone):
    # vendorConfig: Any
    # versionStamp: Any
    # mlppDomainId: Any
    lines: Optional[LineContainer]
    speeddials: Any
    busyLampFields: Any
    blfDirectedCallParks: Any
    # addOnModules: Any
    # services: Any
    # sshPwd: Any
    # cgpnIngressDN: StringAndUUID
    # useDevicePoolCgpnIngressDN: bool
    # msisdn: Any
    # wifiHotspotProfile: StringAndUUID
    # wirelessLanProfileGroup: StringAndUUID
    # elinGroup: StringAndUUID
    # activationIDStatus: Any


"""
class RPhone:
    name: str
    description: str
    product: str
    model: str
    class_: str
    protocol: str
    protocolSide: str
    callingSearchSpaceName: str
    devicePoolName: str
    commonDeviceConfigName: str
    commonPhoneConfigName: str
    networkLocation: str
    locationName: str
    mediaResourceListName: str
    networkHoldMohAudioSourceId: str
    userHoldMohAudioSourceId: str
    automatedAlternateRoutingCssName: str
    aarNeighborhoodName: str
    loadInformation: str
        vendorConfig: str
        versionStamp: str
    traceFlag: str
        mlppDomainId: str
    mlppIndicationStatus: str
    preemption: str
    useTrustedRelayPoint: str
    retryVideoCallAsAudio: str
    securityProfileName: str
    sipProfileName: str
    cgpnTransformationCssName: str
    useDevicePoolCgpnTransformCss: str
    geoLocationName: str
    geoLocationFilterName: str
    sendGeoLocation: str
        lines: str
    numberOfButtons: str
    phoneTemplateName: str
        speeddials: str
        busyLampFields: str
    primaryPhoneName: str
    ringSettingIdleBlfAudibleAlert: str
    ringSettingBusyBlfAudibleAlert: str
        blfDirectedCallParks: str
        addOnModules: str
    userLocale: str
    networkLocale: str
    idleTimeout: str
    authenticationUrl: str
    directoryUrl: str
    idleUrl: str
    informationUrl: str
    messagesUrl: str
    proxyServerUrl: str
    servicesUrl: str
        services: str
    softkeyTemplateName: str
    loginUserId: str
    defaultProfileName: str
    enableExtensionMobility: str
    currentProfileName: str
    loginTime: str
    loginDuration: str
    currentConfig: str
    singleButtonBarge: str
    joinAcrossLines: str
    builtInBridgeStatus: str
    callInfoPrivacyStatus: str
    hlogStatus: str
    ownerUserName: str
    ignorePresentationIndicators: str
    packetCaptureMode: str
    packetCaptureDuration: str
    subscribeCallingSearchSpaceName: str
    rerouteCallingSearchSpaceName: str
    allowCtiControlFlag: str
    presenceGroupName: str
    unattendedPort: str
    requireDtmfReception: str
    rfc2833Disabled: str
    certificateOperation: str
    authenticationMode: str
    keySize: str
    keyOrder: str
    ecKeySize: str
    authenticationString: str
    certificateStatus: str
    upgradeFinishTime: str
    deviceMobilityMode: str
    roamingDevicePoolName: str
    remoteDevice: str
    dndOption: str
    dndRingSetting: str
    dndStatus: str
    isActive: str
    isDualMode: str
    mobilityUserIdName: str
    phoneSuite: str
    phoneServiceDisplay: str
    isProtected: str
    mtpRequired: str
    mtpPreferedCodec: str
    dialRulesName: str
    sshUserId: str
        sshPwd: str
    digestUser: str
    outboundCallRollover: str
    hotlineDevice: str
    secureInformationUrl: str
    secureDirectoryUrl: str
    secureMessageUrl: str
    secureServicesUrl: str
    secureAuthenticationUrl: str
    secureIdleUrl: str
    alwaysUsePrimeLine: str
    alwaysUsePrimeLineForVoiceMessage: str
    featureControlPolicy: str
    deviceTrustMode: str
    earlyOfferSupportForVoiceCall: str
    requireThirdPartyRegistration: str
    blockIncomingCallsWhenRoaming: str
    homeNetworkId: str
    AllowPresentationSharingUsingBfcp: str
    confidentialAccess: str
    requireOffPremiseLocation: str
    allowiXApplicableMedia: str
        cgpnIngressDN: str
        useDevicePoolCgpnIngressDN: str
        msisdn: str
    enableCallRoutingToRdWhenNoneIsActive: str
        wifiHotspotProfile: str
        wirelessLanProfileGroup: str
        elinGroup: str
    enableActivationID: str
        activationIDStatus: str
    mraServiceDomain: str
    allowMraMode: str
"""


class PhoneApi(ObjApi):
    def __init__(self, zeep_service):
        super(PhoneApi, self).__init__(zeep_service)
        self._list = None

    def list(self, refresh=False) -> List[Phone]:
        if refresh or self._list is None:
            self._list = Phone.do_list(self.service.listPhone, 'name')
        return self._list

    def details(self, phone: Phone) -> PhoneDetails:
        print(f'details(){phone.uuid}')
        rt = {field: '' for field in PhoneDetails.__fields__}
        r = self.service.getPhone(uuid=phone.uuid)
        serialized = zeep.helpers.serialize_object(r['return']['phone'])
        o = PhoneDetails.parse_obj(serialized)
        return o
