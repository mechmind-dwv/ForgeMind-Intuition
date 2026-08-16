#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="${FORGEMIND_RUN_DIR:-$ROOT/.forgemind-run}"
ENGINE_HOST="${FORGEMIND_ENGINE_HOST:-127.0.0.1}"
ENGINE_PORT="${FORGEMIND_ENGINE_PORT:-8787}"
WEB_PORT="${FORGEMIND_WEB_PORT:-3000}"

for name in engine frontend web; do
  pid_file="$RUN_DIR/$name.pid"
  if [ -f "$pid_file" ] && kill -0 "$(cat "$pid_file")" 2>/dev/null; then
    printf '%-10s ACTIVE pid=%s\n' "$name" "$(cat "$pid_file")"
  else
    printf '%-10s STOPPED\n' "$name"
  fi
done

if command -v curl >/dev/null && curl -fsS "http://$ENGINE_HOST:$ENGINE_PORT/health" >/tmp/forgemind-engine-health.json 2>/dev/null; then
  printf 'engine health: OK %s\n' "$(cat /tmp/forgemind-engine-health.json)"
else
  printf 'engine health: unavailable at http://%s:%s/health\n' "$ENGINE_HOST" "$ENGINE_PORT"
fi

printf 'frontend URL: http://%s:%s/\n' "$ENGINE_HOST" "$WEB_PORT"
printf '\nRecent logs:\n'
for log in "$RUN_DIR"/*.log; do
  [ -f "$log" ] || continue
  printf '\n--- %s ---\n' "$(basename "$log")"
  tail -n 8 "$log"
done
