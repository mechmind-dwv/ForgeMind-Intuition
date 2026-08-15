# Contribuir a ForgeMind Intuition

Gracias por tu interés en contribuir. ForgeMind es un proyecto experimental, pero sus cambios deben ser reproducibles, revisables y honestos sobre sus límites.

## Antes de empezar

Lee [`README.md`](README.md), [`ARCHITECTURE.md`](ARCHITECTURE.md), [`ROADMAP.md`](ROADMAP.md) y [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md). Comprueba si la propuesta ya aparece en `todo.md` o en una Discussion abierta. Para cambios grandes, abre primero una Discussion describiendo el problema, la capa afectada y el contrato que quieres introducir.

## Preparar el entorno

```bash
git clone https://github.com/mechmind-dwv/ForgeMind-Intuition.git
cd ForgeMind-Intuition
python -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest -q
```

Para trabajar en el almacén vectorizado, instala también el extra:

```bash
python -m pip install -e '.[vectorized]'
```

## Flujo recomendado

Crea una rama con un nombre descriptivo, implementa el cambio en la capa correcta, añade pruebas y actualiza la documentación afectada. Mantén los commits pequeños y explica en el mensaje qué contrato cambia.

```bash
git checkout -b feat/nombre-del-cambio
python -m pytest -q
git diff --check
git add .
git commit -m "feat: describe the change"
git push -u origin feat/nombre-del-cambio
```

## Reglas técnicas

Los cambios algebraicos deben incluir casos de equivalencia y contraejemplos. Los cambios probabilísticos deben conservar la masa posterior, evitar doble aplicación de evidencia y explicar toda eliminación. Las optimizaciones deben incluir un benchmark reproducible y comparar exactitud con una referencia.

NumPy es opcional: el núcleo debe importar y probarse sin el extra vectorizado. No guardes secretos, credenciales, archivos grandes ni datos privados en Git. No presentes datos sintéticos como resultados reales sin etiquetarlos explícitamente.

## Pull requests

Una pull request debe explicar el problema, la solución, la capa modificada, las pruebas ejecutadas, los cambios de rendimiento y los riesgos conocidos. Si cambia una API pública, incluye un ejemplo actualizado. Si cambia el comportamiento probabilístico, describe qué significa el resultado y qué no significa.

Los mantenedores revisarán corrección, trazabilidad, seguridad, claridad de documentación y compatibilidad. Una revisión puede pedir dividir el cambio si mezcla producto, infraestructura y experimento sin un contrato claro.

## Reportar bugs y proponer ideas

Usa la plantilla de issue adecuada. Incluye versión, sistema, comando ejecutado, entrada mínima reproducible, salida observada y salida esperada. Para vulnerabilidades de seguridad, no abras una issue pública: sigue [`SECURITY.md`](SECURITY.md).
