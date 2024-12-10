#!/bin/bash

black --config .black.toml
ruff . --config ruff.toml --fix
isort . --settings .isort.cfg