#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if ! command -v pgrep >/dev/null; then
  echo 'Falta pgrep; instala procps en Termux con: pkg install procps' >&2
  exit 1
fi

found=0
while read -r pid; do
  [ -n "$pid" ] || continue
  [ "$pid" = "$$" ] && continue
  cmdline="$(tr '\0' ' ' < "/proc/$pid/cmdline" 2>/dev/null || true)"
  case "$cmdline" in
    *"$ROOT/frontend"*vite*)
      echo "Deteniendo Vite de ForgeMind: PID $pid"
      kill "$pid" 2>/dev/null || true
      found=1
      ;;
  esac
done < <(pgrep -f "$ROOT/frontend" || true)

if [ "$found" -eq 0 ]; then
  echo 'No se encontraron procesos Vite de ForgeMind.'
fi
