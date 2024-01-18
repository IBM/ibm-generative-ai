#!/bin/bash

RED='\033[0;31m'
NC='\033[0m' # No Color

expected_return_code=5
output="$(poetry run pytest -m 'not unit and not integration and not e2e' --collect-only --disable-warnings --no-header --no-cov 2>/dev/null)"
return_code=$?

if [ $return_code -eq $expected_return_code ]; then
  exit 0
else
  printf "${RED}WARNING${NC}: The following tests are missing markers:\n"
  echo "$output"
  exit 1
fi
