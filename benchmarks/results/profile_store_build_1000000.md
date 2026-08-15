# Profiling de construcción del store — 1.000.000 de hipótesis

## Conclusión ejecutiva

El coste adicional no procede principalmente de los arrays NumPy. La construcción conserva simultáneamente varias representaciones Python del mismo universo: la entrada `hypotheses`, el tuple `ids`, el índice `index`, `descriptions`, `family_by_id`, los diccionarios de `priors` y las claves/valores temporales usados para convertir esos mapas a arrays. La ruta actual necesita esa compatibilidad orientada a IDs, pero duplica memoria cuando el consumidor ya dispone de posiciones y arrays.

> El siguiente cuello de botella prioritario es el constructor array-native: permitir crear el store desde arrays numéricos y, opcionalmente, desde una secuencia compacta de IDs/descripciones, sin exigir simultáneamente diccionarios completos de hipótesis, priors y familias.

## Métricas observadas

| Etapa | RSS observado | Asignaciones Python incrementales relevantes |
|---|---:|---:|
| Proceso base | `32.89 MiB` | Referencia |
| Lista de IDs de entrada | incremento principal de strings `H0...H999999` | `~62.8 MB` trazables en la etapa de IDs |
| Diccionario de descripciones | No aislado en la salida RSS por etapa | Diccionario de un millón de entradas; las claves reutilizan los strings de IDs |
| Diccionario de priors y array fuente | `804.04 MiB` | `62.76 MB` trazables; `54.76 MB` en la comprensión del diccionario de priors y `8.00 MB` en el array fuente |
| Constructor completado | `1365.21 MiB` bajo tracemalloc | `165.27 MB` incrementales; `58.75 MB` en `index`, `30.76 MB` en `descriptions`, `30.76 MB` en `family_by_id` |
| Inventario final | `1617.89 MiB` bajo tracemalloc | `315.14 MB` trazables; el RSS incluye sobrecarga de tracemalloc y buffers nativos |

La ejecución normal sin tracemalloc registró aproximadamente `462.10 MiB` de RSS máximo para 1.000.000 de hipótesis. El perfil con tracemalloc no debe compararse directamente como consumo de producción porque el propio profiler añade overhead y retiene trazas; sirve para atribuir asignaciones Python, no para estimar el RSS operativo final.

## Hotspots atribuidos al código

| Línea | Estructura | Asignación trazable aproximada | Diagnóstico |
|---|---|---:|---|
| `vectorized.py:46` | `self.index = {id: position}` | `58.75 MB` | Índice Python de un millón de entradas; necesario para APIs por ID, pero evitable en la ruta posicional. |
| `vectorized.py:47` | `self.descriptions = dict(hypotheses)` | `30.76 MB` | Copia explícita del diccionario de descripciones; duplica la estructura de entrada. |
| `vectorized.py:48` | `self.family_by_id = {...}` | `30.76 MB` | Mapa Python por hipótesis incluso cuando todas pertenecen a `default`; debe sustituirse por labels numéricos o un fast path de familia única. |
| `vectorized.py:45` | `self.ids = tuple(hypotheses)` | `~8.00 MB` más referencias | Segunda estructura de IDs; puede recibirse directamente como `tuple[str, ...]` en el constructor array-native. |
| `vectorized.py:55` | `family_positions` | `~8.00 MB` | Índice posicional razonable, pero puede compactarse y evitarse para la familia única. |
| `vectorized.py:56`, `62`, `63`, `65` | `raw_priors`, `log_weights`, `posteriors`, `evidence_counts` | `~29 MB` | Estado numérico esperado y relativamente compacto frente al RSS total. |

## Prioridades técnicas

Primero, añadir un constructor array-native que reciba `log_weights` o `priors` ya alineados, `family_labels` opcionales y metadatos lazily materializados. Segundo, representar familias mediante un array entero `family_codes` y un diccionario pequeño `family_name → code`; conservar `family_by_id` solo en un adaptador de compatibilidad. Tercero, permitir que `descriptions` sea opcional o se almacene externamente, ya que el hot path no lo consulta. Finalmente, separar el índice `id → position` de la instancia numérica para consumidores que ya trabajan con posiciones.

## Límites del perfil

`tracemalloc` no contabiliza directamente los buffers nativos de NumPy y aumenta el RSS al conservar trazas. Por ello, el informe debe usarse para localizar asignaciones y no como medición final de producción. La medición de RSS sin profiler permanece en el artefacto de escalabilidad: `~462.10 MiB` de máximo para el store de un millón bajo el protocolo actual.
