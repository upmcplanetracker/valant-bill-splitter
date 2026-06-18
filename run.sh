#!/bin/bash
set -e

# ==============================
#  Valant Bill Splitter Launcher
# ==============================

LOCKFILE=/tmp/splitbills.lock

# ---- Prevent overlapping runs ----
exec 200>"$LOCKFILE"
if ! flock -n 200; then
    echo "Another instance is running. Exiting."
    exit 1
fi

# ---- Activate virtual environment ----
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
source "$SCRIPT_DIR/venv/bin/activate"

# ---- Run the Python script with all arguments ----
if python3 "$SCRIPT_DIR/split_bills.py" "$@"; then
    deactivate
else
    deactivate 2>/dev/null || true
    exit 1
fi
