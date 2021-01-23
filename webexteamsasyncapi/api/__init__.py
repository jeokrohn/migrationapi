import logging

import aiohttp

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
