# Integración probabilística y protocolo de benchmarks

## Propósito

ForgeMind representa la intuición como una distribución de creencias sobre hipótesis. `BayesianHypothesisSet` recibe candidatas con pesos previos, aplica observaciones con likelihoods `P(E|H)` en espacio logarítmico y devuelve decisiones explicables. La integración debe conservar simultáneamente el valor numérico del posterior, el estado de la hipótesis y la procedencia de la decisión.

La implementación de referencia es [`forgemind/bayesian.py`](../forgemind/bayesian.py). El store array-native y la implementación exacta por bloques son optimizaciones compatibles que deben compararse contra este contrato cuando el tamaño del escenario lo permita.

## Contrato de entrada

Cada hipótesis necesita un identificador estable y una descripción no vacía. Los priors son pesos finitos y no negativos; debe existir al menos una hipótesis con masa positiva. Una `EvidenceObservation` necesita un `evidence_id` no vacío, una descripción no vacía y un mapa de likelihoods entre `0` y `1`. Los likelihoods ausentes se interpretan como neutrales (`1.0`) para conservar compatibilidad con observaciones dispersas.

Una misma evidencia no puede aplicarse dos veces. La falsación dura se expresa mediante `hard_falsification` y no debe confundirse con una eliminación automática por umbral. Las decisiones devueltas exponen `hypothesis_id`, `posterior`, `threshold`, `state`, `reason_code`, `reason`, `evidence_ids` y `reversible`.

## Invariantes de integración

| Invariante | Criterio de aceptación |
|---|---|
| Normalización | La suma de posteriores es aproximadamente `1.0` mientras exista masa activa. |
| Estabilidad | Los updates se realizan en log-space y no producen `NaN` para entradas válidas. |
| Trazabilidad | Cada hipótesis actualizada conserva el `evidence_id`; las decisiones conservan la secuencia completa. |
| Falsación | Una falsación dura produce `reason_code=hard_falsification`, estado `eliminated` y `reversible=false`. |
| Umbral | Un posterior bajo el umbral se mantiene `uncertain` hasta alcanzar `min_evidence`; después puede ser eliminado. |
| Reversibilidad | `park` oculta una hipótesis sin falsarla; `unpark` la devuelve a `uncertain`. |
| Ranking | `top_k` devuelve únicamente hipótesis elegibles por defecto y respeta el orden descendente del posterior. |
| Idempotencia defensiva | Una evidencia duplicada se rechaza sin modificar el snapshot del motor. |

Las pruebas de integración en [`tests/test_probabilistic_integration.py`](../tests/test_probabilistic_integration.py) ejercitan estos criterios mediante secuencias de evidencias, falsación dura, parking, reactivación y rechazo de duplicados.

## Protocolo estable de benchmark

El ejecutor oficial es [`benchmarks/probabilistic_protocol.py`](../benchmarks/probabilistic_protocol.py). Usa datos deterministas, no depende de semilla aleatoria y emite JSON con `protocol_version`. La comparación se realiza entre `BayesianHypothesisSet` y `VectorizedHypothesisStore` sobre el mismo conjunto de hipótesis, priors y evidencias.

La ejecución recomendada para una regresión local es:

```bash
python benchmarks/probabilistic_protocol.py \
  --hypotheses 10000 \
  --rounds 3 \
  --repeats 3 \
  --top-k 25
```

El protocolo mide cuatro dimensiones. La **latencia** registra la mediana de `observe` por ronda para cada implementación. La **memoria** registra el pico de `tracemalloc` por motor y el RSS máximo del proceso mediante `resource.getrusage`. La **exactitud** registra error máximo y medio absoluto de posteriores, suma final de masa, coincidencia de conjuntos eliminados y solapamiento mínimo de `top_k`. La **trazabilidad** verifica que ambos motores hayan registrado la misma población de hipótesis con evidencia y que el número de razones crezca con cada ronda.

El resultado local de referencia con 10.000 hipótesis, tres rondas y tres repeticiones fue:

| Métrica | Resultado |
|---|---:|
| Error absoluto máximo del posterior | `3.52e-19` |
| Error absoluto medio | `7.11e-22` |
| Suma final exacta/vectorizada | `0.9999999999999997` / `0.9999999999999996` |
| Solapamiento mínimo de `top_k` | `1.0` |
| Coincidencia de eliminaciones | Sí |
| Coincidencia de trazabilidad | Sí |
| Latencia mediana exacta | `373.2157 ms` |
| Latencia mediana vectorizada | `78.2706 ms` |
| RSS máximo observado | `80.93 MiB` |

Estas cifras son una referencia de una máquina concreta, no un SLA. Para cambios de rendimiento, deben compararse con el mismo Python, tamaño, número de rondas y número de repeticiones. Los escenarios de 1M y 10M deben ejecutarse fuera de la suite unitaria normal y guardar su JSON en `benchmarks/results/`.

## Criterios para CI y regresiones

La suite unitaria debe ejecutar las pruebas de integración con el extra vectorizado instalado. Un cambio probabilístico se considera compatible si mantiene las invariantes numéricas y de trazabilidad, no introduce errores en la suite completa y no altera el contrato de los campos de `EliminationDecision`. Las mediciones de tiempo y RSS sirven para detectar regresiones, pero no deben convertir una diferencia entre máquinas en un fallo duro de CI sin un umbral calibrado para el runner.
