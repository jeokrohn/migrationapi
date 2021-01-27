import aiohttp
import asyncio
import uuid
import logging
import json as json_mod
import urllib.parse
import time

from typing import Callable, Dict, Tuple, Union, AsyncGenerator

from collections import defaultdict, UserDict
from dataclasses import dataclass, field

from .util import CamelModel

log = logging.getLogger(__name__)


class RestError(aiohttp.ClientResponseError):
    def __init__(self, request_body: Union[dict, str, None] = None, response_body: Union[dict, str, None] = None,
                 *args, **kwargs):
        super(RestError, self).__init__(*args, **kwargs)
        if isinstance(response_body, dict):
            response_body = json_mod.dumps(response_body)
        self.request_body = request_body
        self.response_body = response_body

    def pretty(self):
        yield f'{self.status} [{self.message}]: {self.request_info.method} {self.request_info.real_url}'
        for h, v in self.request_info.headers.items():
            if h == 'Authorization':
                v = 'Bearer ***'
            yield f'  {h}: {v}'
        if self.request_body:
            yield f'Body: {self.request_body}'

        yield 'Response:'
        for h, v in self.headers.items():
            yield f'  {h}: {v}'
        if self.response_body:
            yield f'Body: {self.response_body}'


def dump_response(log_id, response: aiohttp.ClientResponse, time_diff: float = None, response_data=None, data=None,
                  json=None, **kwargs) -> None:
    if not log.isEnabledFor(logging.DEBUG):
        return
    for h in response.history:
        dump_response(log_id=log_id, response=h)
    if time_diff is None:
        time_str = ''
    else:
        time_str = f', {time_diff * 1000:.3f}ms'
    log.debug(f'({log_id}) Request {response.status}[{response.reason}]{time_str}: '
              f'{response.request_info.method} {response.request_info.url}')

    for k, v in response.request_info.headers.items():
        if k == 'Authorization':
            v = 'Bearer ***'
        log.debug(f'({log_id})  {k}: {v}')

    if isinstance(data, dict):
        form_data = urllib.parse.quote_plus(urllib.parse.urlencode(data))
        log.debug(f'({log_id}) Body: {form_data}')
    elif isinstance(data, str):
        log.debug(f'({log_id}) Body: {data}')
    elif json:
        log.debug(f'({log_id}) Body: {json_mod.dumps(json)}')

    log.debug(f'({log_id}) Response')
    for k in response.headers:
        log.debug(f'({log_id})  {k}: {response.headers[k]}')
    if response_data:
        log.debug(f'({log_id}) {json_mod.dumps(response_data)}')


@dataclass
class MethodStat:
    """"
    Statistics for one HTTP method (GET, POST, ...)
    """
    requests: int = 0
    connection_errors: int = 0
    # counter for each status code (200, 429, ...)
    status: Dict[int, int] = field(default_factory=lambda: defaultdict(int))

    def __sub__(self, other: 'MethodStat'):
        r = MethodStat()
        r.requests = self.requests - other.requests
        r.connection_errors = self.connection_errors - other.connection_errors
        for status_code in set(self.status).union(other.status):
            delta = self.status[status_code] - other.status[status_code]
            if delta:
                r.status[status_code] = delta
        return r

    def copy(self) -> 'MethodStat':
        r = MethodStat()
        r.requests = self.requests
        r.connection_errors = self.connection_errors
        r.status = defaultdict(int, {k: v for k, v in self.status.items() if v})
        return r

    def __bool__(self):
        # anything relevant?
        return bool(self.requests or self.connection_errors or any(self.status.values()))


class RestStat(UserDict):
    """
    statistics for a REST session.
    Basically a defaultdict with MethodStat values
    """
    def __getitem__(self, key) -> MethodStat:
        try:
            item = super(RestStat, self).__getitem__(key=key)
        except KeyError:
            item = MethodStat()
            super(RestStat, self).__setitem__(key=key, item=item)
        return item

    def __sub__(self, other: 'RestStat'):
        if other is None:
            return self
        r = RestStat()
        for method in set(self).union(other):
            delta = self[method] - other[method]
            if delta:
                r[method] = delta
        return r

    @property
    def cumulative(self) -> MethodStat:
        r = MethodStat()
        for stat in self.values():
            r.requests += stat.requests
            r.connection_errors += stat.connection_errors
            for status, counted in stat.status.items():
                r.status[status] += counted
        return r

    def copy(self) -> 'RestStat':
        r = RestStat()
        r.data = {k: method_stat.copy() for k, method_stat in self.data.items() if method_stat}
        return r

    def snapshot(self) -> 'RestStat':
        return self.copy()

    def pretty(self):
        for method, stat in self.items():
            yield f'{method} requests:{stat.requests} connection errors:{stat.connection_errors} ' \
                  f'{" ".join(f"{status_code}:{count}" for status_code, count in stat.status.items() if count)}'


class RestSession:
    """
    Model a REST session
    """
    BASE = 'https://webexapis.com/v1'
    RETRIES_ON_CLIENT_CONNECTOR_ERRORS = 3
    RETRIES_ON_5XX = 3
    CONCURRENT_REQUESTS = 10
    MAX_WAIT_ON_429 = 20

    def __init__(self, access_token: str, base: str = None, session: aiohttp.ClientSession = None,
                 concurrent_request: int = None):
        self._access_token = access_token
        self._base = base or self.BASE
        concurrent_request = concurrent_request or self.CONCURRENT_REQUESTS
        if session:
            self._session = session
            self._close_session = False
        else:
            self._session = aiohttp.ClientSession(raise_for_status=False)
            self._close_session = True
        self._semaphore = asyncio.Semaphore(value=concurrent_request)
        self._session_stats = RestStat()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
        self._session = None

    async def close(self):
        if self._session and self._close_session:
            log.debug(f'{self}.close(): closing session')
            await self._session.close()
        self._session = None

    @property
    def _headers(self) -> Dict[str, str]:
        """
        Authorization header based on the access token of the API
        :return:
        """
        return {
            'Authorization': f'Bearer {self._access_token}',
            'Content-type': 'application/json;charset=utf-8'
        }

    async def request(self, method: str, url: str, success=None, headers=None,
                      data=None, json=None, **kwargs) -> Tuple[aiohttp.ClientResponse, dict]:
        """
        Execute one API request. Return the response and the JSON body as dict. Handles 429 and
        spurious ClientConnectorErrors
        :param method: GET, POST, PUT, ...
        :param url: url to access
        :param success: set of http response codes considered a 'success'
        :param headers: passed to aiohttp.request
        :param data: passed to aiohttp.request
        :param json: passed to aiohttp.request
        :param kwargs: additional arguments for aiohttp.request
        :return: tuple of response object and JSON body as dict
        """
        success = success or {200}
        client_connector_errors = 0
        status_5xx = 0
        log_id = uuid.uuid4()
        headers = headers or dict()
        headers.update(self._headers)
        headers['TrackingID'] = f'AsyncAPI_{log_id}'
        while True:
            # limit the number of concurrent requests
            async with self._semaphore:
                try:
                    start = time.perf_counter()
                    async with self._session.request(method, url, ssl=False, headers=headers, data=data, json=json,
                                                     **kwargs) as r:
                        self._session_stats[method].requests += 1
                        self._session_stats[method].status[r.status] += 1
                        if r.status in [502, 500]:
                            # sometimes requests simply fail... Retry
                            status_5xx += 1
                            if status_5xx <= self.RETRIES_ON_5XX:
                                dump_response(log_id=log_id, response=r)
                                log.warning(f'got {r.status}: retry ({status_5xx}/{self.RETRIES_ON_5XX}), '
                                            f'{method} {url} ')
                                continue
                        if r.status != 429:
                            ct = r.headers.get('Content-Type')
                            if not ct:
                                response_data = ''
                            elif ct.startswith('application/json'):
                                response_data = await r.json()
                            else:
                                response_data = await r.text()
                            stop = time.perf_counter()
                            dump_response(time_diff=stop - start, log_id=log_id, response=r,
                                          response_data=response_data, data=data, json=json)
                            if r.status not in success:
                                raise RestError(data or json,
                                                response_data,
                                                r.request_info,
                                                r.history,
                                                status=r.status,
                                                message=r.reason,
                                                headers=r.headers)
                            break
                except aiohttp.ClientConnectorError:
                    # retry on spurious ClientConnectorErrors
                    self._session_stats[method].connection_errors += 1
                    client_connector_errors += 1
                    if client_connector_errors <= self.RETRIES_ON_CLIENT_CONNECTOR_ERRORS:
                        log.warning(f'got ClientConnectorError: retry ({client_connector_errors}/'
                                    f'{self.RETRIES_ON_CLIENT_CONNECTOR_ERRORS}), '
                                    f'{method} {url} ')
                        continue
                    raise
                dump_response(log_id=log_id, response=r)

            # async with WebexTeamsAsyncAPI.semaphore
            # on 429 we need to wait some time and then retry
            # waiting has to happen outside of the context protected by the semaphore: we don't want to block
            # other tasks while we are waiting
            retry_after = int(r.headers.get('Retry-After', '5')) or 1
            # never wait more than the defined maximum
            retry_after = min(retry_after, self.MAX_WAIT_ON_429)
            log.warning(f'got 429: waiting for {retry_after} seconds, {method} {url} ')
            await asyncio.sleep(retry_after)
        # while True
        return r, response_data

    async def get(self, url: str, **kwargs) -> dict:
        _, data = await self.request('GET', url, **kwargs)
        return data

    async def put(self, url: str, data=None, json=None, **kwargs) -> dict:
        _, data = await self.request('PUT', url, data=data, json=json, **kwargs)
        return data

    async def post(self, url: str, data=None, json=None, **kwargs) -> dict:
        _, data = await self.request('POST', url, data=data, json=json, **kwargs)
        return data

    async def delete(self, url: str, **kwargs) -> dict:
        _, data = await self.request('DELETE', url, **kwargs)
        return data

    async def update(self, url: str, **kwargs) -> dict:
        _, data = await self.request('GET', url, **kwargs)
        return data

    def endpoint(self, domain: str) -> str:
        """
        get a full endpoint for a given domain
        :param domain: rooms, devices, people, ...
        :return: endpoint URL
        """
        return f'{self._base}/{domain}'

    async def pagination(self, url: str, params: dict,
                         factory: Callable[[Dict], CamelModel]) -> AsyncGenerator[CamelModel, None]:
        """
        Async iterator handling RFC5988 pagination of list requests
        :param url: start url for 1st GET
        :param params: params to be passed to initial GET; subsequent GETs are parameterized through next URL
        :param factory: factory method to create instances of returned objects
        :return: object instances created by factory
        """
        while url:
            log.debug(f'{self}.pagination: getting {url}')
            r, data = await self.request('GET', url, params=params)

            # parameters are only needed for the 1st call. The next url has parameters encoded
            params = dict()

            # try to get the next page (if present)
            try:
                url = str(r.links['next']['url'])
            except KeyError:
                url = None
            # return all items
            for i in data['items']:
                r = factory(i)
                yield r
            # for
        # while
        return

    @property
    def stats(self) -> RestStat:
        return self._session_stats
