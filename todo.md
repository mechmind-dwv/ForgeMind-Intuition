# ForgeMind Intuition — TODO operativo

Este archivo registra el estado del producto y conserva las tareas históricas. Las tareas completadas se mantienen como referencia; las pendientes representan trabajo que todavía necesita implementación o validación.

## Completado

- [x] Reorganizar el código fuente para que el núcleo Python y el frontend vivan bajo una raíz de proyecto clara.
- [x] Añadir una CLI instalable para puntuar hipótesis y recomendar el siguiente experimento.
- [x] Añadir un formato de proyecto reproducible con configuración, probes, targets y resultados.
- [x] Documentar instalación, primeros pasos, API Python y flujo de integración con agentes de código.
- [x] Validar una instalación limpia, pruebas de regresión y ejecución desde la raíz.
- [x] Implementar pesos logarítmicos manteniendo compatibilidad con `posterior`.
- [x] Añadir `top_k(k)` sin ordenar el conjunto completo.
- [x] Crear benchmark reproducible de latencia, memoria y exactitud.
- [x] Corregir la importación de NumPy para que el núcleo base funcione sin el extra vectorizado.
- [x] Validar CI sin NumPy y pruebas completas con el extra vectorizado.
- [x] Diseñar almacenamiento vectorizado con arrays numéricos y metadatos diferidos.
- [x] Comparar memoria y throughput entre objetos Python y almacenamiento vectorizado.
- [x] Publicar la optimización de rendimiento en el repositorio GitHub.
- [x] Reintentar el push desde el sandbox y documentar el procedimiento local cuando apareció el 403.
- [x] Confirmar el estado remoto tras reactivar y guardar Manus Connector.
- [x] Crear la presentación sobre la arquitectura algebraica y probabilística de ForgeMind.
- [x] Crear `ARCHITECTURE.md` con la arquitectura en tres capas.
- [x] Reescribir `README.md` como guía de usuarios, integradores y colaboradores.
- [x] Crear `ROADMAP.md` con fases, riesgos y criterios verificables.

## Núcleo experimental pendiente

- [x] Definir el contrato de entrada para proyectos externos y candidatas de código.
- [x] Validar esquema de proyecto, candidatas, probes y targets con errores legibles.
- [x] Añadir carga desde JSON y normalización de candidatas externas.
- [x] Implementar eliminación de hipótesis con razones, umbrales y estados de incertidumbre.
- [x] Añadir estados `active`, `uncertain`, `parked`, `survivor` y `eliminated`.
- [x] Registrar razones, evidencia, umbral y reversibilidad de cada decisión.
- [ ] Añadir pruebas y documentación adicional de integración del módulo probabilístico.
- [ ] Definir benchmarks de latencia, memoria, exactitud y trazabilidad como protocolo estable.

## Producto distribuible pendiente

- [ ] Preparar una estrategia de distribución y publicación del paquete.
- [ ] Añadir importación y exportación de hipótesis, evidencia y reglas.
- [x] Conectar el frontend con datos reales del motor mediante una API local o servicio de ejecución.
- [x] Alinear la copia de `frontend/` con el contrato de la API pública.

## Full-stack pendiente

- [x] Activar backend, base de datos persistente y almacenamiento de archivos para el frontend.
- [x] Definir entidades para proyectos, hipótesis, evidencias y archivos.
- [x] Integrar carga, listado y asociación de archivos desde la interfaz.
- [x] Validar autenticación, autorización por proyecto y procedencia de archivos.

## Rendimiento pendiente

- [x] Añadir actualización dispersa por familias de hipótesis.
- [x] Separar arrays numéricos de metadatos explicativos en el hot path completo.
- [x] Diseñar poda con cotas superiores y estados `parked` reactivables.
- [x] Medir exactitud frente al modo exacto en espacios masivos.

## Comunidad GitHub pendiente

- [x] Añadir descripción comunitaria del repositorio.
- [x] Crear `CODE_OF_CONDUCT.md`.
- [x] Crear `CONTRIBUTING.md`.
- [x] Crear `SECURITY.md`.
- [x] Añadir licencia MIT explícita.
- [x] Crear plantillas de issues y pull requests.
- [x] Preparar el anuncio inicial de GitHub Discussions.
- [x] Verificar sintaxis y reconocimiento remoto de las plantillas de issues y pull requests.
- [x] Ejecutar la suite completa de pruebas unitarias y revisar errores de dependencias.

## Alineación con API pública

- [x] Inventariar el contrato público de la API y los adaptadores usados por frontend/.
- [x] Alinear rutas, payloads, respuestas y tipos compartidos.
- [x] Corregir estados de carga, error, vacío y compatibilidad en frontend/.
- [x] Ejecutar pruebas, build y verificación responsive de frontend/.

## Activación full-stack

- [x] Auditar backend, conexión de base de datos y helpers de almacenamiento existentes.
- [x] Verificar migraciones y tablas persistentes para proyectos, hipótesis, evidencias, ejecuciones y archivos.
- [x] Verificar endpoints protegidos y flujo de subida/listado/descarga de archivos.
- [x] Ejecutar pruebas, build y comprobación de extremo a extremo.

## Verificación de entidades persistentes

- [x] Auditar entidades de proyectos, hipótesis, evidencias y archivos frente al esquema real y sus migraciones.
- [x] Verificar relaciones, claves foráneas, índices y autorización por propietario.
- [x] Validar procedimientos de creación, consulta, ejecución y almacenamiento asociados a estas entidades.

## Integración de archivos en la interfaz

- [x] Auditar controles de archivo, procedimientos protegidos y helpers S3 existentes.
- [x] Completar subida y asociación de archivos al proyecto activo.
- [x] Completar listado persistido y descarga mediante URL servida.
- [x] Validar estados de carga, error, vacío, autorización y responsive.

## Seguridad de archivos y proyectos

- [x] Verificar rechazo de usuarios anónimos en consultas y mutaciones protegidas.
- [x] Verificar aislamiento entre propietarios al listar y descargar archivos.
- [x] Verificar que la subida solo acepte proyectos propios y metadatos válidos.
- [x] Ejecutar pruebas de seguridad, build y comprobación del flujo protegido.

## Actualización dispersa por familias

- [x] Definir la representación de familias y el índice de hipótesis afectadas.
- [x] Implementar actualización parcial sin recomputar familias no afectadas.
- [x] Mantener razones, estados y compatibilidad con la actualización exacta existente.
- [x] Añadir pruebas de equivalencia y benchmark de trabajo evitado.

## Separación del hot path vectorizado

- [x] Auditar qué campos numéricos y explicativos se tocan durante observe y top_k.
- [x] Separar estructuras numéricas, índices de familia y metadatos de explicación.
- [x] Mantener snapshots, razones y compatibilidad sin añadir objetos al hot path.
- [x] Añadir pruebas y benchmark de memoria, latencia y exactitud.

## Poda reversible con cotas superiores

- [x] Definir una cota superior segura para hipótesis con evidencia futura.
- [x] Implementar poda a `parked` sin confundirla con falsación o eliminación.
- [x] Permitir reactivar hipótesis parked y conservar su trazabilidad.
- [x] Añadir pruebas de seguridad, exactitud y benchmark de trabajo evitado.

## Exactitud vectorizada frente a modo exacto

- [x] Definir tolerancias para posteriores, ranking y estados entre implementaciones.
- [x] Implementar benchmark reproducible en espacios masivos con evidencia compartida.
- [x] Comparar error máximo, error medio, top-k y decisiones de eliminación.
- [x] Guardar resultados, ejecutar la suite y publicar la validación.

## Benchmark ampliado a un millón

- [x] Ejecutar comparación exacta/vectorizada con 1.000.000 de hipótesis.
- [x] Verificar precisión de posteriores, top-k y eliminaciones.
- [x] Comparar speedup, memoria y escalabilidad frente al benchmark de 100.000.
- [x] Guardar resultados y documentar límites observados.

## Escalabilidad de la API vectorizada

- [x] Añadir una ruta de ingestión por arrays para evitar materializar un millón de IDs y likelihoods como diccionarios Python.
- [x] Evaluar la comparación contra el modo exacto objeto bajo un protocolo de memoria controlada; a 1.000.000 no es viable con la representación actual.

## Ingestión directa por arrays

- [x] Añadir una ruta de observación que acepte likelihoods NumPy sin diccionarios Python.
- [x] Mantener `observe()` y la trazabilidad por IDs como APIs compatibles.
- [x] Adaptar el benchmark de un millón a la ruta directa.
- [x] Verificar precisión, top-k, estados, memoria y speedup.

## Comparación final de escalabilidad

- [x] Reejecutar comparación exacta/vectorizada a 100.000 y 1.000.000 con la API directa por arrays.
- [x] Verificar posteriores, top-k y conjuntos de eliminados en ambas escalas.
- [x] Comparar speedup, memoria numérica y crecimiento entre escalas.
- [x] Consolidar resultados y límites observados en un artefacto reproducible.

## Siguiente lista técnica de escalabilidad

- [x] Diseñar un protocolo de referencia exacta por bloques que permita comparar 1.000.000 de hipótesis sin materializar objetos Python.
- [x] Ejecutar un escenario con eliminaciones no vacías para validar decisiones de poda y estados.
- [x] Medir memoria total del proceso además de memoria de arrays numéricos.
- [ ] Evaluar un constructor array-native que evite diccionarios de IDs cuando el consumidor ya trabaja con posiciones.
- [x] Documentar criterios de aceptación para precisión, top-k, estados y escalabilidad.

## Medición de memoria total

- [x] Instrumentar RSS máximo del proceso durante benchmark y distinguirlo de memoria de arrays.
- [x] Ejecutar medición a 100.000 y 1.000.000 de hipótesis.
- [x] Comparar crecimiento de RSS, buffers temporales y estado numérico.
- [x] Documentar límites de memoria y validar la suite.

## Profiling de metadatos Python

- [x] Instrumentar snapshot de asignaciones durante la construcción del store de 1.000.000.
- [x] Separar contribuciones de IDs, diccionarios, índices, creencias y metadatos explicativos.
- [x] Comparar RSS, tracemalloc y memoria numérica del store.
- [x] Guardar hotspots y límites observados para priorizar la siguiente optimización.

## Comparación objeto a un millón

- [x] Diseñar una referencia exacta acotada por bloques sin duplicar entradas innecesarias.
- [x] Ejecutar comparación objeto/vectorizada con límite de memoria y timeout explícitos.
- [x] Verificar precisión, top-k, eliminaciones y condiciones de terminación.
- [x] Documentar si la comparación completa es viable o queda bloqueada por memoria.

**Resultado de viabilidad:** el modo exacto basado en `HypothesisBelief` completa 100.000 hipótesis con `185.64 MiB` de RSS máximo, pero a 1.000.000 falla durante la construcción bajo un límite controlado de `900 MiB`. La comparación completa de precisión a un millón sigue siendo técnicamente bloqueada; la referencia válida a esa escala es la implementación numérica por arrays y bloques.

## Estrategia exacta por bloques para modo objeto

- [x] Definir un presupuesto de memoria y tamaño de bloque reproducible.
- [x] Implementar estado numérico por bloques con metadatos explicativos diferidos.
- [x] Mantener normalización global mediante acumulación log-sum-exp por bloques.
- [x] Mantener top-k global, eliminaciones y trazabilidad sin materializar un millón de objetos.
- [x] Validar exactitud y RSS frente a la referencia vectorizada y documentar el límite del modo objeto.

## Stress test a 10 millones

- [x] Ejecutar la estrategia por bloques con 10.000.000 de hipótesis y límite de memoria explícito.
- [x] Medir RSS máximo, memoria numérica, buffers temporales y latencia por ronda.
- [x] Verificar normalización, top-k y estados en el escenario que complete.
- [x] Documentar si el proceso completa o queda limitado por memoria/tiempo y guardar el artefacto reproducible.

## Compatibilidad sin NumPy

- [x] Evitar que la importación raíz de `forgemind` requiera NumPy en instalaciones base.
- [x] Mantener el módulo exacto por bloques disponible cuando se instala el extra vectorizado.
- [x] Validar CI sin NumPy y ejecutar la suite completa con NumPy.

## Automatización CI/CD

- [x] Añadir workflow de GitHub Actions para instalar el extra vectorizado y ejecutar la suite completa.
- [x] Validar localmente los mismos comandos del workflow y documentar el comportamiento ante fallos.

## Cobertura de validación de exact_block

- [x] Añadir pruebas parametrizadas para priors vacíos, formas inválidas y valores no finitos.
- [x] Ejecutar la suite vectorizada completa y publicar la ampliación de cobertura.

## Integración probabilística y protocolo estable

- [x] Añadir pruebas de integración del módulo probabilístico con evidencias, eliminación, trazabilidad y selección top-k.
- [x] Documentar el contrato de integración y criterios de exactitud del módulo probabilístico.
- [x] Definir un benchmark reproducible de latencia, memoria, exactitud y trazabilidad.
- [x] Ejecutar el protocolo estable y guardar resultados versionados.

## Auditoría de arquitectura y roadmap

- [x] Comparar la arquitectura propuesta en tres capas con el estado real del repositorio.
- [x] Analizar ROADMAP.md y clasificar evolución, logros, pendientes y desviaciones.
- [x] Consolidar nuevas tareas técnicas y de producto derivadas del análisis.
- [x] Actualizar todo.md con la evaluación y publicar el estado revisado.

## Nuevas prioridades derivadas de la auditoría

### P0 — Consolidación de producto

- [x] Decidir y documentar si el full-stack WebDev se incorpora a este repositorio, se mantiene como repositorio hermano o se publica mediante releases coordinadas.
- [x] Actualizar el contrato versionado entre el motor Python, `services/engine_api.py` y la aplicación full-stack.
- [ ] Crear un ciclo E2E reproducible de proyecto → evidencia → ejecución → ranking → archivo → snapshot.
- [x] Actualizar los criterios de finalización de las fases 4 y 5 con la implementación real de WebDev.

### P1 — Distribución, agentes y seguridad

- [ ] Preparar la primera distribución etiquetada del paquete Python con build limpio e instalación desde wheel.
- [ ] Definir herramientas versionadas para agentes: registrar hipótesis, consultar top-k, proponer probes, aportar evidencia, explicar, aparcar, reactivar y restaurar snapshots.
- [ ] Añadir aislamiento de ejecución para programas y oráculos con timeout, límites de recursos y auditoría.
- [ ] Completar pruebas E2E multiusuario de autorización, archivos y recuperación de sesión.
- [ ] Implementar eliminación lógica y metadatos completos de archivos en la superficie full-stack.

### P2 — Escala y observabilidad

- [x] Implementar el constructor array-native sin diccionarios de IDs cuando el consumidor opere por posiciones.
- [x] Añadir una matriz de regresión de rendimiento con umbrales separados para latencia, RSS, exactitud y trazabilidad.
- [ ] Medir número de hipótesis visitadas, coste de explicación y reactivación en escenarios masivos.
- [ ] Evaluar índices invertidos de evidencia, poda integrada y paralelismo por lotes sin perder el modo exacto auditable.

## Ejecución priorizada P0–P2

- [x] Auditar y fijar el contrato entre `forgemind`, `services/engine_api.py` y el full-stack WebDev.
- [x] Documentar la decisión de consolidación de repositorios y los límites de publicación coordinada.
- [ ] Implementar y validar las tareas P0 antes de tachar las tareas dependientes P1/P2.
