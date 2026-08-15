# Contrato versionado del ForgeMind Engine API

## Estado

La versión actual del contrato es **1.0**. El servicio se implementa en [`services/engine_api.py`](../services/engine_api.py) y el adaptador full-stack se encuentra en `server/routers.ts` del proyecto WebDev asociado.

La versión del contrato se expone en `/health` como `contract_version` y en la respuesta de `POST /v1/evaluate`. Un cambio incompatible debe incrementar la versión mayor; los campos opcionales y extensiones compatibles pueden conservar la versión mayor y documentarse como una revisión menor.

## `GET /health`

Respuesta `200`:

```json
{
  "status": "ok",
  "engine": "forgemind-python",
  "version": "0.16",
  "contract_version": "1.0"
}
```

`status=ok` indica que el proceso responde. No sustituye una comprobación de disponibilidad de la base de datos, almacenamiento de archivos o servicio full-stack.

## `POST /v1/evaluate`

Request:

```json
{
  "project": {
    "schema_version": "1.0",
    "name": "mi-proyecto",
    "candidates": [
      {
        "id": "candidate-1",
        "description": "candidata explicable",
        "source": "agent",
        "program": [{"kind": "U", "name": "sort"}],
        "metadata": {"language": "python"}
      }
    ],
    "probes": [[3, 1, 2]],
    "targets": [],
    "metadata": {}
  }
}
```

Response `200`:

```json
{
  "project": "mi-proyecto",
  "candidate_count": 1,
  "results": [],
  "engine": "forgemind-python",
  "contract_version": "1.0"
}
```

`results` contiene recomendaciones serializadas por `CandidateAdvice`. El consumidor debe tratarlas como decisiones explicables y no como pruebas semánticas. La procedencia, el motivo y la incertidumbre deben permanecer visibles en la superficie full-stack.

Los errores de validación del proyecto, campos inválidos o IDs inconsistentes devuelven `422` con un campo `detail`. Los errores de disponibilidad del proceso o del transporte no deben reinterpretarse como evidencia sobre las hipótesis.

## Reglas de compatibilidad

| Cambio | Acción |
|---|---|
| Añadir campo opcional | Compatible; documentar en la revisión menor |
| Cambiar significado de un campo | Nueva versión mayor |
| Eliminar o renombrar campo | Nueva versión mayor |
| Cambiar estados o `reason_code` | Nueva versión mayor o migración explícita |
| Cambiar error de validación | Mantener `422`; documentar el nuevo detalle |

El adaptador full-stack debe comprobar que `contract_version` está presente y registrar `engine` y `contract_version` junto con cada ejecución persistida. El contrato no incluye bytes de archivos: los archivos se gestionan por el flujo S3 del full-stack y solo sus metadatos se asocian al proyecto.
