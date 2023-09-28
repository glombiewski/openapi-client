#!/bin/python3

'''
Generator for the OpenAPI client.
'''

import os
import subprocess

# TODO: generate the openapi.json file
# For now: `wget http://localhost:3030/api/api-docs/openapi.json -O input/openapi.json`

subprocess.run(
    [
        "podman", "run",
            "--network=host",
            "--rm", # remove the container after running
            "-v", f"{os.getcwd()}:/local",
            "docker.io/openapitools/openapi-generator-cli",
                "generate",
                    "-i", "/local/input/openapi.json",
                    "-g", "python",
                    "--additional-properties=useOneOfDiscriminatorLookup=true",
                    "-o", "/local/generated",
    ],
    check=True
)
