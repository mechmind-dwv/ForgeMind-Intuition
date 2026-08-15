# ForgeMind Intuition — Roadmap

## Dirección del producto

ForgeMind debe evolucionar desde un motor experimental de falsación hacia una herramienta que desarrolladores y agentes puedan integrar en proyectos reales. La dirección no es ocultar la incertidumbre, sino convertirla en una secuencia de decisiones verificables: qué hipótesis compiten, qué evidencia pesa, qué probe discrimina y qué código merece sobrevivir.

## Principios de planificación

El proyecto prioriza primero los contratos y la reproducibilidad, después el rendimiento y finalmente las superficies de colaboración. Ninguna optimización debe romper la trazabilidad. Ninguna interfaz debe presentar una recomendación probabilística como si fuera una prueba. Ninguna integración externa debe convertir secretos o datos de usuario en artefactos versionados.

Las fases se pueden solapar cuando sus contratos ya estén definidos, pero no se considera terminada una fase hasta que sus criterios de aceptación sean verificables con pruebas, benchmarks o documentación ejecutable.

## Estado resumido

| Fase | Estado | Resultado principal |
|---|---|---|
| 0. Núcleo experimental | Completada | representación, ejecución y falsación activa |
| 1. Intuición explicable | Completada | memoria, scoring, calibración y advisor |
| 2. Inferencia estable | Completada | Bayes, `log_weight`, `top_k` y eliminación explicable |
| 3. Escala vectorizada | Completada | arrays NumPy opcionales y benchmark comparativo |
| 4. Software distribuible | En progreso | CLI, proyectos JSON, frontend y documentación |
| 5. Persistencia full-stack | En diseño | API, base de datos y almacenamiento de archivos |
| 6. Integración con agentes | Planeada | contratos de herramientas y ejecución controlada |

## Fase 4 — Software distribuible

El objetivo es que una persona pueda instalar ForgeMind, inicializar un proyecto y obtener una recomendación sin estudiar primero el código interno.

El trabajo base ya incluye un `pyproject.toml` instalable, los comandos `forgemind init`, `forgemind score` y `forgemind advise`, el formato de proyecto reproducible, documentación de tres capas y un frontend versionable. La parte pendiente es cerrar el contrato de entrada para proyectos externos, alinear el frontend integrado con la API real y preparar la primera distribución etiquetada.

### Criterios de finalización

| Criterio | Verificación |
|---|---|
| instalación limpia | entorno virtual nuevo + `pip install -e .` |
| CLI funcional | `init`, `score` y `advise` con fixture documentado |
| API estable | pruebas de contrato para entradas y salidas |
| documentación usable | README ejecutable por una persona nueva |
| distribución | artefacto de paquete y versión etiquetada |

## Fase 5 — Persistencia full-stack

Esta fase conecta la interfaz con un backend real. El modelo mínimo contiene `projects`, `hypotheses`, `evidence` y `projectFiles`. El propietario y el proyecto deben controlar el acceso; los bytes de archivos deben almacenarse en almacenamiento de objetos; la base de datos conserva metadatos y referencias.

El flujo previsto es login, creación de proyecto, carga de configuración o evidencia, persistencia de hipótesis, consulta del ranking, asociación de archivos y visualización de procedencia. La API debe usar procedimientos tipados y separar operaciones públicas de operaciones protegidas.

### Criterios de finalización

| Criterio | Verificación |
|---|---|
| persistencia | crear, leer, actualizar y listar un proyecto real |
| aislamiento | un usuario no puede leer el proyecto de otro |
| archivos | cargar bytes y guardar solo `storageKey` + metadatos |
| resiliencia | estados de carga, error, vacío y reintento |
| seguridad | no hay secretos en código, Git ni respuestas públicas |
| pruebas | Vitest cubre autorización, consultas y metadatos |

## Fase 6 — Integración con agentes

ForgeMind debe exponer operaciones que un agente pueda invocar con límites claros: registrar hipótesis, consultar top-k, proponer el siguiente probe, aportar evidencia, pedir explicación y exportar un snapshot. Las operaciones que ejecutan código o cambian estado deben ser explícitas y auditablemente registradas.

La integración no debe entregar una caja negra que diga “esta es la respuesta”. Debe devolver una acción recomendada, el motivo, las hipótesis afectadas, la evidencia utilizada y el nivel de incertidumbre.

### Criterios de finalización

Un agente podrá ejecutar un ciclo completo en un proyecto de ejemplo, recuperar una explicación reproducible y reanudar la sesión desde un snapshot. Las pruebas deberán cubrir evidencia duplicada, falsación dura, errores del oráculo y restauración de estado.

## Fase 7 — Escala y rendimiento

La siguiente frontera de rendimiento es reducir el coste de visitar hipótesis que no pueden cambiar el top-k. El orden recomendado es actualización dispersa por familia, índices invertidos de evidencia, DAG algebraico, poda con cotas superiores y paralelismo por lotes. El modo `exact` debe permanecer disponible para auditoría.

La métrica no será únicamente tiempo por actualización. También se medirán memoria, número de hipótesis visitadas, diferencia respecto al posterior exacto, calidad del top-k, coste de explicación y capacidad de reactivación de hipótesis aparcadas.

## Riesgos principales

| Riesgo | Consecuencia | Mitigación |
|---|---|---|
| confundir posterior con verdad | decisiones sobre código sin prueba | separar siempre creencia, evidencia y equivalencia |
| poda irreversible prematura | perder soluciones válidas | estados `active`, `parked` y `eliminated` con cotas |
| dependencia NumPy obligatoria | CI base roto y adopción más difícil | extra opcional + importación lazy |
| almacenamiento de bytes en DB | base lenta y costosa | S3/objeto para bytes, DB para metadatos |
| frontend desconectado | demo sin uso real | API tipada y pruebas de integración |
| benchmark no reproducible | conclusiones exageradas | protocolos versionados y resultados con contexto |
| secretos expuestos | acceso no autorizado | `.gitignore`, revocación y secretos gestionados |

## Fuera de alcance por ahora

ForgeMind no promete descubrir automáticamente la verdad de un programa, reemplazar la suite de pruebas del proyecto, ejecutar código arbitrario sin aislamiento, entrenar un modelo fundacional propio ni ofrecer garantías estadísticas universales para cualquier espacio de hipótesis. Esas capacidades requieren contratos de seguridad, evaluación y operación separados.

## Cómo proponer una nueva fase

Una propuesta de fase debe describir el problema que resuelve, la capa afectada, la API que introduce, los invariantes que preserva, el benchmark o prueba que la valida y el riesgo que reduce. Si no puede expresarse esa información, el cambio todavía es una exploración y debe permanecer en `todo.md`, no convertirse en promesa del roadmap.
