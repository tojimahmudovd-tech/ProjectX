# AutomationExercise API Testing (Python)

This project provides a simple, portable **Python** test runner for the public APIs on https://automationexercise.com/api_list.

## What you get
- `src/api_test_runner.py` — runs **10+ automated API tests** (positive + negative).
- `requirements.txt` — minimal dependencies.
- `run_windows.bat` and `run_mac_linux.sh` — one-command run.
- `reports/` — test output log file created on each run.

## Prerequisites
- Python 3.10+ recommended (3.8+ should work).
- Internet access (tests call automationexercise.com).

## Quick start (Windows)
1. Unzip the folder
2. Double-click: `run_windows.bat`

## Quick start (macOS / Linux)
1. Unzip the folder
2. In terminal:
   ```bash
   chmod +x run_mac_linux.sh
   ./run_mac_linux.sh
   ```

## Notes
- The script creates a **temporary user account** (random email), validates login, fetches products/brands, runs negative method tests, and finally **deletes the account**.
- If the site rate-limits or is temporarily down, rerun the tests.

## Evidence for your report
- Screenshot the terminal output and the generated log in `reports/`.
