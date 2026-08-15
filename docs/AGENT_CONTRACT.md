# Contrato de herramientas para agentes

La versión actual del contrato es `1.0` y se implementa en `forgemind.agent_contract`. El contrato es deliberadamente agnóstico del transporte: puede exponerse por HTTP, MCP, CLI o tRPC sin cambiar sus envelopes.

Las operaciones permitidas son `register_hypothesis`, `top_k`, `propose_probe`, `record_evidence`, `explain`, `park`, `unpark` y `restore_snapshot`. Cada request contiene `contract_version`, `operation`, `project_id`, `payload` y opcionalmente `request_id`. Cada response contiene `contract_version`, `operation`, `ok`, `data`, `error` y `request_id`.

> El contrato describe una acción recomendada o una mutación explícita; no declara que una hipótesis sea verdadera.

Las operaciones que modifican estado deben ser idempotentes o rechazar duplicados mediante un identificador de evidencia/request. `execute_arbitrary_code` no es una operación válida del contrato. La ejecución de programas y oráculos requiere un adaptador aislado con límites de tiempo, memoria, procesos y registro de auditoría; definir ese adaptador es una tarea separada y pendiente.

| Operación | Propósito | Mutación |
|---|---|---|
| `register_hypothesis` | Incorporar una candidata con descripción y prior | Sí |
| `top_k` | Consultar ranking y estados | No |
| `propose_probe` | Pedir la siguiente evidencia discriminativa | No |
| `record_evidence` | Aportar evidencia identificada y su procedencia | Sí |
| `explain` | Recuperar posterior, razón y trazabilidad | No |
| `park` | Aparcar una candidata de forma reversible | Sí |
| `unpark` | Reactivar una candidata aparcada | Sí |
| `restore_snapshot` | Reanudar un ciclo desde un snapshot validado | Sí |

Las pruebas en `tests/test_agent_contract.py` verifican versionado, operaciones permitidas y consistencia entre respuestas exitosas y fallidas. La implementación del dispatcher, la autorización por proyecto, los snapshots persistentes y el aislamiento de ejecución quedan fuera de este contrato de datos y siguen pendientes.
