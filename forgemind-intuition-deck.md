# ForgeMind Intuition — Arquitectura algebraica y probabilística

## Cover
ForgeMind Intuition
Del álgebra de programas a una intuición experimental
Arquitectura del núcleo 0.16 · Manus AI

## Slide 1
### La intuición es inferencia comprimida

- ForgeMind no trata la intuición como magia: la modela como selección de hipótesis bajo evidencia.
- Memoria estructurada aporta priors; probes y oráculos aportan evidencia; la falsación reduce el espacio.
- El resultado es una recomendación operativa: qué hipótesis probar después.
- Una recomendación no equivale a verdad: expresa valor experimental y grado de creencia.

> Tesis: intuición = memoria + comparación + actualización + eliminación.

## Slide 2
### El álgebra define el espacio de posibilidades

- Una candidata es una secuencia composicional de nodos: `rev → sort → neg → rev`.
- La canonización permite comparar estructuras sin depender del texto superficial.
- Las reglas de reescritura expresan equivalencias reutilizables, como `sort(sort(x)) = sort(x)`.
- La búsqueda algebraica reduce programas a familias semánticas antes de asignar probabilidades.

**Idea clave:** sin una representación algebraica estable, el posterior confunde sinónimos con hipótesis nuevas.

## Slide 3
### Bayes convierte evidencia en cambio de creencia

- Cada hipótesis comienza con un `prior` que representa memoria o contexto previo.
- Una observación registra su fuente y la verosimilitud `P(E|H)`.
- El motor actualiza proporcionalmente: `P(H|E) ∝ P(E|H) · P(H)`.
- La distribución se normaliza: creencias no negativas cuya suma es uno [1] [2].

**Lectura de ForgeMind:** el posterior es una credencia condicionada a evidencia registrada, no una garantía de corrección.

## Slide 4
### La evidencia debe tener procedencia

- `evidence_id` conecta cada actualización con una probe, test, oráculo o regla.
- `description` explica qué observación se incorporó.
- `source` separa evidencia ejecutable, histórica y experta.
- Las razones se conservan junto con el posterior para que un agente pueda justificar su recomendación.

**Contrato mínimo:** hipótesis, prior, likelihood, fuente, descripción y estado.

## Slide 5
### Eliminar no es olvidar: es dejar una traza

- Una hipótesis cruza a `eliminated` si su posterior cae bajo el umbral después del mínimo de evidencia.
- Una falsación dura puede llevarla directamente a probabilidad cero.
- Las alternativas supervivientes se renormalizan para mantener una distribución válida.
- Cada eliminación conserva el porqué: evidencia, umbral y momento de la decisión.

**Estados:** `active` → `survivor` → `eliminated`.

## Slide 6
### La arquitectura separa cuatro responsabilidades

- **Álgebra:** nodos, canonización, reescrituras y equivalencias.
- **Memoria:** hipótesis, reglas, falsificaciones y procedencia.
- **Probabilidad:** priors, likelihoods, posteriors y renormalización.
- **Agencia:** ranking, valor experimental y siguiente experimento.

**Flujo:** candidato → representación → evidencia → actualización → eliminación → recomendación.

## Slide 7
### Ejemplo: dos hipótesis, una probe

- `H1`: `sort` preserva la relación; `H2`: `reverse` preserva la relación.
- Priors iniciales: `P(H1)=0.50`, `P(H2)=0.50`.
- Observación: salida ordenada; `P(E|H1)=0.90`, `P(E|H2)=0.20`.
- Posteriores: `P(H1|E)=0.818`, `P(H2|E)=0.182`.

**Interpretación:** H1 gana credencia, pero todavía necesita pruebas que puedan distinguirla de sus rivales.

## Slide 8
### El agente elige información, no solo puntuación

- El ranking combina posterior, novedad, compresión y valor de falsación.
- Una hipótesis con alta credencia puede ser poco útil si no separa familias rivales.
- Una hipótesis menos probable puede ser prioritaria si su prueba tiene gran valor experimental.
- El frontend debe mostrar la contribución de cada señal, no ocultarla en un número único.

**Regla de decisión:** probar aquello que más reduce la duda por unidad de coste.

## Slide 9
### Guardrails contra una intuición engañosa

- No confundir posterior con probabilidad objetiva de verdad.
- No actualizar dos veces la misma evidencia como si fueran observaciones independientes.
- No eliminar por umbral sin un mínimo de evidencia configurable.
- No convertir una analogía algebraica en equivalencia semántica sin oráculo o prueba.

> ForgeMind organiza incertidumbre; no la maquilla.

## Slide 10
### De módulo probabilístico a software para proyectos

- `BayesianHypothesisSet` ya permite priors, observaciones, falsación dura y snapshots explicables.
- La siguiente integración conecta el motor con proyectos JSON, probes reales y el frontend de ForgeMind.
- La API de agentes puede pedir: “¿qué pruebo primero y qué evidencia cambió la decisión?”
- El objetivo es una memoria experimental compartida entre desarrollador, agente y código.

**Cierre:** una intuición útil es una hipótesis que sabe por qué sigue viva.

## Slide 11
### Referencias

- [1] NIST, *Bayes Solution and Bayesian Statistics 101*: prior, likelihood, posterior y actualización sucesiva. https://www.nist.gov/document/bayesclassday1-1pdf
- [2] Stanford Encyclopedia of Philosophy, *Bayesian Epistemology*: probabilismo, condicionalización, zeroing y rescaling. https://plato.stanford.edu/entries/epistemology-bayesian/
- [3] Mariano et al., ACM POPL/OOPSLA, *Program synthesis with algebraic library specifications*: especificaciones algebraicas como reglas de reescritura para síntesis. https://doi.org/10.1145/3360558
- [4] ForgeMind Intuition 0.16, implementación local: `forgemind/bayesian.py`, `forgemind/knowledge.py`, `forgemind/intuition.py` y `forgemind/advisor.py`.
