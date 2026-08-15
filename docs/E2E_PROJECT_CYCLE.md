# Ciclo E2E reproducible de proyecto a snapshot

El ciclo E2E oficial se ejecuta con `python benchmarks/e2e_project_cycle.py` y usa fixtures versionados en `fixtures/e2e/`. No depende de una base de datos, S3 ni un servicio externo: reproduce el contrato del engine directamente para que la prueba sea determinista en CI.

El fixture `project.json` representa un proyecto realista de transformación de listas con tres candidatas, probes, target y conocimiento previo. `evidence.json` contiene dos observaciones de un oráculo identificado, cada una con likelihoods `P(E|H)` y procedencia. El runner carga y valida el proyecto, aplica las evidencias al motor bayesiano, ejecuta el endpoint público Python `/v1/evaluate` mediante sus modelos reales, calcula el ranking posterior y el ranking del advisor, archiva la evidencia con SHA-256 y metadatos, genera `snapshot.json` y restaura el estado reproduciendo las evidencias.

| Paso | Evidencia verificable |
|---|---|
| Proyecto | `ForgeMindProject.from_dict()` valida `schema_version`, IDs, programas y probes |
| Evidencia | `EvidenceObservation` valida identificadores, descripción y likelihoods |
| Ejecución | `EvaluateRequest`/`evaluate()` usa el contrato engine API `1.0` |
| Ranking | posterior bayesiano y ranking de `advisor` se serializan por ID estable |
| Archivo | copia content-addressed local con MIME, tamaño y SHA-256 |
| Snapshot | proyecto, evidencia, rankings, respuesta del engine y archivo se guardan en JSON |
| Restauración | replay del snapshot reproduce el estado posterior y verifica el hash del archivo |

La prueba automatizada está en `tests/test_e2e_cycle.py`. La salida local validada fue `sorting-pipeline-e2e`, tres candidatas, dos evidencias, contrato engine `1.0`, restauración correcta y `91` pruebas totales correctas.

Este ciclo valida reproducibilidad del núcleo. La variante de producción debe sustituir el archivo local por el flujo full-stack de S3 y persistencia, conservando los mismos campos, hashes, IDs de evidencia y snapshot. La autenticación multiusuario y la recuperación desde la base de datos siguen siendo una extensión separada del E2E local.
