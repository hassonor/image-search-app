#!/usr/bin/env bash
#
# Run all test suites across the repository so CI can verify every
# microservice before merging changes.

set -e

# Test suites for each service. All suites are executed with pytest
services=(
  "api_service/tests"
  "file_reader_service/tests"
  "downloader_service/tests"
  "embedding_service/src/tests"
)

if ! command -v pytest >/dev/null 2>&1; then
  echo "pytest not installed; unable to run tests" >&2
  exit 1
fi

for suite in "${services[@]}"; do
  echo "Running tests in $suite"
  (cd "$suite" && pytest -v)
done
