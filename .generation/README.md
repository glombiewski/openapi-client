# geoengine-openapi-client - Code Generation

Auto-generated Python Client API for Geo Engine

# Dependencies

- Python
- Podman

# Requirements

- Postgres instance running on `localhost:5432` with
  - `geoengine:geoengine` credentials and
  - `geoengine` database

# Generation

From the root of the repository run:

```bash
.generation/generate.py
```

## Dev-Mode

To run the generation in dev mode, run:

```bash
.generation/generate.py --no-spec-fetch --no-container-build
```

This will skip the running of the container and instead use the local files.
It will also stop building the customized generator container.

## Update config.ini

To update the config.ini file, run:

```bash
.generation/update_config.py --backendTag pro-nightly-2023-11-28
```

This will set a new backend tag and increment the version number.
