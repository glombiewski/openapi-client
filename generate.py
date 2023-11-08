#!/bin/python3

'''
Generator for the OpenAPI client.
'''

import os
import subprocess

# Set `DEV_RUN=1` to run the generator in development mode.
dev_run: bool = int(os.environ.get('DEV_RUN', 0)) == 1

if dev_run:
    print("Running in development mode.")

# Generate the openapi.json file.
if not dev_run:
    pass
    # TODO: generate the openapi.json file
    # For now: `wget http://localhost:3030/api/api-docs/openapi.json -O input/openapi.json`

# Build the patched generator image.
if not dev_run:
    subprocess.run(
        [
            "podman", "build",
                "-t", "openapi-generator-cli:patched",
                ".",
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
            "--env-file=override.env",
            # "docker.io/openapitools/openapi-generator-cli:v7.0.1",
            "openapi-generator-cli:patched",
                "generate",
                    "-i", "/local/input/openapi.json",
                    "-g", "python",
                    "--additional-properties=useOneOfDiscriminatorLookup=true",
                    "--enable-post-process-file",
                    "-o", "/local/generated",
    ],
    check=True,
)
