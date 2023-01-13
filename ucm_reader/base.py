from pydantic import BaseModel, Field
import zeep.exceptions
import zeep.helpers
import re
import logging

from typing import Optional, Generator

__all__ = ['AXLObject', 'StringAndUUID', 'ObjApi', 'GetRequired']

# Field definition for attributes which require an AXL get
GetRequired = Field(None, get_required=True)

log = logging.getLogger(__name__)


class AXLObject(BaseModel):
    _axl_type: Optional[str] = None
    _axl_search: Optional[str] = None

    class Config:
        extra = 'allow'

    def __init_subclass__(cls, **kwargs):
        super(AXLObject, cls).__init_subclass__(**kwargs)

    def __init__(self, **kwargs):
        super(AXLObject, self).__init__(**kwargs)

    @classmethod
    def tags(cls, only_for_list=True, only_extra=False) -> Generator[str, None, None]:
        """
        Generator over names of all attributes of the class.
        :param only_for_list: only yield the tags which are compatible with list calls (skip the ones which require a
        get AXL call
        :param only_extra: only yield the tags which require a get AXL call
        :return:
        """
        for field in cls.__fields__.values():
            if only_extra:
                if not field.field_info.extra.get('get_required'):
                    continue
            elif only_for_list and field.field_info.extra.get('get_required'):
                continue

            if field.alias:
                yield field.alias
            else:
                yield field.name

    def _init_get_details(self, obj_api: 'ObjApi'):
        """
        Initialize the helper attributes required to get details on demand if an attribute is accessed which requires
        a get call
        :param obj_api: obj api to store in the object for further use
        :return:
        """
        self._obj_api = obj_api
        # we haven't read details yet
        self._details_read = False

    @classmethod
    def parse_obj(cls, obj_api: 'ObjApi', obj):
        """
        Create an object from data and prepare for automatic get if needed
        :param obj_api: object api to store in the object
        :param obj: init data for object creation
        :return:
        """
        model = super(AXLObject, cls).parse_obj(obj)
        # noinspection PyProtectedMember
        model._init_get_details(obj_api)
        return model

    def __getattribute__(self, item):
        """
        Override to get details the 1st time an attribute is accessed which required a get call
        :param item:
        :return:
        """
        if item.startswith('_'):
            return super(AXLObject, self).__getattribute__(item)
        field = self.__fields__.get(item)
        if field is not None:
            if field.field_info.extra.get('get_required') and not self._details_read:
                # need to get the details via AXL
                get_method_name = f'get{self._axl_type.capitalize()}'
                log.debug(f'{get_method_name(uuid={self.uuid})} triggered by access to {self.__class__.__name__}.{item}')
                get_method = self._obj_api.service[get_method_name]
                zeep_response = get_method(uuid=self.uuid)
                zeep_data = zeep_response['return'][next(iter(zeep_response['return']))]
                data = zeep.helpers.serialize_object(zeep_data)
                obj = self.__class__.parse_obj(obj_api=self._obj_api, obj=data)
                # set indication that details have been read so that we don't do it again for this object
                obj._details_read = True
                self._details_read = True
                # now copy values of all extra attributes
                for tag in self.tags(only_extra=True):
                    self.__setattr__(tag, obj.__getattribute__(tag))

        return super(AXLObject, self).__getattribute__(item)

    def __repr_args__(self):
        # suppress _details_read and _obj_api from string output
        return [(a, v)
                for a, v in super(AXLObject, self).__repr_args__()
                if a not in ['_details_read', '_obj_api']]

    @classmethod
    def do_list(cls, obj_api: 'ObjApi', first=None, skip=None):
        """
        get a list of objects via AXL
        :param obj_api: axl API
        :param first: limit to the first n objects
        :param skip: skip 1st n objects
        :return: list of objects
        """
        # the AXL method to list the objects is something like 'listUser'
        list_call_name = f'list{cls._axl_type.capitalize()}'
        list_call = obj_api.service[list_call_name]
        log.debug(f'Calling {list_call_name}')
        try:
            zeep_response = list_call(searchCriteria={cls._axl_search: '%'},
                                      returnedTags={t: '' for t in cls.tags()},
                                      first=first,
                                      skip=skip)
        except zeep.exceptions.Fault as e:
            # check if we need to restrict the query to smaller sets
            # Error to look for is something like:
            # 'Query request too large. Total rows matched: 1277 rows. Suggestive Row Fetch: less than 953 rows'
            message = e.message
            if (m := re.match(r'Query request too large\..+matched: (\d+).+less than (\d+)', message)):
                total_rows = int(m.group(1))
                batch_size = int(m.group(2))
                # reduce site (safety)
                batch_size = int(batch_size * 0.7)
                log.debug(f'{list_call_name} returns to many rows, need to request batches: {message}')
                result = []
                for skip in range(0, total_rows, batch_size):
                    batch = cls.do_list(obj_api, first=batch_size, skip=skip)
                    result.extend(batch)
                return result
            else:
                # for other errors re-raise the exception
                raise
        if zeep_response['return'] is None:
            return []
        # list of objects is in the first entry of the return dictionary
        zeep_response = zeep_response['return'][next(iter(zeep_response['return']))]
        result = []
        log.debug(f'{list_call_name} serializing {len(zeep_response)} {cls.__name__} objects')
        for zeep_object in zeep_response:
            d = zeep.helpers.serialize_object(zeep_object)
            # the AXl response potentially contains more attributes than we are interested in
            # only look at the ones we have in the class definition
            filtered = {tag: d[tag] for tag in cls.tags()}
            # create object from values
            o = cls.parse_obj(obj_api=obj_api, obj=filtered)
            result.append(o)
        return result


class ObjApi:
    """
    Simple API helper
    """

    def __init__(self, zeep_service):
        self.service = zeep_service


class StringAndUUID(BaseModel):
    value: str = Field(None, alias='_value_1')
    uuid: Optional[str]
