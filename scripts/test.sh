#!/usr/bin/env bash

# exit script at first failure
set -e
# print a trace showing the commands being run
set -x

uv run pytest
