#!/bin/python3

'''
Generator for the OpenAPI client.
'''

import os
import subprocess
from urllib import request
from urllib.error import URLError
import sys
import time

# Python package name
PACKAGE_NAME = 'geoengine_sys'
PACKAGE_VERSION = os.environ.get('PACKAGE_VERSION', '0.0.1')
PACKAGE_URL = 'https://github.com/geo-engine/geoengine-python-sys'

# Set `DEV_RUN=1` to run the generator in development mode.
DEV_RUN: bool = int(os.environ.get('DEV_RUN', 0)) == 1

# Specify backend version
GE_BACKEND_TAG: str = os.environ.get('GE_BACKEND_TAG', 'pro-nightly-2023-11-01')

if DEV_RUN:
    print("Running in development mode.", file=sys.stderr)

# Generate the openapi.json file.
#
# Imitating manually fetching it, e.g.
# `wget http://localhost:3030/api/api-docs/openapi.json -O .generation/input/openapi.json`
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

    for _ in range(10):
        try:
            with request.urlopen("http://localhost:8080/api/api-docs/openapi.json", timeout=10) as w, \
                open(".generation/input/openapi.json", "wb") as f:
                api_json = w.read()
                f.write(api_json)

            print("Stored `openapi.json`.", file=sys.stderr)
        except URLError as e:
            # try again
            time.sleep(1) # 1 second

    print("Stopping Geo Engine backend.", file=sys.stderr)
    ge_process.kill()

# Build the patched generator image.
if not DEV_RUN:
    subprocess.run(
        [
            "podman", "build",
                "-t", "openapi-generator-cli:patched",
                ".generation/",
        ],
        check=True,
    )

# Run the generator.

subprocess.run(
    [
        "podman", "run",
            "--network=host",
            "--rm", # remove the container after running
            "-v", f"{os.getcwd()}:/local",
            "--env-file=.generation/override.env",
            # "docker.io/openapitools/openapi-generator-cli:v7.0.1",
            "openapi-generator-cli:patched",
                "generate",
                    "-i", "/local/.generation/input/openapi.json",
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
