#!/usr/bin/env python
"""
Read learned patterns from remoteroutingpattern table from UCMs configured in YML config and write to CSV for further
processing
"""
import csv
import logging
import os
import re
import sys
from collections.abc import Iterable, Generator
from itertools import chain
from typing import Optional

import yaml
from pydantic import BaseModel, Field, parse_obj_as

from ucmaxl import AXLHelper


class LearnedPattern(BaseModel):
    """
    A pattern in the remoteroutingpattern table
    """
    remote_catalog_key_id: str = Field(alias='remotecatalogkey_id')
    route_string: Optional[str]
    pattern: str


class RemoteCatalog(BaseModel):
    """
    One entry in remoteclusteruricatalog table
    """
    peer_id: str = Field(alias='peerid')
    route_string: str = Field(alias='routestring')


class RcKey(BaseModel):
    """
    One entry in remotecatalogkey table
    """
    rc_key_id: str = Field(alias='remotecatalogkey_id')
    rc_catalog_peer_id: str = Field(alias='remoteclusteruricatalog_peerid')


def unique_patterns(patterns: Iterable[LearnedPattern]) -> Generator[LearnedPattern, None, None]:
    """
    Filter out duplicate patterns
    :param patterns:
    :return:
    """
    pattern_keys = set()
    for pattern in patterns:
        key = f'{pattern.route_string}:{pattern.pattern}'
        if key in pattern_keys:
            continue
        pattern_keys.add(key)
        yield pattern


def normalize(patterns: Iterable[LearnedPattern]) -> Generator[LearnedPattern, None, None]:
    """
    Normalize learned patterns to make them compatible with WxC.
    WxC dial plans only have "X" as wildcard. We look for [] enumerations and expand them

    :param patterns:
    :return:
    """
    # regex to catch patterns with [..] in it
    catch_re = re.compile(r"""(?P<pre>.*?)          # any characters (non greedy) until ...
                              (?P<re_part>\[.+?])   # "[” followed by any characters(non greedy) until "]"
                              (?P<post>.*)          # and whatever might come after that enumeration""",
                          flags=re.VERBOSE)
    for learned_pattern in patterns:
        pattern = learned_pattern.pattern
        if any(c in pattern for c in '.*!'):
            print(f'illegal pattern format: {pattern}', file=sys.stderr)
            continue
        if m := catch_re.match(pattern):
            # get pre, regex, post
            pre = m.group('pre')
            re_part = m.group('re_part')
            post = m.group('post')
            # determine digits matched by the reqex in the pattern and yield normalized patterns
            digit_matcher = re.compile(re_part)
            matching_digits = (d for d in '0123456789'
                               if digit_matcher.match(d))
            logging.debug(f'expanding "{pattern}"')
            for d in matching_digits:
                expanded = f'{pre}{d}{post}'
                logging.debug(f' {expanded}')
                expanded_learned = learned_pattern.copy(deep=True)
                expanded_learned.pattern = expanded
                # recursive call to make sure we catch patterns with multiple enumeration in it
                yield from normalize([expanded_learned])
        else:
            # nothing to do, just yield the pattern
            yield learned_pattern


def learned_patterns(axl: AXLHelper, with_numbers: bool = False) -> list[LearnedPattern]:
    """
    read learned patterns from remoteroutingpattern table
    :param axl:
    :param with_numbers: if true, also include individual numbers (not only patterns)
    :return: list of learned patterns/numbers
    """
    """
    tk pattern usage:
    - 22   Uri Routing                           
    + 23   ILS Learned Enterprise Number         
    + 24   ILS Learned E164 Number               
    + 25   ILS Learned Enterprise Numeric Pattern
    + 26   ILS Learned E164 Numeric Pattern      
    + 27   Alternate Number                      
    - 28   ILS Learned URI                       
    - 29   ILS Learned PSTN Failover Rule        
    + 30   ILS Imported E164 Number    
    """
    usage = [25, 26]
    if with_numbers:
        usage.extend((23, 24))
    usage = f'({",".join(str(u) for u in usage)})'
    patterns = axl.sql_query(
        f'select remotecatalogkey_id,pattern from remoteroutingpattern where tkpatternusage in {usage}')
    return parse_obj_as(list[LearnedPattern], patterns)


def read_from_ucm(*, axl_host: str, axl_user: str, axl_password: str) -> list[LearnedPattern]:
    """
    Read learned patterns from UCM using thin AXL.
    """
    print(f'Reading from UCM "{axl_host}"...')
    axl = AXLHelper(ucm_host=axl_host, auth=(axl_user, axl_password), verify=False)

    remote_catalogs = parse_obj_as(list[RemoteCatalog],
                                   axl.sql_query('select peerid,routestring from remoteclusteruricatalog'))
    rc_by_peer_id: dict[str, RemoteCatalog] = {rc.peer_id: rc for rc in remote_catalogs}

    rc_keys = parse_obj_as(
        list[RcKey],
        axl.sql_query('select remotecatalogkey_id,remoteclusteruricatalog_peerid from remotecatalogkey'))
    route_string_by_catalog_key: dict[str, str] = {rc.rc_key_id: rc_by_peer_id[rc.rc_catalog_peer_id].route_string
                                                   for rc in rc_keys}

    # read learned patterns
    learned = learned_patterns(axl)
    print(f'read {len(learned)} learned patterns from {axl_host}')
    for pattern in learned:
        pattern.route_string = route_string_by_catalog_key[pattern.remote_catalog_key_id]
    return learned


class UCMInfo(BaseModel):
    """
    Information for one AXL target
    """
    host: str
    user: str
    password: str


def ucm_info_from_yml() -> list[UCMInfo]:
    """
    Read list of UCMs with AXL credentials from YML file
    """
    path = os.path.abspath(f'{os.path.splitext(__file__)[0]}.yml')
    print(f'reading config from {path}')

    with open(path, mode='r') as f:
        data = yaml.safe_load(f)
    hosts = parse_obj_as(list[UCMInfo], data)
    return hosts


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('zeep.wsdl.wsdl').setLevel(logging.INFO)
    logging.getLogger('zeep.xsd.schema').setLevel(logging.INFO)

    # get UCM information from YML file
    ucm_infos = ucm_info_from_yml()

    # get learned patterns from all configured UCMs
    # - expand patterns to make sure they are compatible with WxC dial plans
    # - only consider unique patterns (there might me catalogs that are read from multiple clusters)
    ucm_learned_patterns = list(unique_patterns(
        normalize(
            chain.from_iterable(
                read_from_ucm(axl_host=ucm_info.host,
                              axl_user=ucm_info.user,
                              axl_password=ucm_info.password)
                for ucm_info in ucm_infos))))

    # write patterns to file with route string column
    csv_path = os.path.abspath(f'{os.path.splitext(__file__)[0]}.csv')
    print(f'Writing patterns to "{csv_path}"')
    with open(csv_path, mode='w', newline='') as output:
        writer = csv.writer(output)
        writer.writerow(('route_string', 'pattern'))
        for csv_pattern in ucm_learned_patterns:
            writer.writerow((csv_pattern.route_string, csv_pattern.pattern))
    print(f'Wrote {len(ucm_learned_patterns)} patterns to {csv_path}')
