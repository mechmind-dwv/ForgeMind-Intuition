# Distribución de ForgeMind

## Paquete Python

ForgeMind se distribuye como paquete Python independiente. La versión del paquete actual es `0.16.0` y el contrato HTTP del engine es `1.0`. El full-stack WebDev se mantiene como repositorio hermano; cada release full-stack debe declarar la versión mínima del paquete/contrato que consume.

Para generar los artefactos desde un checkout limpio:

```bash
python -m pip install -e '.[dev,vectorized]'
python -m build --wheel --sdist
```

Los artefactos generados son un wheel universal y un source distribution. La verificación mínima de instalación se ejecuta en un entorno virtual separado:

```bash
python -m venv /tmp/forgemind-wheel-check
/tmp/forgemind-wheel-check/bin/python -m pip install --no-deps dist/forgemind-*.whl
/tmp/forgemind-wheel-check/bin/python -c 'import forgemind; print(forgemind.__version__)'
```

La suite completa con las capacidades vectorizadas requiere además instalar el extra `vectorized` y las dependencias de desarrollo.

## Versionado coordinado

La release `v0.16.0` del paquete Python establece `ENGINE_API_CONTRACT_VERSION=1.0`. Una aplicación full-stack puede actualizarse de forma independiente si conserva compatibilidad con ese contrato. Un cambio incompatible en payloads, estados, `reason_code` o semántica de resultados requiere una versión mayor del contrato y una release coordinada del repositorio hermano.

El workflow de CI valida cada push y pull request. La publicación de una release debe adjuntar el wheel y el source distribution construidos desde el commit etiquetado, junto con el resultado de las pruebas.
