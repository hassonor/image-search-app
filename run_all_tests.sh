#!/usr/bin/env bash
#
# Run all test suites across the repository so CI can verify every
# microservice before merging changes.

set -e

# Standard unittest suites
unittest_services=(
  "api_service/tests"
  "file_reader_service/tests"
  "downloader_service/tests"
)

for suite in "${unittest_services[@]}"; do
  echo "Running tests in $suite"
  python3 -m unittest discover "$suite" -v
done

# Pytest-based suite for the embedding service
if command -v pytest >/dev/null 2>&1; then
  echo "Running tests in embedding_service/src/tests"
  pytest embedding_service/src/tests -v
else
  echo "pytest not installed; skipping embedding_service tests" >&2
fi
