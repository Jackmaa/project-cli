#!/bin/bash
# Helper script to run the project CLI

cd "$(dirname "$0")"
python3 -m projects.cli "$@"
