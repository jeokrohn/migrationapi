from typing import AsyncGenerator, Optional

from ..rest import RestSession
from ..util import to_camel, CamelModel


class Room(CamelModel):
    id: str
    title: str
    type: str
    is_locked: bool
    team_id: Optional[str]
    last_activity: Optional[str]
    creator_id: str
    created: str
    owner_id: Optional[str]


class MeetingDetails(CamelModel):
    """
    Return value of space_meeting_details() call
    """
    room_id: str
    meeting_link: str
    sip_address: str
    meeting_number: str
    call_in_toll_free_number: str
    call_in_toll_number: str


class RoomsAPI:
    def __init__(self, session: RestSession):
        self._session = session
        self._endpoint = self._session.endpoint('rooms')

    def list(self, team_id: str = None,
             type: str = None,
             sort_by: str = None,
             max: int = None) -> AsyncGenerator[Room, None]:
        assert type is None or type in ['direct', 'group']
        assert sort_by is None or sort_by in ['id', 'lastactivity', 'Created']
        params = {to_camel(k): v for k, v in locals().items() if v is not None and k != 'self'}

        url = self._endpoint
        # noinspection PyTypeChecker
        return self._session.pagination(url=url, params=params, factory=Room.parse_obj)

    async def create(self, title: str, team_id: str = None) -> Room:
        params = {to_camel(k): v for k, v in locals().items() if v is not None and k != 'self'}
        url = self._endpoint
        r = await self._session.post(url=url, json=params)
        return Room.parse_obj(r)

    async def details(self, room_id: str) -> Room:
        url = f'{self._endpoint}/{room_id}'
        r = await self._session.get(url)
        return Room.parse_obj(r)

    async def meeting_details(self, room_id: str) -> MeetingDetails:
        url = f'{self._endpoint}/{room_id}/meetingInfo'
        r = await self._session.get(url)
        return MeetingDetails.parse_obj(r)

    async def update(self, room_id: str, title: str) -> Room:
        url = f'{self._endpoint}/{room_id}'
        data = {'title': title}
        r = await self._session.put(url, json=data)
        return Room.parse_obj(r)

    async def delete(self, room_id: str) -> None:
        url = f'{self._endpoint}/{room_id}'
        await self._session.delete(url, success={204})
