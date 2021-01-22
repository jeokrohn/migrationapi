import logging
from typing import Optional, AsyncIterator, List

import aiohttp
import webexteamssdk

from .licenses import LicensesAPI
from .locations import LocationsAPI
from .memberships import MembershipAPI
from .people import PeopleAPI
from .rooms import RoomsAPI
from ..rest import RestSession

log = logging.getLogger(__name__)


class WebexTeamsAsyncAPI:
    """
    Basis asynchronous Webex Teams API handler
    """

    def __init__(self, access_token: str, base: str = None, concurrent_requests: int = None,
                 session: aiohttp.ClientSession = None):
        self._rest_session = RestSession(access_token=access_token, session=session, base=base,
                                         concurrent_request=concurrent_requests)
        self.people = PeopleAPI(self._rest_session)
        self.licenses = LicensesAPI(self._rest_session)
        self.locations = LocationsAPI(self._rest_session)
        self.memberships = MembershipAPI(self._rest_session)
        self.rooms = RoomsAPI(self._rest_session)

    async def close(self):
        log.debug(f'{self}.close()')
        await self._rest_session.close()

    async def __aenter__(self) -> 'WebexTeamsAsyncAPI':
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    @property
    def rest_session(self) -> RestSession:
        return self._rest_session

    # messages
    @property
    def messages_endpoint(self):
        return self._rest_session.endpoint('messages')

    def list_messages(self, p_roomId: Optional[str] = None,
                      p_mentionedPeople: Optional[List[str]] = None,
                      p_before: Optional[str] = None,
                      p_beforeMessage: Optional[str] = None,
                      p_max: Optional[int] = None) -> AsyncIterator[webexteamssdk.Message]:
        params = {k[2:]: v for k, v in locals().items() if k.startswith('p_') and v is not None}
        return self._rest_session.pagination(url=self.messages_endpoint, params=params, factory=webexteamssdk.Message)

    def list_direct_messages(self, p_personId: Optional[str] = None,
                             p_personEmail: Optional[str] = None) -> AsyncIterator[webexteamssdk.Message]:
        params = {k[2:]: v for k, v in locals().items() if k.startswith('p_') and v is not None}
        url = f'{self.messages_endpoint}/direct'
        return self._rest_session.pagination(url=url, params=params, factory=webexteamssdk.Message)

    async def create_message(self, p_roomId: Optional[str] = None, p_toPersonId: Optional[str] = None,
                             p_toPersonEmail: Optional[str] = None, p_text: Optional[str] = None,
                             p_markdown: Optional[str] = None) -> webexteamssdk.Message:
        params = {k[2:]: v for k, v in locals().items() if k.startswith('p_') and v is not None}
        url = f'{self.messages_endpoint}'
        r = await self._rest_session.post(url=url, json=params)
        return webexteamssdk.Message(r)

    async def get_message_detail(self, p_messageId: str) -> webexteamssdk.Message:
        url = f'{self.messages_endpoint}/{p_messageId}'
        r = await self._rest_session.get(url=url)
        return webexteamssdk.Message(r)

    async def delete_message(self, p_messageId: str) -> None:
        url = f'{self.messages_endpoint}/{p_messageId}'
        await self._rest_session.delete(url=url)
        return
