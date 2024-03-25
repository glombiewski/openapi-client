#!/bin/bash

# FOR DEVELOPMENT USE ONLY
#
# increment the version and regenerate the openapi-client

set -e

.generation/update_config.py --backendTag pro-nightly-$(date -d "+1 day" "+%Y-%m-%d")

wget http://localhost:3030/api/api-docs/openapi.json -O - | python3 -m json.tool --indent 2 > .generation/input/openapi.json
.generation/generate.py --no-spec-fetch --no-container-build python
.generation/generate.py --no-spec-fetch --no-container-build typescript
