#!/usr/bin/env bash
set -euo pipefail

# Simple runner for desktop (Linux). Creates a venv if missing, installs Kivy,
# enables console logs, and runs the app with helpful diagnostics.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
cd "$ROOT_DIR"

VENV_DIR=".venv"

if [[ ! -d "$VENV_DIR" ]]; then
  echo "[setup] Creating virtualenv at $VENV_DIR"
  python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"
python -m pip install -U pip wheel setuptools >/dev/null

# Install Python deps for desktop run only (avoid compiling pyjnius here)
if ! python -c 'import kivy, sys; sys.exit(0)' 2>/dev/null; then
  echo "[setup] Installing Kivy 2.3.1 and requests"
  pip install "Kivy==2.3.1" "requests==2.32.3"
fi

echo "[info] Python: $(python --version)"
echo "[info] Kivy:   $(python -c 'import kivy; print(kivy.__version__)' 2>/dev/null || echo 'not installed')"

# Improve logging on desktop
export KIVY_NO_CONSOLELOG=0
export KIVY_LOG_LEVEL=debug

echo "[run] Starting app..."
if ! python main.py; then
  EC=$?
  echo "[error] App exited with code $EC"
  echo "[hint] If no window appeared, ensure SDL2 libs are installed:"
  echo "       sudo apt-get install -y libgl1-mesa-dev libgles2-mesa-dev libsdl2-dev \"
  echo "            libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \"
  echo "            libgstreamer1.0-dev gstreamer1.0-plugins-base gstreamer1.0-plugins-good"
  exit "$EC"
fi

echo "[done] App closed normally."
