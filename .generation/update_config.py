#!/bin/python3

'''
1. Set a new container tag
2. Increment the version number
'''

import argparse
import configparser
from pathlib import Path

CWD = Path('.generation/')
INI_FILE = CWD / 'config.ini'

parser = argparse.ArgumentParser(description='Update the config.ini file.')
parser.add_argument('--backendTag', dest='backend_tag', required=True, type=str, nargs=1,)

args = parser.parse_args()

config = configparser.ConfigParser()
config.read(INI_FILE)

config['input']['backendTag'] = args.backend_tag[0]

# retrieve version
version_digits: list[int] = [int(digit) for digit in config['package']['version'].split('.')]
# increment last version digit
version_digits[-1] += 1
# write back
config['package']['version'] = '.'.join(str(digit) for digit in version_digits)

with open(INI_FILE, 'w', encoding='utf-8') as f:
    config.write(f)
