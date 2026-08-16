# Modelo de rendimiento del pipeline de ForgeMind

Las referencias sobre `DataLoader` y utilización de GPU aportan una regla transferible al motor de intuición: no se debe atribuir una latencia al cálculo bayesiano sin separar primero la preparación de datos, la selección de posiciones, la actualización numérica y la escritura de explicaciones.

## Correspondencia con ForgeMind

| Fase del pipeline | Equivalente en ForgeMind | Señal principal |
|---|---|---|
| Lectura / ingestión | Conversión y validación de likelihoods o mapas de evidencia | `ingest_ms` |
| Espera / selección | Selección de familias y posiciones afectadas | `positions_selected` |
| Cómputo | Actualización logarítmica, normalización y poda | `numeric_update_ms` |
| Metadata / trazabilidad | Registro de `evidence_id` y razones explicativas | `metadata_ms` |
| Rendimiento efectivo | Hipótesis actualizadas por milisegundo y coste total | `total_ms`, `positions_updated` |

La nueva instantánea `VectorizedHypothesisStore.performance_snapshot()` expone estas magnitudes para la última observación sin exponer arrays internos mutables. El camino `observe_arrays()` conserva su semántica exacta, mantiene la normalización posterior y sigue siendo compatible con el almacenamiento array-native sin diccionarios de identificadores.

## Interpretación operativa

Si `ingest_ms` domina, conviene reducir conversiones, copias y materialización de diccionarios. Si `numeric_update_ms` domina, la investigación debe centrarse en actualización dispersa, normalización y poda. Si `metadata_ms` domina, las razones deben permanecer fuera del hot path y escribirse solo para posiciones activas. Si el número de posiciones seleccionadas es mucho mayor que el número de posiciones actualizadas, existe una oportunidad para mejorar índices invertidos o selección de familias.

Estas métricas no representan utilización de GPU: el motor actual es NumPy/CPU y el modo exacto auditable debe conservar una ruta independiente. La analogía con GPU se utiliza para localizar esperas y transferencias conceptuales, no para justificar una aceleración no medida.

## Próxima evolución

La siguiente fase debe evaluar batching, prefetch y paralelismo por lotes sobre evidencia real. Cada alternativa deberá compararse con el resultado secuencial exacto mediante posteriores, top-k, estados y trazabilidad. No se considerará una optimización válida si reduce la latencia a costa de perder explicaciones o cambiar decisiones de eliminación.
