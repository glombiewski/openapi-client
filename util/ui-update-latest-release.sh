#!/bin/bash

# FOR DEVELOPMENT USE ONLY
#
# update the openapi-client to the latest release version in the ui

set -e

version=$(awk -F " = " '/version/ {print $2; exit}' .generation/config.ini)

cd ../geoengine-ui

npm uninstall @geoengine/openapi-client
npm install --save-exact @geoengine/openapi-client@${version}

cd -
