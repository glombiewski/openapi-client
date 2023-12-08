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
parser.add_argument('--backendTag', dest='backend_tag',
                    required=True, type=str)

args = parser.parse_args()

config = configparser.ConfigParser()
config.optionxform = str  # do not convert keys to lowercase
config.read(INI_FILE)

config['input']['backendTag'] = args.backend_tag

for language in ['python', 'typescript']:
    # retrieve version
    version_digits: list[int] = [
        int(digit) for digit in config[language]['version'].split('.')]
    # increment last version digit
    version_digits[-1] += 1
    # write back
    config[language]['version'] = '.'.join(
        str(digit) for digit in version_digits)

with open(INI_FILE, 'w', encoding='utf-8') as f:
    config.write(f)
