# ForgeMind Intuition

> **Un motor explicable para explorar hipótesis sobre código, diseñar experimentos y convertir evidencia en decisiones verificables.**

ForgeMind Intuition es un software local-first para síntesis de programas, falsación activa e inferencia experimental. En lugar de tratar la generación de código como una búsqueda ciega, mantiene una población de candidatas, estima qué hipótesis merece la siguiente prueba, conserva la evidencia y elimina alternativas de manera explicable.

La intuición de ForgeMind no pretende ser una corazonada. Es una combinación auditable de representación algebraica, memoria de experimentos, actualización probabilística, compresión y selección de acciones.

## Qué problema resuelve

Un sistema puede encontrar un programa que encaje con ejemplos conocidos y aun así estar equivocado. ForgeMind cambia el objetivo operativo:

> **No basta con encontrar una candidata compatible; hay que buscar el experimento que pueda demostrar que las candidatas actuales están equivocadas.**

El ciclo principal es:

```text
candidatas → predicciones → probe discriminativo → oráculo
     ↑                                      ↓
composición ← supervivientes ← falsación ← evidencia
```

Cada decisión debe conservar su procedencia. Un posterior es una creencia condicionada a evidencia; una equivalencia algebraica o una falsación dura requiere un contrato semántico distinto.

## Estado actual

La versión actual contiene representación y ejecución de programas, búsqueda activa frente a una línea base pasiva, memoria de conocimiento, puntuación de intuición, calibración adaptativa, inferencia bayesiana explicable, ranking top-k, almacenamiento vectorizado opcional y una CLI instalable.

| Área | Estado | Punto de entrada |
|---|---|---|
| Núcleo algebraico | Disponible | `forgemind/core.py` |
| Falsación activa | Disponible | `forgemind/active.py` |
| Inferencia bayesiana | Disponible | `forgemind/bayesian.py` |
| Almacenamiento vectorizado | Disponible como extra | `forgemind/vectorized.py` |
| Proyectos reproducibles | Disponible | `forgemind/project.py` |
| CLI | Disponible | `forgemind/cli.py` |
| Frontend visual | Incluido | `frontend/` |
| Presentación arquitectónica | Incluida | `presentation/` |
| Backend full-stack | En integración | ver `ROADMAP.md` |

## Instalación

ForgeMind requiere Python 3.11 o posterior. Para instalar el núcleo y sus comandos:

```bash
git clone https://github.com/mechmind-dwv/ForgeMind-Intuition.git
cd ForgeMind-Intuition
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

Para desarrollo y pruebas:

```bash
python -m pip install -e '.[dev]'
python -m pytest -q
```

El almacenamiento vectorizado es opcional porque el núcleo base no debe obligar a instalar NumPy:

```bash
python -m pip install -e '.[vectorized]'
```

Sin ese extra, `import forgemind` continúa funcionando y las pruebas vectorizadas se omiten correctamente.

## Inicio rápido con la CLI

Inicializa un proyecto reproducible, inspecciona su recomendación y puntúa candidatas:

```bash
forgemind init forgemind.project.json
forgemind advise forgemind.project.json
forgemind score forgemind.project.json
```

El archivo de proyecto está pensado para viajar con el código y los protocolos, no para sustituir un almacén de archivos ni para guardar secretos. Sus campos principales son candidatas, probes, targets, resultados y configuración experimental.

## Contrato de entrada para proyectos externos

Un proyecto externo se transporta como JSON con `schema_version`, `name`, `candidates`, `probes`, `targets` y `metadata`. Cada candidata debe tener un identificador estable, descripción, programa y origen. El lector mantiene compatibilidad con el formato legacy en el que una candidata era directamente una lista de nodos, pero los proyectos nuevos deben usar el formato rico:

```json
{
  "schema_version": "1.0",
  "name": "mi-proyecto",
  "candidates": [
    {
      "id": "candidate-sort-01",
      "description": "ordena la entrada ascendentemente",
      "source": "agent",
      "program": [{"kind": "U", "name": "sort"}],
      "metadata": {"language": "python"}
    }
  ],
  "probes": [[3, 1, 2]],
  "targets": [],
  "metadata": {"repository": "local"}
}
```

`ProjectInput.from_dict()` valida versión, nombres, IDs únicos, programas no vacíos, probes enteros y tipos de metadata. Los errores se expresan como `ProjectValidationError` con la ruta del campo inválido. Los targets no se inventan: los proporciona el integrador mediante su oráculo.

## Uso del motor bayesiano

`BayesianHypothesisSet` mantiene un conjunto normalizado de creencias. Internamente trabaja con `log_weight` para evitar underflow y usa normalización estable; la propiedad `posterior` se conserva para compatibilidad.

```python
from forgemind.bayesian import BayesianHypothesisSet, EvidenceObservation

beliefs = BayesianHypothesisSet.from_priors(
    {
        "H1": "sort preserva el orden",
        "H2": "reverse preserva el orden",
    },
    priors={"H1": 0.5, "H2": 0.5},
)

beliefs.observe(EvidenceObservation(
    evidence_id="probe-01",
    description="la salida conserva el orden ascendente",
    likelihoods={"H1": 0.9, "H2": 0.2},
    source="property-test",
))

for belief in beliefs.top_k(2):
    print(belief.hypothesis_id, belief.posterior, belief.state)
```

La misma `evidence_id` no se puede aplicar dos veces. Una falsación dura se registra separadamente de una eliminación por umbral, y cada decisión conserva razones y procedencia.

El estado de una hipótesis distingue incertidumbre de falsación:

| Estado | Significado | ¿Se muestra en `top_k()`? | ¿Es reversible? |
|---|---|---:|---:|
| `active` | todavía no hay señal suficiente | sí | sí |
| `uncertain` | posterior bajo, pero falta evidencia mínima | sí | sí |
| `parked` | aparcada por decisión del usuario o agente | no por defecto | sí |
| `survivor` | supera el umbral actual | sí | sí |
| `eliminated` | falsada o descartada tras evidencia suficiente | no por defecto | no dentro del ciclo |

Para decisiones explícitas se usan `eliminate_hypothesis(hypothesis_id, reason=..., evidence_ids=...)`, `park(...)` y `unpark(...)`. El resultado incluye `reason_code`, `reversible`, `state`, posterior, umbral y evidencia asociada.

## Uso vectorizado para espacios grandes

`VectorizedHypothesisStore` separa el estado numérico de los metadatos. Los arrays `priors`, `log_weights`, `posteriors`, `states` y `evidence_counts` evitan crear un objeto Python completo por hipótesis. `observe()` acepta actualizaciones dispersas y `top_k(k)` usa partición NumPy en lugar de ordenar todo el conjunto.

```python
from forgemind import VectorizedHypothesisStore

store = VectorizedHypothesisStore({
    "H1": "candidata A",
    "H2": "candidata B",
})
store.observe(
    {"H1": 0.9, "H2": 0.2},
    "probe-01",
    reason="property-test",
)
print(store.top_k(1)[0])
```

El benchmark comparativo se ejecuta con:

```bash
python benchmarks/vectorized_vs_object.py --hypotheses 10000 --repeats 3 --top-k 20
```

Los resultados locales se guardan en `benchmarks/results/`. Son mediciones de referencia de una máquina concreta, no un SLA.

## Arquitectura

ForgeMind se organiza en tres capas. La **Capa 1** contiene el núcleo algebraico, la representación de programas, la canonicalización, la ejecución y los oráculos. La **Capa 2** contiene la inferencia, el ranking, la eliminación explicable, la calibración y el asesoramiento. La **Capa 3** contiene la CLI, los proyectos reproducibles, los benchmarks, el frontend y las futuras integraciones de agentes.

La documentación detallada, los contratos y las reglas de evolución están en [`ARCHITECTURE.md`](ARCHITECTURE.md).

## Estructura del repositorio

```text
forgemind-intuition/
├── forgemind/                 # paquete Python público
│   ├── core.py                # representación algebraica y ejecución
│   ├── active.py              # selección de probes y falsación activa
│   ├── bayesian.py            # posterior, log_weight y eliminación
│   ├── vectorized.py          # arrays NumPy opcionales
│   ├── knowledge.py           # memoria experimental
│   ├── intuition.py           # puntuación explicable
│   ├── adaptive.py            # calibración adaptativa
│   ├── advisor.py             # recomendaciones para agentes
│   ├── project.py             # formato de proyecto JSON
│   └── cli.py                 # comandos instalables
├── tests/                     # regresión y contratos
├── benchmarks/                # protocolos y resultados reproducibles
├── frontend/                  # copia versionable de la interfaz visual
├── presentation/              # presentación arquitectónica
├── ARCHITECTURE.md            # diseño de tres capas
├── ROADMAP.md                 # fases y prioridades
├── todo.md                    # tablero operativo
├── pyproject.toml             # instalación y entry point
└── .gitignore                 # secretos y artefactos locales
```

## Contrato para agentes de código

Un agente puede utilizar ForgeMind para mantener alternativas sin convertir su propia confianza en verdad. El flujo recomendado es registrar candidatas, pedir una recomendación, diseñar un probe, ejecutar el oráculo, registrar la evidencia y volver a actualizar el conjunto.

```python
from forgemind import advise

recommendation = advise(
    candidates=[candidate_a, candidate_b],
    evidence=observations,
)
print(recommendation.next_hypothesis)
print(recommendation.reason)
```

La interfaz de asesoramiento recomienda qué probar primero. No ejecuta cambios destructivos por sí sola, no inventa resultados y no sustituye una prueba del proyecto anfitrión.

## Benchmarks y pruebas

Ejecuta toda la suite con:

```bash
python -m pytest -q
```

Los benchmarks importantes son:

```bash
python benchmarks/bayesian_latency.py --hypotheses 10000 --repeats 5 --top-k 20
python benchmarks/vectorized_vs_object.py --hypotheses 10000 --repeats 3 --top-k 20
```

Los invariantes mínimos son masa posterior aproximadamente igual a uno, rechazo de evidencia duplicada, falsación dura irreversible salvo restauración explícita, ranking determinista bajo entradas iguales y explicación recuperable para cada eliminación.

## Frontend

La carpeta `frontend/` contiene una copia versionable de la interfaz neo-editorial de laboratorio: hipótesis, evidencia, puntuaciones y siguiente experimento. La versión gestionada por Manus se desarrolla en el proyecto web full-stack separado y usa React, Vite, tRPC, Drizzle y almacenamiento de objetos. La sincronización entre ambos árboles se documentará antes de convertir el backend en parte del repositorio distribuible.

No se deben guardar imágenes grandes, credenciales ni bytes de archivos en Git. Para almacenamiento de archivos, la futura capa full-stack debe guardar los bytes en almacenamiento de objetos y únicamente conservar en base de datos la clave, URL, tipo MIME, tamaño, propietario y proyecto asociado.

## Seguridad y límites

No guardes tokens en `.env` versionados, README, issues, URLs ni mensajes. El `.gitignore` ya excluye `.env` y sus variantes. Si una credencial se expone, debe revocarse y sustituirse.

ForgeMind es un sistema experimental. Sus scores y posteriors son señales de decisión, no demostraciones matemáticas de corrección. La evidencia de un oráculo, las reglas de equivalencia y los límites de cada benchmark deben permanecer visibles.

## Contribuir

Antes de abrir un cambio, ejecuta la suite de pruebas y el benchmark relevante. Conserva compatibilidad con la API pública, añade pruebas para nuevos contratos y actualiza `ARCHITECTURE.md`, `ROADMAP.md` o `todo.md` cuando cambie la responsabilidad de una capa.

Los cambios que introducen aproximaciones deben documentar el modo de exactitud y cómo se estima el error. Los cambios que afectan la representación algebraica deben incluir casos de equivalencia y contraejemplos.

## Licencia

El proyecto declara licencia MIT en `pyproject.toml`. Revisa la licencia antes de redistribuir componentes externos o datos de benchmarks.
