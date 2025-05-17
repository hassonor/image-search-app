#!/usr/bin/env bash

set -e

services=(
  "api_service/tests"
  "file_reader_service/tests"
  "downloader_service/tests"
)

for suite in "${services[@]}"; do
  echo "Running tests in $suite"
  python3 -m unittest discover "$suite" -v
done
