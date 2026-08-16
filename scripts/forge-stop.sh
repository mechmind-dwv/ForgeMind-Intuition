#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="${FORGEMIND_RUN_DIR:-$ROOT/.forgemind-run}"
for name in frontend web engine; do
  pid_file="$RUN_DIR/$name.pid"
  if [ -f "$pid_file" ]; then
    pid="$(cat "$pid_file")"
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
      printf 'Detenido %s (PID %s)\n' "$name" "$pid"
    else
      printf '%s ya no estaba activo (PID %s)\n' "$name" "$pid"
    fi
    rm -f "$pid_file"
  fi
done
