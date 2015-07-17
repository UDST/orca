#!/usr/bin/env bash

# Run the gulp command to build the JS dist bundle
# Assumes that gulp is installed and all JS dependencies have been
# installed locally using npm.

cd orca/server/static

if [[ $1 == 'complete' ]]; then
    npm install -g gulp
    npm install
fi

gulp js-build
