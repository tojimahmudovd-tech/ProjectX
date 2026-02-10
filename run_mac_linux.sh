#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

echo "Creating virtual environment..."
python3 -m venv .venv

echo "Activating venv..."
source .venv/bin/activate

echo "Installing requirements..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "Running tests..."
python src/api_test_runner.py

echo ""
echo "Done. Logs saved in reports/"
