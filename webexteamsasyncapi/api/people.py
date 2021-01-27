from typing import Optional, AsyncGenerator, List

from ..rest import RestSession
from ..util import to_camel, CamelModel


class PhoneNumber(CamelModel):
    type: str
    value: str


class SipAddress(CamelModel):
    type: str
    value: str
    primary: bool


class Person(CamelModel):
    id: str
    emails: List[str]
    phone_numbers: Optional[List[PhoneNumber]]
    extension: Optional[str]
    location_id: Optional[str]
    sip_addresses: Optional[List[SipAddress]]
    display_name: str
    nick_name: str
    first_name: Optional[str]
    last_name: Optional[str]
    avatar: Optional[str]
    org_id: str
    roles: List[str]
    licenses: List[str]
    created: str
    last_modified: str
    timezone: Optional[str]
    last_activity: Optional[str]
    status: str
    invite_pending: bool
    login_enabled: bool
    type: str

    @property
    def work_phone(self) -> Optional[str]:
        if not self.phone_numbers:
            return None
        return next((p.value for p in self.phone_numbers if p.type == 'work'), None)


class PeopleAPI:
    def __init__(self, session: RestSession):
        self._session = session
        self._endpoint = self._session.endpoint('people')

    def list(self, email: str = None, display_name: str = None,
             id: str = None,
             org_id: str = None, max: int = None) -> AsyncGenerator[Person, None]:

        params = {to_camel(k): v for k, v in locals().items() if v is not None}
        params.pop('self')

        url = self._endpoint
        # noinspection PyTypeChecker
        return self._session.pagination(url=url, params=params, factory=Person.parse_obj)

    async def create(self, emails: List[str], display_name: str = None,
                     first_name: str = None,
                     last_name: str = None, avatar: str = None,
                     org_id: str = None,
                     roles: Optional[List[str]] = None,
                     licenses: Optional[List[str]] = None,
                     location_id: Optional[str] = None) -> Person:
        params = {to_camel(k): v for k, v in locals().items() if k != 'self' and v is not None}
        url = self._endpoint
        r = await self._session.post(url=url, json=params)
        return Person.parse_obj(r)

    async def details(self, person_id: str, calling_data: bool = False) -> Person:
        url = f'{self._endpoint}/{person_id}'
        if calling_data:
            params = {'callingData': 'true'}
        else:
            params = None
        r = await self._session.get(url, params=params)
        return Person.parse_obj(r)

    async def update(self, person_id: str, first_name: str, last_name: str, display_name: str,
                     emails: List[str] = None,
                     phone_numbers: Optional[List[PhoneNumber]] = None,
                     extension: str = None,
                     avatar=None, roles=None,
                     licenses: List[str] = None,
                     location_id: Optional[str] = None,
                     calling_data: bool = False) -> Person:

        assert licenses is not None, 'To clear licenses pass am empty list'
        if phone_numbers:
            phone_numbers = [p.dict() for p in phone_numbers]
        data = {to_camel(k): v for k, v in locals().items() if
                k not in ['self', 'person_id', 'calling_data'] and v is not None}

        url = f'{self._endpoint}/{person_id}'
        if calling_data:
            params = dict(callingData='true')
        else:
            params = None
        r = await self._session.put(url, json=data, params=params)
        return Person.parse_obj(r)

    async def delete(self, person_id) -> None:
        url = f'{self._endpoint}/{person_id}'
        await self._session.delete(url, success={204})

    async def me(self):
        url = f'{self._endpoint}/me'
        r = await self._session.get(url)
        return Person.parse_obj(r)
