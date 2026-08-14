# ForgeMind Intuition 0.16.0

## Entrega

Se creó una copia independiente del repositorio original `mechmind-dwv/ForgeMind` en `/home/ubuntu/ForgeMind-Intuition`. La copia tiene historial Git local separado y está empaquetada como `/home/ubuntu/ForgeMind-Intuition-0.16.0.tar.gz`.

## Implementación

La versión 0.16 añade `KnowledgeBase` para memoria experimental de descubrimientos, equivalencias, falsificaciones y reglas de reescritura; `intuition_score()` para puntuación algorítmica explicable; `AdaptiveIntuitionModel` para calibración con evidencia ponderada, shrinkage y penalización explícita de complejidad; y `advise()` como interfaz para agentes de programación o LLMs que necesiten decidir qué hipótesis falsar primero.

También se incorporó `benchmarks/ranking_metrics.py` con `mean_rank`, `MRR`, `top-k`, `exact_rank`, `best_equivalent_rank` y evaluaciones hasta solución. La métrica equivalente evita penalizar representaciones estructuralmente distintas que producen el mismo comportamiento en los probes observados.

## Validación

La suite completa terminó con **35 pruebas aprobadas**. El benchmark de discovery existente se ejecutó con semillas y objetivos del repositorio. En la configuración actual observó, por ejemplo, 5.47 supervivientes activos frente a 7.70 pasivos con presupuesto 1, y convergencia a 5.47 frente a 5.47 desde presupuesto 4; estos números son observaciones de este benchmark, no una afirmación general de superioridad.

## Limitación de publicación

El intento de crear automáticamente un repositorio privado en GitHub falló porque la cuenta autenticada no tiene permiso `CreateRepository`. El repositorio local sí está completo y limpio. Para publicarlo, basta crear un repositorio vacío con el nombre `ForgeMind-Intuition` y ejecutar `git remote add origin <URL>` seguido de `git push -u origin main` desde la carpeta indicada.

## Siguiente paso

El siguiente hito es conectar `advise()` con `forgemind.active`: generar candidatos, puntuar y ordenar, elegir el experimento, ejecutar el oráculo, registrar el resultado en `KnowledgeBase` y actualizar `AdaptiveIntuitionModel` sin permitir que la intuición sustituya a la falsación.
