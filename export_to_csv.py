#!/usr/bin/env python
"""
usage: export_to_csv.py [-h] [--host HOST] [--user USER] [--password PASSWORD] table

Dump a table from UCM to CSV

positional arguments:
  table                table name

options:
  -h, --help           show this help message and exit
  --host HOST          AXl host
  --user USER          AXL user
  --password PASSWORD  AXL password
"""
import csv
import logging
import os
import sys
from argparse import ArgumentParser

from dotenv import load_dotenv
from ucmaxl import AXLHelper


def main():
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('zeep.wsdl.wsdl').setLevel(logging.INFO)
    logging.getLogger('zeep.xsd.schema').setLevel(logging.INFO)

    parser = ArgumentParser(description='Dump a table from UCM to CSV')
    parser.add_argument('table', type=str,
                        help='table name')
    parser.add_argument('--host', type=str, help='AXl host')
    parser.add_argument('--user', type=str, help='AXL user')
    parser.add_argument('--password', type=str, help='AXL password')
    args = parser.parse_args()

    load_dotenv()
    axl_host = args.host or os.getenv('AXL_HOST')
    axl_user = args.user or os.getenv('AXL_USER')
    axl_pass = args.password or os.getenv('AXL_PASSWORD')
    if not all((axl_pass, axl_host, axl_user)):
        print('AXL host, AXL user, and AXL password all need to be provided either as parameter or in environment '
              '(AXL_HOST, AXL_USER, AXL_PASSWORD)', file=sys.stderr)
        exit(1)
    with AXLHelper(ucm_host=axl_host, auth=(axl_user, axl_pass), verify=False) as axl:
        r = axl.sql_query(f'select * from {args.table}')
        csv_name = f'{args.table}.csv'
        with open(csv_name, mode='w', newline='') as output:
            # take keys of 1st record as field names
            writer = csv.DictWriter(output, fieldnames=list(r[0]))
            writer.writeheader()
            list(map(writer.writerow, r))
            print(f'wrote {len(r)} records to {csv_name}')


if __name__ == '__main__':
    main()
