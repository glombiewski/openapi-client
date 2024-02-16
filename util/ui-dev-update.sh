#!/bin/bash

# FOR DEVELOPMENT USE ONLY
#
# Usage (from the repo root): ./util/ui-dev-update.sh [-a] [commit-message]
#
# this script uses the OpenAPI json from a Geo Engine instance running on port 3030
# it generates the openapi-client and pushes it to the current branch (-a to amend the last commit)
# then it updates the geoengine-ui's openapi-client dependency to the development branch
# note: the geoengine-ui git repo must be in the same directory as the openapi-client repo

set -e

wget http://localhost:3030/api/api-docs/openapi.json -O - | python3 -m json.tool --indent 2 > .generation/input/openapi.json
.generation/generate.py --no-spec-fetch --no-container-build python
.generation/generate.py --no-spec-fetch --no-container-build typescript

git add .

# Check if -a is passed as an argument
if [[ "$*" == *"-a"* ]]; then
    # Use git commit --amend
    git commit --amend --no-edit
else
    # Get all arguments as a single string
    args_as_string="$*"

    # Set the commit message to the input arguments or a default message
    message=${args_as_string:-"update openapi-client"}

    git commit -m "$message"
fi

git push

current_branch=$(git rev-parse --abbrev-ref HEAD)

cd ../geoengine-ui

npm uninstall @geoengine/openapi-client
npm install @geoengine/openapi-client@https://gitpkg.now.sh/geo-engine/openapi-client/typescript?${current_branch}

cd -
