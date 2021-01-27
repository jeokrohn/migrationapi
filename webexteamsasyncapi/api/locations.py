from typing import AsyncGenerator

from ..rest import RestSession
from ..util import to_camel, CamelModel


class LocationAddress(CamelModel):
    address1: str
    address2: str
    city: str
    state: str
    postal_code: str
    country: str


class Location(CamelModel):
    id: str
    name: str
    org_id: str
    address: LocationAddress


class LocationsAPI:
    def __init__(self, session: RestSession):
        self._session = session
        self._endpoint = self._session.endpoint('locations')

    def list(self, name: str = None, id: str = None, max: int = None) -> AsyncGenerator[Location, None]:
        data = {to_camel(k): v for k, v in locals().items() if k != 'self' and v is not None}
        url = f'{self._endpoint}'
        # noinspection PyTypeChecker
        return self._session.pagination(url=url, params=data, factory=Location.parse_obj)

    async def details(self, location_id) -> Location:
        url = f'{self._endpoint}/{location_id}'
        data = await self._session.get(url=url)
        location = Location.parse_obj(data)
        return location
