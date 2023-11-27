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
DEV_RUN=1 .generation/generate.py
```

This will skip the running of the container and instead use the local files.
