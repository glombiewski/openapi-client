#!/bin/python3

'''
Generator for the OpenAPI client.
'''

from __future__ import annotations
import argparse
from dataclasses import dataclass
from pathlib import Path
from urllib import request
from urllib.error import URLError
from urllib.parse import urlsplit
import configparser
import json
import os
import shutil
import subprocess
import sys
import time
from typing import Literal


CWD = Path('.generation/')


def eprint(*args, **kwargs):
    '''Print to stderr.'''
    print(*args, file=sys.stderr, **kwargs)


class ProgramArgs(argparse.Namespace):
    '''Typed command line arguments.'''
    language: Literal['python', 'typescript']
    fetch_spec: bool
    build_container: bool

    @staticmethod
    def parse_arguments() -> ProgramArgs:
        '''Parse command line arguments.'''
        parser = argparse.ArgumentParser(
            description='Create a client for the Geo Engine API.')
        parser.add_argument('--no-spec-fetch', dest='fetch_spec', action='store_false',
                            required=False, default=True)
        parser.add_argument('--no-container-build', dest='build_container', action='store_false',
                            required=False, default=True)
        parser.add_argument('language', choices=['python', 'typescript'],
                            type=str)

        parsed_args: ProgramArgs = parser.parse_args()
        return parsed_args


@dataclass
class ConfigArgs():
    '''Typed config.ini arguments.'''
    # Backend version
    ge_backend_tag: str

    # General
    github_url: str

    # Python package name
    python_package_name: str
    python_package_version: str

    # TypeScript package name
    typescript_package_name: str
    typescript_package_version: str

    @staticmethod
    def parse_config() -> ConfigArgs:
        '''Parse config.ini arguments.'''
        parsed = configparser.ConfigParser()
        parsed.optionxform = str  # do not convert keys to lowercase
        parsed.read(CWD / 'config.ini')

        return ConfigArgs(
            ge_backend_tag=parsed['input']['backendTag'],
            github_url=parsed['general']['githubUrl'],
            python_package_name=parsed['python']['name'],
            python_package_version=parsed['python']['version'],
            typescript_package_name=parsed['typescript']['name'],
            typescript_package_version=parsed['typescript']['version'],
        )


def fetch_spec(*, ge_backend_tag: str) -> None:
    '''
    Generate the openapi.json file.

    Imitating manually fetching it, e.g.

    ```bash
    wget http://localhost:3030/api/api-docs/openapi.json -O - \
      | python -m json.tool --indent 2 > .generation/input/openapi.json
    ```
    '''
    eprint("Starting Geo Engine backend.")

    ge_process = subprocess.Popen(
        [
            "podman", "run",
            "--rm",  # remove the container after running
            "--network=host",  # port 8080 by default
            # "-p", "3030:8080",
            f"quay.io/geoengine/geoengine:{ge_backend_tag}",
        ],
    )

    for _ in range(180):  # <3 minutes
        eprint("Requesting `openapi.json`….")
        try:
            with request.urlopen(
                "http://localhost:8080/api/api-docs/openapi.json",
                timeout=10,
            ) as w:
                api_json = json.load(w)

            with open(CWD / "input/openapi.json", "w", encoding='utf-8') as f:
                json.dump(api_json, f, indent=2)

            eprint("Stored `openapi.json`.")
            break
        except URLError as _e:
            pass  # try again
        time.sleep(1)  # 1 second

    eprint("Stopping Geo Engine backend.")
    ge_process.kill()


def build_container():
    '''Build the patched generator image'''
    subprocess.run(
        [
            "podman", "build",
            "-t", "openapi-generator-cli:patched",
            CWD,
        ],
        check=True,
    )


def clean_test_dirs(*, language: Literal['python', 'typescript']):
    '''Remove the test directory, since it will not be overwritten by the generator.'''
    test_path = Path(language) / 'test'
    if os.path.isdir(test_path):
        shutil.rmtree(test_path)


def generate_python_code(*, package_name: str, package_version: str, package_url: str):
    '''Run the generator.'''
    subprocess.run(
        [
            "podman", "run",
            "--network=host",
            "--rm",  # remove the container after running
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
                f"packageName={package_name}",
                f"packageVersion={package_version}",
                f"packageUrl={package_url}",
            ]),
            "--enable-post-process-file",
            "-o", "/local/python/",
        ],
        check=True,
    )


def generate_typescript_code(*, npm_name: str, npm_version: str, repository_url: str):
    '''Run the generator.'''

    parsed_url = urlsplit(repository_url)
    (url_path, _url_ext) = os.path.splitext(parsed_url.path)
    (url_path, git_user_id) = os.path.split(url_path)
    (url_path, git_repo_id) = os.path.split(url_path)

    subprocess.run(
        [
            "podman", "run",
            "--network=host",
            "--rm",  # remove the container after running
            "-v", f"{os.getcwd()}:/local",
            f"--env-file={CWD / 'override.env'}",
            # "docker.io/openapitools/openapi-generator-cli:v7.0.1",
            "openapi-generator-cli:patched",
            "generate",
            "-i", f"{'/local' / CWD / 'input/openapi.json'}",
            "-g", "typescript-fetch",
            "--additional-properties=" + ",".join([
                "supportsES6=true",
                f"npmName={npm_name}",
                f"npmVersion={npm_version}",
            ]),
            "--git-host", parsed_url.netloc,
            "--git-user-id", git_user_id,
            "--git-repo-id", git_repo_id,
            "--enable-post-process-file",
            "-o", "/local/typescript/",
        ],
        check=True,
    )


def main():
    '''The entry point of the program'''
    args = ProgramArgs.parse_arguments()
    config = ConfigArgs.parse_config()

    if args.fetch_spec:
        fetch_spec(ge_backend_tag=config.ge_backend_tag)

    if args.build_container:
        build_container()

    clean_test_dirs(language=args.language)

    if args.language == 'python':
        generate_python_code(
            package_name=config.python_package_name,
            package_version=config.python_package_version,
            package_url=config.github_url,
        )
    elif args.language == 'typescript':
        generate_typescript_code(
            npm_name=config.typescript_package_name,
            npm_version=config.typescript_package_version,
            repository_url=config.github_url,
        )
    else:
        raise RuntimeError(f'Unknown language {args.language}.')


if __name__ != '__main__':
    raise RuntimeError('This module should not be imported.')

main()
