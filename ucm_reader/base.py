from pydantic import BaseModel, Field
import zeep.exceptions
import zeep.helpers
import re

from typing import Iterable, Optional

__all__ = ['AXLObject', 'StringAndUUID']


class AXLObject(BaseModel):

    @classmethod
    def tags(cls) -> Iterable[str]:
        """
        Iterable over names of all attributes of the class
        :return:
        """
        return (alias if (alias := field.alias) else field.name
                for field in cls.__fields__.values())

    @classmethod
    def do_list(cls, list_call, search_attribute: str, first=None, skip=None):
        try:
            zeep_response = list_call(searchCriteria={search_attribute: '%'},
                                      returnedTags={t: '' for t in cls.tags()},
                                      first=first,
                                      skip=skip)
        except zeep.exceptions.Fault as e:
            # check if we need to restrict the query to smaller sets
            # Error to look for is something like:
            # 'Query request too large. Total rows matched: 1277 rows. Suggestive Row Fetch: less than 953 rows'
            message = e.message
            if (m := re.match(r'Query request too large\. Total rows matched: (\d+) rows\. '
                              r'Suggested row fetch: less than (\d+) rows',
                              message)):
                total_rows = int(m.group(1))
                batch_size = int(m.group(2))
                batch_size = int(batch_size * 0.7)
                result = []
                for skip in range(0, total_rows, batch_size):
                    batch = cls.do_list(list_call, search_attribute, first=batch_size, skip=skip)
                    result.extend(batch)
                return result
            else:
                raise
        if zeep_response['return'] is None:
            return []
        zeep_response = zeep_response['return'][next((r for r in zeep_response['return']))]
        result = []
        for zeep_object in zeep_response:
            d = zeep.helpers.serialize_object(zeep_object)
            filtered = {tag: d[tag] for tag in cls.tags()}
            # create object from values
            o = cls.parse_obj(filtered)
            result.append(o)
        return result


class ObjApi:
    def __init__(self, zeep_service):
        self.service = zeep_service


class StringAndUUID(BaseModel):
    value: str = Field(None, alias='_value_1')
    uuid: Optional[str]
