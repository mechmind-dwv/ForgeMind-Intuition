#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="${FORGEMIND_RUN_DIR:-$ROOT/.forgemind-run}"
ENGINE_HOST="${FORGEMIND_ENGINE_HOST:-127.0.0.1}"
ENGINE_PORT="${FORGEMIND_ENGINE_PORT:-8787}"
WEB_PORT="${FORGEMIND_WEB_PORT:-3000}"
MODE="${1:-dev}"

mkdir -p "$RUN_DIR"
cd "$ROOT"

start_process() {
  local name="$1"; shift
  local pid_file="$RUN_DIR/$name.pid"
  local log_file="$RUN_DIR/$name.log"
  if [ -f "$pid_file" ] && kill -0 "$(cat "$pid_file")" 2>/dev/null; then
    printf '%s ya está activo (PID %s)\n' "$name" "$(cat "$pid_file")"
    return 0
  fi
  rm -f "$pid_file"
  nohup "$@" >"$log_file" 2>&1 &
  echo $! >"$pid_file"
  printf '%s iniciado (PID %s, log %s)\n' "$name" "$(cat "$pid_file")" "$log_file"
}

command -v python >/dev/null || { echo 'Falta python.' >&2; exit 1; }

if [ "$MODE" = "production" ]; then
  command -v pnpm >/dev/null || { echo 'Falta pnpm.' >&2; exit 1; }
  (cd "$ROOT/frontend" && pnpm build)
  start_process engine python -m uvicorn services.engine_api:app --host "$ENGINE_HOST" --port "$ENGINE_PORT"
  start_process web env NODE_ENV=production PORT="$WEB_PORT" FORGEMIND_ENGINE_URL="http://$ENGINE_HOST:$ENGINE_PORT" pnpm --dir "$ROOT/frontend" start
else
  command -v pnpm >/dev/null || { echo 'Falta pnpm.' >&2; exit 1; }
  start_process engine python -m uvicorn services.engine_api:app --host "$ENGINE_HOST" --port "$ENGINE_PORT"
  start_process frontend pnpm --dir "$ROOT/frontend" dev --host "$ENGINE_HOST" --port "$WEB_PORT"
fi

printf '\nMotor:   http://%s:%s/health\n' "$ENGINE_HOST" "$ENGINE_PORT"
printf 'Frontend: http://%s:%s/\n' "$ENGINE_HOST" "$WEB_PORT"
printf 'Estado:  bash scripts/forge-status.sh\n'
printf 'Parar:   bash scripts/forge-stop.sh\n'
