#!/bin/bash
# AI Escape Room - Unified Demo Launcher

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
PROJECT_ROOT="$DIR/.."

echo "=========================================================="
echo "    AI ESCAPE ROOM: AIML INNOVATIVE ASSIGNMENT PROTOTYPE   "
echo "=========================================================="
echo "Starting Unified CLI Application..."
echo ""

cd "$PROJECT_ROOT/Source_Code/src"
/usr/bin/python3 main.py
