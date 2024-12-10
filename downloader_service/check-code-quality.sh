#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Function to display messages in green
function echo_success {
    echo -e "\033[0;32m$1\033[0m"
}

# Function to display messages in yellow
function echo_warning {
    echo -e "\033[1;33m$1\033[0m"
}

# Function to display messages in red
function echo_error {
    echo -e "\033[0;31m$1\033[0m"
}

# Check if the script is run inside a virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo_warning "Warning: You are not running inside a virtual environment."
    echo_warning "It's recommended to activate your virtual environment before running this script."
fi

# Ensure all required configuration files exist
CONFIG_FILES=(".black.toml" "ruff.toml" ".isort.cfg")

for config in "${CONFIG_FILES[@]}"; do
    if [[ ! -f "$config" ]]; then
        echo_error "Error: Configuration file '$config' not found."
        exit 1
    fi
done

# Run isort to sort imports
echo_success "Running isort to sort imports..."
isort --settings .isort.cfg src/
echo_success "isort completed successfully."

# Run Black to format code
echo_success "Running Black to format code..."
black --config .black.toml src/
echo_success "Black completed successfully."

# Run Ruff to lint and fix code
echo_success "Running Ruff to lint and fix code..."
ruff check src --config ruff.toml --fix
echo_success "Ruff completed successfully."

echo_success "All code quality checks passed successfully!"
