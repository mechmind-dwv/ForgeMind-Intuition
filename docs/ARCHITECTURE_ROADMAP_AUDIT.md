# Auditoría de arquitectura y roadmap

## Conclusión ejecutiva

La arquitectura propuesta en tres capas **sí se ha conseguido como arquitectura funcional del núcleo**, con una salvedad importante: la Capa 3 existe en dos superficies que todavía deben formalizarse como un único producto distribuible. El repositorio contiene el núcleo Python, la CLI, el formato de proyectos, el servicio de ejecución, el frontend versionable, los benchmarks y la documentación. La aplicación full-stack con autenticación, base de datos persistente y almacenamiento S3 está operativa en el proyecto WebDev asociado, pero no está integrada físicamente bajo la raíz de este repositorio GitHub.

Por tanto, la separación conceptual y los contratos de las capas 1 y 2 están maduros para continuar evolucionando. La arquitectura de producto está **parcialmente consolidada**: es utilizable para desarrollo local y para integración experimental, pero todavía necesita una decisión explícita sobre si el frontend full-stack se incorpora a este repositorio, se mantiene como repositorio separado o se conecta mediante un contrato versionado entre ambos.

## Comparación con las tres capas

| Capa | Propuesta | Estado observado | Evaluación |
|---|---|---|---|
| Capa 1: núcleo algebraico y evidencia | Representación de programas, ejecución, canonicalización, probes, oráculos y falsación activa | `core.py`, `active.py`, `run.py`, pruebas de ejecución/falsación y contratos de proyectos | **Conseguida** para el alcance actual. Falta reforzar aislamiento de ejecución y contratos de oráculo para producción. |
| Capa 2: inferencia y decisión | Bayes explicable, `log_weight`, estados, eliminación, ranking, calibración, advisor y escala numérica | `bayesian.py`, `intuition.py`, `adaptive.py`, `advisor.py`, `vectorized.py`, `exact_block.py`, integración, CI y benchmarks | **Conseguida y validada**. Hay cobertura de invariantes, trazabilidad, exactitud y estrés hasta 10M en modo numérico por bloques. |
| Capa 3: producto y agentes | CLI, proyectos JSON, API para agentes, frontend, persistencia, exportación y operación | CLI, `project.py`, `services/engine_api.py`, frontend visual, documentación, benchmarks y WebDev full-stack separado | **Parcialmente conseguida**. Las superficies existen, pero falta cerrar el contrato operativo entre repositorio Python y aplicación full-stack. |

La dependencia entre capas se mantiene razonablemente limpia: el núcleo no importa la interfaz, la inferencia consume hipótesis y observaciones, y las superficies de uso orquestan proyectos y presentan decisiones. El principal punto de arquitectura pendiente no es conceptual, sino de empaquetado y operación: dónde vive la aplicación full-stack y cómo se versiona junto con el contrato Python.

## Evolución conseguida

ForgeMind evolucionó desde una fuente experimental mínima hacia un motor explicable con una secuencia técnica coherente. Primero se consolidaron representación, ejecución, falsación activa, proyectos reproducibles y CLI. Después se incorporaron priors, actualización bayesiana en log-space, `top_k`, estados de incertidumbre y decisiones con razones. La siguiente etapa separó arrays numéricos de metadatos, añadió actualización dispersa y creó la estrategia exacta por bloques.

La validación de escala progresó desde comparaciones pequeñas hasta un millón de hipótesis y un estrés de diez millones. El benchmark de 10M completó tres rondas con aproximadamente `786 MiB` de RSS máximo bajo un límite de `1,2 GiB`. Posteriormente se corrigió la importación opcional de NumPy, se automatizó CI con el extra vectorizado y se formalizó un protocolo de integración probabilística que mide latencia, memoria, exactitud y trazabilidad. La suite pasó de 65 a 76 pruebas.

En paralelo, la superficie de producto avanzó desde un frontend visual hacia una aplicación full-stack con autenticación, persistencia de proyectos, hipótesis, evidencias y ejecuciones, además de metadatos de archivos en S3. Esa parte está implementada en el proyecto WebDev asociado y debe integrarse o documentarse como sistema compañero del repositorio Python.

## Tareas completadas

| Área | Evidencia |
|---|---|
| Contrato de proyectos externos | `ProjectInput`, validación, formato JSON y compatibilidad legacy |
| Inferencia explicable | Bayes, log-space, posterior, `top_k`, estados y decisiones |
| Poda y reversibilidad | `parked`, cotas superiores, `unpark` y razones |
| Escala | store vectorizado, arrays directos, actualización dispersa y bloques exactos |
| Validación | pruebas unitarias, integración probabilística, exactitud y trazabilidad |
| Rendimiento | benchmarks de 100K, 1M y estrés numérico de 10M |
| Distribución técnica | `pyproject.toml`, CLI, README, arquitectura, roadmap, licencia y plantillas GitHub |
| Calidad operativa | CI con Python 3.12 y extra vectorizado; NumPy opcional en la importación raíz |
| Producto full-stack | frontend neo-editorial, API de motor, auth, DB persistente y almacenamiento S3 en WebDev |

## Pendientes heredados

La fase de software distribuible todavía no tiene una primera versión etiquetada ni un flujo documentado de construcción/publicación del paquete. Tampoco están terminadas la importación/exportación completa de hipótesis, evidencia y reglas, ni la prueba de instalación limpia como artefacto de distribución.

La integración con agentes permanece planeada. Falta definir herramientas versionadas para registrar hipótesis, consultar ranking, proponer probes, aportar evidencia, pedir explicaciones, aparcar/reactivar candidatas y restaurar snapshots. Las operaciones que ejecutan código necesitan aislamiento y auditoría explícitos.

La fase de persistencia full-stack figura como “en diseño” en `ROADMAP.md`, aunque el proyecto WebDev ya tiene una implementación funcional. Esto es una desviación documental que debe resolverse actualizando el roadmap o incorporando formalmente el proyecto WebDev al repositorio. También queda pendiente cerrar la política de archivos eliminados lógicamente, metadatos visibles y pruebas E2E multiusuario.

En rendimiento, sigue pendiente el constructor array-native que evite diccionarios cuando el consumidor ya trabaja con posiciones. También quedan como mejoras futuras los índices invertidos de evidencia, las cotas superiores integradas en el hot path y el paralelismo por lotes. Estas optimizaciones no deben preceder a la definición de sus invariantes y benchmarks.

## Nuevas tareas derivadas

| Prioridad | Tarea nueva | Criterio de cierre |
|---|---|---|
| P0 | Decidir y documentar la estrategia de repositorios para el full-stack | Un contrato versionado indica si vive en esta raíz, en un repositorio hermano o como release coordinado |
| P0 | Actualizar `ROADMAP.md` con el estado real de las fases 4, 5 y 6 | Las fases distinguen “implementado en WebDev” de “publicado en GitHub” |
| P0 | Crear un ciclo E2E reproducible proyecto → evidencia → ejecución → ranking → archivo | Fixture documentado, autorización probada y snapshot recuperable |
| P1 | Preparar primera distribución etiquetada del paquete Python | Build limpio, instalación desde wheel y versión publicada o artefacto firmado |
| P1 | Definir API de herramientas para agentes | Esquemas de entrada/salida, errores, idempotencia, auditoría y restauración |
| P1 | Añadir aislamiento para ejecución de programas y oráculos | Timeouts, límites de recursos, control de procesos y pruebas de escape |
| P1 | Formalizar eliminación lógica y metadatos de archivos | Estado, tamaño, MIME, fechas, propietario, descarga autorizada y E2E |
| P2 | Implementar constructor array-native | Ingestión por posiciones sin materialización de IDs y benchmark de memoria |
| P2 | Crear matriz de regresión de rendimiento | Umbrales de latencia/RSS separados de los tests unitarios y resultados por entorno |
| P2 | Añadir índices invertidos de evidencia y poda integrada | Menos hipótesis visitadas con equivalencia exacta documentada |

## Decisión de arquitectura recomendada

La arquitectura de tres capas debe conservarse. No conviene mezclar la persistencia, la autenticación o los componentes React dentro de los módulos del núcleo Python. La aplicación WebDev se tratará como una **Capa 3 desplegable**, conectada a la Capa 2 mediante el servicio de engine y contratos versionados.

La decisión arquitectónica adoptada es mantener el full-stack WebDev como **repositorio hermano con releases coordinadas**, no copiarlo dentro de este repositorio Python. El motor Python conserva su ciclo de distribución independiente; el contrato HTTP versionado y la versión del engine son la frontera de integración. Cada release full-stack debe declarar la versión mínima del contrato Python que consume.

La siguiente etapa no debería ser otra optimización aislada. Debe cerrar la trazabilidad de extremo a extremo y la distribución: una persona debe poder instalar el motor, crear un proyecto, ejecutar un ciclo de evidencia, recuperar una explicación y continuar desde un snapshot, mientras el frontend muestra exactamente los mismos estados y decisiones que el backend.
