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

- [ ] Activar backend, base de datos persistente y almacenamiento de archivos para el frontend.
- [ ] Definir entidades para proyectos, hipótesis, evidencias y archivos.
- [ ] Integrar carga, listado y asociación de archivos desde la interfaz.
- [ ] Validar autenticación, autorización por proyecto y procedencia de archivos.

## Rendimiento pendiente

- [ ] Añadir actualización dispersa por familias de hipótesis.
- [ ] Separar arrays numéricos de metadatos explicativos en el hot path completo.
- [ ] Diseñar poda con cotas superiores y estados `parked` reactivables.
- [ ] Medir exactitud frente al modo exacto en espacios masivos.

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
