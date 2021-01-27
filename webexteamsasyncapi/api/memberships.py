from typing import AsyncGenerator

from ..rest import RestSession
from ..util import to_camel, CamelModel


class Membership(CamelModel):
    id: str
    room_id: str
    person_id: str
    person_email: str
    person_display_name: str
    person_org_id: str
    is_moderator: bool
    is_monitor: bool
    is_room_hidden: bool
    created: str


class MembershipAPI:
    def __init__(self, session: RestSession):
        self._session = session
        self._endpoint = self._session.endpoint('memberships')

    def list(self, room_id: str = None,
             person_id: str = None,
             person_email: str = None,
             max: int = None) -> AsyncGenerator[Membership, None]:
        params = {to_camel(k): v for k, v in locals().items() if v is not None and k != 'self'}

        url = self._endpoint
        # noinspection PyTypeChecker
        return self._session.pagination(url=url, params=params, factory=Membership.parse_obj)

    async def create(self, room_id: str,
                     person_id: str = None,
                     person_email: str = None,
                     is_moderator: bool = None) -> Membership:
        assert person_id or person_email, 'One of peerson_id and person_email needs to be provided'
        params = {to_camel(k): v for k, v in locals().items() if v is not None and k != 'self'}
        url = self._endpoint
        r = await self._session.post(url=url, json=params)
        return Membership.parse_obj(r)

    async def details(self, membership_id: str) -> Membership:
        url = f'{self._endpoint}/{membership_id}'
        r = await self._session.get(url)
        return Membership.parse_obj(r)

    async def update(self, membership_id: str, is_moderator: bool) -> Membership:
        url = f'{self._endpoint}/{membership_id}'
        data = {'isModerator': is_moderator}
        r = await self._session.put(url, json=data)
        return Membership.parse_obj(r)

    async def delete(self, membership_id: str) -> None:
        url = f'{self._endpoint}/{membership_id}'
        await self._session.delete(url, success={204})
