# ForgeMind Runbook

Este runbook reúne los comandos para arrancar y probar el motor Python, la API HTTP y la aplicación frontend/backend. Está pensado para ejecutarse desde la raíz del repositorio, tanto en Termux como en un Linux de escritorio.

## Preparación

```sh
cd ~/ForgeMind-Intuition
source .venv/bin/activate 2>/dev/null || true
python -m pip install -e '.[vectorized,dev]'
cd frontend
pnpm install --frozen-lockfile
cd ..
```

En Termux, `python-numpy` puede instalarse con `pkg install python-numpy` antes de ejecutar la instalación Python.

## Ejecutar en desarrollo

Desde la raíz del repositorio:

```sh
bash scripts/forge-start.sh dev
```

El motor queda en `http://127.0.0.1:8787` y Vite en `http://127.0.0.1:3000`. La aplicación frontend utiliza el adaptador `/api/engine`; para el backend Express de producción usa `FORGEMIND_ENGINE_URL`.

Para inspeccionar procesos y salud:

```sh
bash scripts/forge-status.sh
```

Los logs se guardan en `.forgemind-run/`. Para detener solo los procesos lanzados por el script:

```sh
bash scripts/forge-stop.sh
```

## Ejecutar el modo de producción local

El modo producción compila Vite y Express antes de arrancar:

```sh
bash scripts/forge-start.sh production
```

La aplicación servida por Express queda en `http://127.0.0.1:3000` y el motor continúa en el puerto 8787. No uses simultáneamente `dev` y `production` en los mismos puertos; detén primero los procesos anteriores.

## Ejecutar toda la batería de pruebas

```sh
bash scripts/forge-test.sh
```

La batería comprueba la suite Python, arranca una instancia temporal del Engine API, valida `/health`, publica un `ProjectInput` mínimo en `/v1/evaluate`, ejecuta typecheck y tests del frontend y termina con un build de producción. La instancia temporal de la API se cierra automáticamente incluso si una prueba falla.

## Diagnóstico rápido

Si aparece `address already in use`, detén los procesos gestionados y vuelve a intentarlo:

```sh
bash scripts/forge-stop.sh
bash scripts/forge-start.sh dev
```

Si el frontend no puede conectar con el motor, comprueba:

```sh
bash scripts/forge-status.sh
curl -fsS http://127.0.0.1:8787/health
```

Si falta un ejecutable, comprueba:

```sh
command -v python
command -v pnpm
python --version
pnpm --version
```

No uses `git add .` para publicar logs, builds o secretos. Los scripts guardan sus archivos de ejecución en `.forgemind-run/`, que debe permanecer fuera del control de versiones.
