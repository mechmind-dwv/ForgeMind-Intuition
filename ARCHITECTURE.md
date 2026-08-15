# ForgeMind Intuition — Arquitectura

## Propósito

ForgeMind es un motor local-first para explorar hipótesis sobre código, diseñar experimentos discriminativos, actualizar creencias y conservar una memoria experimental auditable. La arquitectura separa el conocimiento algebraico, la inferencia probabilística y las superficies de uso para que cada capa pueda evolucionar sin convertir la intuición en una caja negra.

> **Principio central:** una probabilidad representa una creencia condicionada a evidencia; una equivalencia algebraica o una falsación producida por un oráculo representa una afirmación semántica con un contrato distinto.

## Vista general en tres capas

```text
┌──────────────────────────────────────────────────────────────┐
│ Capa 3 · Producto y agentes                                 │
│ CLI · API para agentes · frontend · proyectos · exportación  │
└───────────────────────────────▲──────────────────────────────┘
                                │ contratos de uso
┌───────────────────────────────┴──────────────────────────────┐
│ Capa 2 · Inferencia y decisión                               │
│ BayesianHypothesisSet · log_weight · top_k · advisor         │
│ eliminación explicable · calibración · selección de probes   │
└───────────────────────────────▲──────────────────────────────┘
                                │ hipótesis + observaciones
┌───────────────────────────────┴──────────────────────────────┐
│ Capa 1 · Núcleo algebraico y evidencia                       │
│ Node · Hyp · canonicalización · ejecución · equivalencias    │
│ active falsification · oráculos · complejidad                 │
└──────────────────────────────────────────────────────────────┘
```

La dependencia debe fluir de abajo hacia arriba. La Capa 1 no conoce la CLI ni la interfaz; la Capa 2 consume representaciones y observaciones; la Capa 3 orquesta proyectos y presenta decisiones. Ninguna capa debe convertir una puntuación probabilística en una prueba semántica sin registrar esa transición.

## Capa 1 — Núcleo algebraico y evidencia

Esta capa representa qué es una candidata y cómo se ejecuta. Sus componentes principales son `forgemind/core.py` y `forgemind/active.py`.

`core.py` define nodos, hipótesis, canonicalización, composición, mutación, ejecución, complejidad y objetivos. La canonicalización permite detectar representaciones equivalentes o duplicadas antes de que entren en el ranking. La complejidad actúa como señal de parsimonia, no como sustituto de la corrección.

`active.py` construye particiones de predicciones, mide desacuerdo o información, selecciona probes discriminativos, ejecuta el oráculo y elimina candidatas incompatibles. El oráculo es una frontera explícita: ForgeMind puede proponer y ordenar experimentos, pero el resultado debe venir de una evaluación verificable.

### Contratos de la Capa 1

| Contrato | Entrada | Salida | Invariante |
|---|---|---|---|
| Representación | nodos y parámetros | programa canónico | misma semántica → misma clave cuando la regla lo garantiza |
| Ejecución | programa + input | output o error | el resultado conserva procedencia del probe |
| Oráculo | candidato/probe | observación | nunca se confunde con una predicción del modelo |
| Falsación | hipótesis + observación | conjunto superviviente | una falsación dura necesita evidencia explícita |

## Capa 2 — Inferencia y decisión

Esta capa transforma observaciones en creencias actualizadas y decisiones explicables. Sus módulos principales son `bayesian.py`, `intuition.py`, `adaptive.py` y `advisor.py`.

`BayesianHypothesisSet` mantiene priors, posterior y estados `active`, `survivor` o `eliminated`. Internamente usa `log_weight` y normalización estable por log-sum-exp; externamente conserva `posterior` para compatibilidad. Una misma `evidence_id` no puede aplicarse dos veces.

La eliminación tiene dos mecanismos. La **falsación dura** viene de un oráculo o prueba que declara incompatible una hipótesis. La **eliminación por umbral** es una decisión probabilística y reversible solo mediante una operación futura explícita; debe registrar umbral, evidencia y razón.

`VectorizedHypothesisStore` es la variante para espacios grandes. Mantiene arrays NumPy para priors, pesos logarítmicos, posteriores, estados y contadores, mientras que descripciones y explicaciones permanecen en metadatos auxiliares. Se instala con `forgemind[vectorized]` y no debe ser una dependencia obligatoria del núcleo base.

`intuition.py` calcula una puntuación explicable combinando novedad, similitud, compresión, falsabilidad y complejidad. `adaptive.py` calibra la confianza con evidencia ponderada y shrinkage. `advisor.py` expone una recomendación para agentes: qué hipótesis probar primero y qué evidencia falta.

### Contratos de la Capa 2

| Contrato | Entrada | Salida | Invariante |
|---|---|---|---|
| Actualización | prior + likelihood + evidencia | posterior | masa activa ≈ 1 |
| Ranking | distribución + `k` | top-k | no se presenta como prueba de verdad |
| Eliminación | posterior/umbral o falsación | decisión | siempre incluye razón y procedencia |
| Asesoría | estado experimental | siguiente acción | recomienda; no sustituye al oráculo |

## Capa 3 — Producto y agentes

Esta capa hace que el motor sea utilizable por proyectos reales. Incluye `project.py`, `cli.py`, los benchmarks, la documentación y el frontend integrado en `frontend/`.

El formato de proyecto conserva hipótesis, priors, probes, targets, resultados y configuración en JSON. La CLI expone `forgemind init`, `forgemind score` y `forgemind advise`. La interfaz debe consumir contratos tipados y mostrar estados de carga, error, vacío y procedencia.

El frontend visual actual es una superficie de exploración: muestra hipótesis, evidencia, puntuaciones y la próxima prueba. La futura integración full-stack debe usar una API explícita para persistir proyectos, hipótesis, evidencias y metadatos de archivos. Los bytes de archivos deben vivir en almacenamiento de objetos; la base de datos solo conserva `storageKey`, URL, tipo MIME, tamaño y relación con el proyecto.

### Contratos de la Capa 3

| Superficie | Responsabilidad | No debe hacer |
|---|---|---|
| CLI | inicializar y ejecutar flujos reproducibles | ocultar evidencia o alterar el núcleo sin registrar cambios |
| Proyecto JSON | transportar estado portable | guardar secretos o bytes grandes |
| Frontend | explorar, comparar y disparar acciones | inventar posterior, reviews o evidencia |
| Agente | pedir ranking, probe o explicación | declarar verdad sin evaluación |
| Benchmark | medir protocolos | presentar datos sintéticos como resultados reales |

## Flujo de una decisión

```text
1. La Capa 1 genera o recibe candidatas algebraicas.
2. La Capa 2 asigna prior y calcula qué observación discriminaría mejor.
3. La Capa 3 solicita o ejecuta el probe mediante un oráculo autorizado.
4. La observación vuelve a la Capa 2 con source y evidence_id.
5. La Capa 2 actualiza log_weight, posterior y estado.
6. La Capa 3 muestra top-k, razón y siguiente acción.
7. La Capa 1 puede componer supervivientes para el siguiente ciclo.
```

## Reglas de evolución

Las nuevas optimizaciones deben preservar la API base o declarar una versión mayor. Toda aproximación debe indicar su modo de exactitud: `exact`, `bounded` o `approximate`. Toda poda debe poder responder qué hipótesis se aparcó, qué cota se usó y cómo reactivarla. Toda evidencia debe conservar identificador, descripción, origen y relación con las hipótesis afectadas.

La separación de capas también sirve para probar. La Capa 1 se prueba con equivalencia y ejecución; la Capa 2 con invariantes probabilísticos, estabilidad numérica y explicaciones; la Capa 3 con contratos de CLI, persistencia, integración y experiencia de usuario.
