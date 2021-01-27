from typing import AsyncGenerator, Optional

from ..rest import RestSession
from ..util import to_camel, CamelModel


class License(CamelModel):
    id: str
    name: str
    total_units: int
    consumed_units: int
    subscription_id: Optional[str]
    site_url: Optional[str]
    site_type: Optional[str]


class LicensesAPI:
    def __init__(self, session: RestSession):
        self._session = session
        self._endpoint = self._session.endpoint('licenses')

    def list(self, org_id: str = None) -> AsyncGenerator[License, None]:
        data = {to_camel(k): v for k, v in locals().items() if k != 'self' and v is not None}
        url = f'{self._endpoint}'
        # noinspection PyTypeChecker
        return self._session.pagination(url=url, params=data, factory=License.parse_obj)

    async def details(self, license_id) -> License:
        url = f'{self._endpoint}/{license_id}'
        data = await self._session.get(url=url)
        license = License.parse_obj(data)
        return license
