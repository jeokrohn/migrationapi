from pydantic import BaseModel


def to_camel(s: str) -> str:
    """
    Convert snake case variable name to camel case
    'log_id' -> 'logId'
    :param s:
    :return:
    """
    return ''.join(w.title() if i else w for i, w in enumerate(s.split('_')))


class CamelModel(BaseModel):
    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True