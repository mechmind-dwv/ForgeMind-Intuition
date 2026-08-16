# Integración inicial con Obsidian desde Termux

ForgeMind puede exportar snapshots bayesianos a una bóveda Obsidian usando archivos Markdown y JSON locales. El flujo no necesita tokens ni una API de Obsidian: Termux ejecuta ForgeMind y Obsidian abre la carpeta resultante.

## Preparar Termux

Concede a Termux acceso al almacenamiento compartido y crea una carpeta nueva para la bóveda:

```sh
termux-setup-storage
mkdir -p /sdcard/Obsidian/ForgeMind
```

En Obsidian, selecciona **Open folder as vault** y elige `/sdcard/Obsidian/ForgeMind`.

## Estructura generada

Cada exportación crea una estructura como la siguiente:

```text
ForgeMind/
└── Projects/
    └── demo-project/
        ├── README.md
        ├── snapshot.json
        └── hypotheses/
            └── h-alpha.md
```

`README.md` funciona como índice navegable. Cada hipótesis tiene frontmatter, posterior, estado, evidencia relacionada y razones de decisión. `snapshot.json` conserva el objeto completo para restauración o procesamiento posterior.

## Exportar desde Python

Desde la raíz del repositorio:

```sh
python - <<'PY'
from forgemind import BayesianHypothesisSet, EvidenceObservation, export_snapshot

beliefs = BayesianHypothesisSet.from_priors({
    "h-alpha": "La candidata alpha explica el comportamiento observado.",
    "h-beta": "La candidata beta explica el comportamiento observado.",
})
beliefs.observe(EvidenceObservation(
    evidence_id="e-1",
    description="Fixture de validación local",
    likelihoods={"h-alpha": 0.9, "h-beta": 0.2},
    source="termux-fixture",
))

export_snapshot(
    beliefs.snapshot(),
    "/sdcard/Obsidian/ForgeMind",
    project_name="Primer proyecto ForgeMind",
    project_id="primer-proyecto",
)
PY
```

La exportación solo escribe en la ruta indicada. No lee el resto de la bóveda ni incluye variables de entorno, cookies, tokens o secretos.

## Validación

El exportador se cubre con pruebas unitarias en `tests/test_obsidian.py`. Antes de usar una bóveda real, ejecuta:

```sh
python -m pytest tests/test_obsidian.py -q
```

La integración actual es de **exportación local unidireccional**. Una futura iteración puede añadir importación de notas editadas, sincronización Git o un plugin de Obsidian, pero esas funciones no se activan automáticamente para evitar sobrescribir contenido del usuario.

## Copiar el repositorio completo a Termux

El paquete limpio entregado por ForgeMind se puede colocar en la carpeta raíz de Termux. En Termux, primero instala el acceso al almacenamiento compartido de forma interactiva:

```sh
termux-setup-storage
```

Cuando aparezca `Do you want to continue? (y/n)`, escribe únicamente `y` y pulsa Enter. No pegues `mkdir` en ese mismo prompt; por eso el intento anterior se canceló.

Después copia `ForgeMind-Intuition-termux.tar.gz` a la carpeta `~` de Termux y ejecuta:

```sh
cd ~
rm -rf ForgeMind-Intuition
mkdir ForgeMind-Intuition
tar -xzf ForgeMind-Intuition-termux.tar.gz -C ForgeMind-Intuition
cd ~/ForgeMind-Intuition
bash scripts/termux-install.sh
```

Si el archivo llega a `~/storage/downloads`, usa esta variante:

```sh
cd ~
rm -rf ForgeMind-Intuition
mkdir ForgeMind-Intuition
tar -xzf ~/storage/downloads/ForgeMind-Intuition-termux.tar.gz -C ForgeMind-Intuition
cd ~/ForgeMind-Intuition
bash scripts/termux-install.sh
```

El instalador ejecuta `pip install -e '.[vectorized,dev]'`, por lo que corrige los dos errores mostrados: instala NumPy para el almacenamiento vectorizado y pytest para las pruebas.
