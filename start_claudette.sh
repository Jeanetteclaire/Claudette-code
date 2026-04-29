#!/bin/bash

# start_claudette.sh
# Wrapper script for the Claudette Launch Agent.
# Finds Python, activates the right environment, starts server.py.

CLAUDETTE_DIR="/Users/jeanettearthur/Claudette"
LOG="$CLAUDETTE_DIR/claudette_server.log"
cd "$CLAUDETTE_DIR"
export PYTHONUNBUFFERED=1

echo "$(date): Starting Claudette server..." >> "$LOG"

# Try Python locations in order of preference.
# If you use a virtual environment, activate it first.

# Option 1: Virtual environment (recommended — uncomment if you set one up)
# source "$CLAUDETTE_DIR/venv/bin/activate"
# python "$CLAUDETTE_DIR/server.py"

# Option 2: Python from Homebrew
if [ -f "/usr/local/bin/python3" ]; then
    echo "$(date): Using /usr/local/bin/python3" >> "$LOG"
    /usr/local/bin/python3 "$CLAUDETTE_DIR/server.py"

# Option 3: Python from Homebrew (Apple Silicon path)
elif [ -f "/opt/homebrew/bin/python3" ]; then
    echo "$(date): Using /opt/homebrew/bin/python3" >> "$LOG"
    /opt/homebrew/bin/python3 "$CLAUDETTE_DIR/server.py"

# Option 4: System Python
elif [ -f "/usr/bin/python3" ]; then
    echo "$(date): Using /usr/bin/python3" >> "$LOG"
    /usr/bin/python3 "$CLAUDETTE_DIR/server.py"

else
    echo "$(date): ERROR — could not find Python. Install Python via Homebrew." >> "$LOG"
    exit 1
fi
