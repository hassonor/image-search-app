#!/bin/bash

black . --config .black.toml --check
ruff check . --config ruff.toml
isort . --settings .isort.cfg --check-only
