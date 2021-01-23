from ucm_reader.base import AXLObject, ObjApi
from typing import Optional, List

__all__ = ['Location', 'LocationApi']


class Location(AXLObject):
    _axl_search = 'name'
    _axl_type = 'location'

    uuid: str
    name: Optional[str]
    id: Optional[int]
    withinAudioBandwidth: Optional[int]
    withinVideoBandwidth: Optional[int]
    # noinspection SpellCheckingInspection
    withinImmersiveKbits: Optional[int]

    pass


class LocationApi(ObjApi):
    def __init__(self, zeep_service):
        super(LocationApi, self).__init__(zeep_service)
        self._list = None

    def list(self, refresh=False) -> List[Location]:
        if refresh or self._list is None:
            self._list = Location.do_list(obj_api=self)
        return self._list
