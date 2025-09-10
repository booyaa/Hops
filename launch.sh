#!/bin/bash
# This script launches the Hops bot in a virtual environment

# launch.sh
cd "$(dirname "$0")"


# activate the virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "Virtual environment not found, this tool just launches the .py in venv"
    exit 1
fi

# launch the application
if [[ "$1" == hops* ]]; then
    python3 Hops.py --serial
else
    echo "Unknown application, try "hops" instead"
    exit 1
fi

deactivate
