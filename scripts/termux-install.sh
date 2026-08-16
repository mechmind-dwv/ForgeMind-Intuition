#!/usr/bin/env bash
set -Eeuo pipefail

repo_dir="${1:-$HOME/ForgeMind-Intuition}"
cd "$repo_dir"

# Si el prompt conserva VIRTUAL_ENV pero su intérprete fue eliminado,
# desactivarlo antes de intentar cualquier comando Python.
if [ -n "${VIRTUAL_ENV:-}" ] && [ ! -x "$VIRTUAL_ENV/bin/python" ]; then
  echo "Entorno virtual roto detectado: $VIRTUAL_ENV"
  unset VIRTUAL_ENV
  hash -r
fi

command -v python >/dev/null || {
  echo "Falta Python. En Termux ejecuta: pkg install python" >&2
  exit 1
}

if [ ! -x .venv/bin/python ]; then
  echo "Creando .venv con paquetes del sistema disponibles..."
  rm -rf .venv
  python -m venv --system-site-packages .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -e '.[vectorized,dev]'

python - <<'PY'
import fastapi
import numpy
import uvicorn
print(f"FastAPI: {fastapi.__version__}")
print(f"Uvicorn: {uvicorn.__version__}")
print(f"NumPy: {numpy.__version__}")
PY

chmod +x scripts/*.sh

printf '\nForgeMind quedó instalado en %s\n' "$repo_dir"
printf 'Prueba rápida: bash scripts/forge-test.sh\n'
printf 'Arranque: bash scripts/forge-start.sh dev\n'
printf 'Estado: bash scripts/forge-status.sh\n'
printf 'Parada: bash scripts/forge-stop.sh\n'
printf 'Exportador: docs/OBSIDIAN_TERMUX.md\n'
