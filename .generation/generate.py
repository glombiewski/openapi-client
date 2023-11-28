#!/bin/python3

'''
Generator for the OpenAPI client.
'''

from pathlib import Path
from urllib import request
from urllib.error import URLError
import configparser
import json
import os
import shutil
import subprocess
import sys
import time

# Set `DEV_RUN=1` to run the generator in development mode.
DEV_RUN: bool = int(os.environ.get('DEV_RUN', 0)) == 1

# Read configuration from `config.ini`.
config = configparser.ConfigParser()
CWD = Path('.generation/')
config.read(CWD / 'config.ini')

# Python package name
PACKAGE_NAME: str = config['package']['name']
PACKAGE_VERSION: str = config['package']['version']
PACKAGE_URL: str = config['package']['url']

# Specify backend version
GE_BACKEND_TAG: str = config['input']['backendTag']

if DEV_RUN:
    print("Running in development mode.", file=sys.stderr)

# Generate the openapi.json file.
#
# Imitating manually fetching it, e.g.
#
# ```bash
# wget http://localhost:3030/api/api-docs/openapi.json -O - \
#   | python -m json.tool --indent 2 > .generation/input/openapi.json
# ```
#
if not DEV_RUN:
    print("Starting Geo Engine backend.", file=sys.stderr)

    ge_process = subprocess.Popen(
        [
            "podman", "run",
                "--rm", # remove the container after running
                "--network=host", # port 8080 by default
                # "-p", "3030:8080",
                f"quay.io/geoengine/geoengine:{GE_BACKEND_TAG}",
        ],
    )

    for _ in range(90):
        print("Requesting `openapi.json`….", file=sys.stderr)
        try:
            with request.urlopen(
                "http://localhost:8080/api/api-docs/openapi.json",
                 timeout=10,
            ) as w:
                api_json = json.load(w)

            with open(CWD / "input/openapi.json", "w", encoding='utf-8') as f:
                json.dump(api_json, f, indent=2)

            print("Stored `openapi.json`.", file=sys.stderr)
            break
        except URLError as e:
            pass # try again
        time.sleep(1) # 1 second

    print("Stopping Geo Engine backend.", file=sys.stderr)
    ge_process.kill()

# Build the patched generator image.
if not DEV_RUN:
    subprocess.run(
        [
            "podman", "build",
                "-t", "openapi-generator-cli:patched",
                CWD,
        ],
        check=True,
    )

# Remove the test directory, since it will not be overwritten by the generator.
if os.path.isdir("test"):
    shutil.rmtree("test")

# Run the generator.
subprocess.run(
    [
        "podman", "run",
            "--network=host",
            "--rm", # remove the container after running
            "-v", f"{os.getcwd()}:/local",
            f"--env-file={CWD / 'override.env'}",
            # "docker.io/openapitools/openapi-generator-cli:v7.0.1",
            "openapi-generator-cli:patched",
                "generate",
                    "-i", f"{'/local' / CWD / 'input/openapi.json'}",
                    "-g", "python",
                    "--additional-properties=" + ",".join([
                        "useOneOfDiscriminatorLookup=true",
                        # "generateSourceCodeOnly=true",
                        f"packageName={PACKAGE_NAME}",
                        f"packageVersion={PACKAGE_VERSION}",
                        f"packageUrl={PACKAGE_URL}",
                    ]),
                    "--enable-post-process-file",
                    "-o", "/local/",
    ],
    check=True,
)
