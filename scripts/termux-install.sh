#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

repo_dir="${1:-$HOME/ForgeMind-Intuition}"
cd "$repo_dir"

python -m pip install --upgrade pip
python -m pip install -e '.[vectorized,dev]'

printf '\nForgeMind quedó instalado en %s\n' "$repo_dir"
printf 'Prueba rápida: python -m pytest tests/test_obsidian.py -q\n'
printf 'Exportador: docs/OBSIDIAN_TERMUX.md\n'
