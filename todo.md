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

- [ ] Ejecutar comparación exacta/vectorizada con 1.000.000 de hipótesis.
- [ ] Verificar precisión de posteriores, top-k y eliminaciones.
- [ ] Comparar speedup, memoria y escalabilidad frente al benchmark de 100.000.
- [ ] Guardar resultados y documentar límites observados.

## Escalabilidad de la API vectorizada

- [ ] Añadir una ruta de ingestión por arrays para evitar materializar un millón de IDs y likelihoods como diccionarios Python.
- [ ] Repetir la comparación contra el modo exacto objeto cuando exista un protocolo de memoria compatible con 1.000.000 de hipótesis.

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
