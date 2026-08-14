# ForgeMind

## Active Program Synthesis through Experimental Falsification

> **A computational engine for discovering compact programs by generating hypotheses, designing discriminative experiments, and actively searching for counterexamples.**

ForgeMind is an experimental research system for **computational discovery, program synthesis, and hypothesis falsification**.

Its central question is:

> **Can a system discover compact programs more efficiently by actively searching for informative counterexamples rather than relying only on passive examples?**

Instead of treating program synthesis as a pure search problem, ForgeMind treats it as an **experimental cycle**:

```text
┌──────────────────────┐
│ Hypothesis Generator │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Candidate Programs   │
│ H₁ H₂ H₃ ... Hₙ     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────────┐
│ Discriminative Experiment│
│          x*              │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────┐
│ Oracle / Target      │
│ evaluation           │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Falsification        │
│ eliminate Hᵢ         │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Survivor Population  │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Mutation / Composition│
└──────────────────────┘
           │
           └──────────────► next experiment

The goal is not merely to find a program that fits the available examples.

The goal is to find a compact hypothesis that survives attempts to falsify it.


---

1. Research hypothesis

Let the current hypothesis population be:

\[
\mathcal{H} =
\{H_1,H_2,\ldots,H_n\}
\]

Each hypothesis represents a candidate program.

For an input (x):

\[
H_i(x) \rightarrow y_i
\]

ForgeMind searches for an input (x^*) that maximizes disagreement between surviving hypotheses:

\[
x^* =
\arg\max_x
\operatorname{Disagreement}
\left(
H_1(x),\ldots,H_n(x)
\right)
\]

The oracle then provides the actual result:

\[
y^* = H_{\text{target}}(x^*)
\]

Any hypothesis satisfying:

\[
H_i(x^*) \neq y^*
\]

is falsified and removed from the population.

This creates an active loop:

\[
\boxed{
\text{Generate}
\rightarrow
\text{Predict}
\rightarrow
\text{Discriminate}
\rightarrow
\text{Test}
\rightarrow
\text{Falsify}
\rightarrow
\text{Select}
\rightarrow
\text{Compose}
}
\]


---

2. Why falsification?

A conventional synthesis system often asks:

> Which program explains the examples?



ForgeMind asks an additional question:

> Which experiment would most effectively prove the current hypotheses wrong?



This distinction matters.

A program that fits 100 observed examples may still be completely wrong.

A carefully selected counterexample can eliminate an entire class of competing programs in a single evaluation.

Therefore ForgeMind treats information gained by falsification as a first-class experimental quantity.


---

3. Active vs passive search

ForgeMind contains an explicit passive baseline.

Passive strategy

Inputs are selected without considering the current hypothesis population:

\[
x \sim \text{RandomGenerator}
\]

Active strategy

Inputs are selected according to the disagreement structure of the current population:

\[
x^* =
\arg\max_x H(Predictions(H,x))
\]

where (H(\cdot)) denotes the Shannon entropy of the prediction partition.

The experimental comparison is therefore:

PASSIVE

hypotheses
    │
    ▼
random input
    │
    ▼
oracle
    │
    ▼
elimination


ACTIVE

hypotheses
    │
    ▼
prediction partition
    │
    ▼
information gain
    │
    ▼
discriminative input
    │
    ▼
oracle
    │
    ▼
elimination

The principal research metric is:

\[
Efficiency =
\frac{\text{hypotheses eliminated}}
{\text{oracle queries}}
\]


---

4. Current experimental results

The current benchmark infrastructure compares active falsification against passive random testing.

A recent baseline produced:

active mean eliminations     = 61.125
passive mean eliminations    = 61.125

active mean survivors        = 2.875
passive mean survivors       = 2.875

active elimination/query     = 5.0102
passive elimination/query    = 4.2102

active/passive efficiency    = 1.190x

This corresponds to an observed:

\[
\boxed{1.19\times}
\]

active/passive efficiency ratio under the current benchmark configuration.

Additional information-selection experiments produced approximately:

target 0   ratio = 1.03x
target 1   ratio = 1.03x
target 2   ratio = 1.04x
target 3   ratio = 1.02x
target 4   ratio = 1.04x
target 5   ratio = 1.02x
target 6   ratio = 1.03x
target 7   ratio = 1.03x
target 8   ratio = 1.03x
target 9   ratio = 1.03x

These results are experimental observations, not a final scientific conclusion.

ForgeMind is explicitly designed so that the central hypothesis can fail.


---

5. Adversarial evaluation

ForgeMind also includes an adversarial benchmark designed to test whether apparently successful programs survive stronger evaluation.

Current baseline:

FORGEMIND 0.9.1 ADVERSARIAL

cases                = 40

random mean          = 1.0
adversarial mean     = 1.0
equivalence gap      = 0.0

perfect random       = 40 / 40
perfect adversarial  = 40 / 40

discovery found      = 0 / 160000
discovery rate       = 0.0

The discovery found = 0 result is particularly important.

ForgeMind does not assume that a benchmark will demonstrate an advantage.

A failed discovery experiment is useful because it identifies a limitation in the current hypothesis-generation/search regime.


---

6. Core representation

Programs are represented compositionally.

A program is a sequence of nodes:

[
    Node("U", "rev"),
    Node("U", "sort"),
]

A node represents an operation in the program language.

The system maintains canonical representations of programs:

Program
   │
   ▼
Canonical representation
   │
   ├── equivalence detection
   ├── duplicate removal
   ├── population management
   └── complexity comparison

This makes the representation suitable for:

mutation

composition

deduplication

equivalence testing

parsimony

evolutionary search

hypothesis tracking



---

7. Parsimony

ForgeMind does not optimize correctness alone.

A candidate should also remain compact.

Conceptually:

\[
Score(H)
=
-\lambda_E E(H,D)
-\lambda_C Complexity(H)
+\lambda_R Robustness(H)
\]

where:

(E(H,D)) is empirical error

(Complexity(H)) measures program complexity

(Robustness(H)) measures survival under adversarial testing


This introduces a minimum-description-length-style pressure:

> Prefer the simplest hypothesis that continues to survive falsification.



This is essential because unrestricted program synthesis can easily produce hypotheses that memorize observations rather than discover structure.


---

8. Architecture

The repository is intentionally divided into experimental and core components.

ForgeMind/
│
├── forgemind/
│   ├── core.py
│   └── active.py
│
├── tests/
│   ├── test_core.py
│   └── test_active.py
│
├── benchmarks/
│   ├── active_vs_passive.py
│   ├── active_vs_passive/
│   │   └── results.json
│   │
│   ├── discovery/
│   │   ├── active_vs_passive_v2.py
│   │   └── results.json
│   │
│   └── adversarial/
│       ├── arena.py
│       └── results.json
│
└── backups/
    └── 0.9.1-active-baseline/

forgemind/core.py

Core program representation and execution machinery.

Responsible for concepts such as:

Node

Hyp

canonicalization

execution

mutation

generation

complexity

target programs


forgemind/active.py

Experimental active-falsification layer.

Provides:

hypothesis partitioning

prediction signatures

information gain

informative experiment selection

active falsification

passive baseline

distractor generation


benchmarks/

Reproducible experimental protocols.

The benchmark layer is intentionally separated from the core synthesis engine so that experimental methodology can evolve without contaminating the basic program representation.


---

9. Active falsification engine

The central API includes:

partition_hypotheses(...)

Partitions hypotheses according to their predictions.

information_gain(...)

Computes Shannon entropy over prediction partitions.

select_experiment(...)

Searches candidate inputs for the most informative experiment.

falsify_once(...)

Evaluates the oracle and eliminates inconsistent hypotheses.

build_distractors(...)

Constructs competing hypotheses without inserting the target itself.

run_active_protocol(...)

Runs the active experimental protocol.

run_passive_protocol(...)

Provides the passive baseline.

The compatibility API also exposes:

select_informative_probe(...)

for explicit candidate-set experiments.


---

10. Experimental protocol

A typical active experiment follows:

pool = build_distractors(
    target,
    seed=123,
    count=64,
)

x, gain = select_experiment(
    pool,
    rng,
    budget=32,
)

y, eliminated = falsify_once(
    pool,
    target,
    x,
)

The process repeats until:

the hypothesis population converges,

the query budget is exhausted,

or the experimental protocol terminates.



---

11. Reproducibility

Experiments use explicit random seeds.

For example:

SEEDS = (3, 11, 29, 47)

Benchmark parameters are recorded alongside results.

This allows experiments to be rerun and compared without changing the underlying methodology.


---

12. Testing

ForgeMind currently includes a unit/integration test suite covering:

program representation

canonicalization

execution

mutation

active hypothesis partitioning

information gain

deterministic probe selection

distractor generation

active protocol reproducibility

passive protocol execution


Current validation:

28 passed

Run the complete suite:

cd ~/ForgeMind
python -m pytest -q

Expected:

28 passed


---

13. Running the benchmarks

Active vs passive

cd ~/ForgeMind

PYTHONPATH=. python -m benchmarks.active_vs_passive

Results are written to:

benchmarks/active_vs_passive/results.json

Validate the JSON:

python -m json.tool \
    benchmarks/active_vs_passive/results.json \
    >/dev/null \
    && echo "OK: JSON válido"


---

Adversarial benchmark

cd ~/ForgeMind

PYTHONPATH=. python benchmarks/adversarial/arena.py

Results:

benchmarks/adversarial/results.json

Validate:

python -m json.tool \
    benchmarks/adversarial/results.json \
    >/dev/null \
    && echo "OK: adversarial JSON válido"


---

Discovery benchmark

The discovery benchmark is an experimental research layer and is being developed separately from the stable active/passive protocol.

cd ~/ForgeMind

PYTHONPATH=. python \
    -m benchmarks.discovery.active_vs_passive_v2

Results:

benchmarks/discovery/results.json


---

14. Research questions

ForgeMind is organized around several increasingly difficult questions.

RQ1 — Active falsification

Can informative counterexample selection eliminate competing hypotheses more efficiently than passive random testing?

\[
Efficiency_{active}
>
Efficiency_{passive}
\;?
\]

RQ2 — Generalization

Does active falsification reduce overfitting?

RQ3 — Compression

Does the pressure of falsification produce smaller programs?

RQ4 — Discovery

Can the system discover the target program rather than merely identify it among a supplied population?

RQ5 — Composition

Can surviving partial programs be recombined into progressively better abstractions?

RQ6 — Scaling

Does the advantage of active experimentation increase with the size of the hypothesis space?


---

15. The important distinction

ForgeMind is not intended to be described simply as:

> "an evolutionary program generator."



That would miss the central idea.

The intended abstraction is:

DISCOVERY
                     │
                     ▼
              hypothesis space
                     │
                     ▼
             competing models
                     │
                     ▼
        ┌────────────────────────┐
        │ ACTIVE EXPERIMENT DESIGN│
        └────────────┬───────────┘
                     │
                     ▼
                counterexample
                     │
                     ▼
                falsification
                     │
                     ▼
              surviving models
                     │
                     ▼
             abstraction/composition
                     │
                     └──────────────►

The system therefore sits at the intersection of:

program synthesis

inductive programming

evolutionary computation

active learning

experimental design

automated reasoning

falsification

minimum-description-length principles



---

16. Scientific philosophy

ForgeMind follows a simple principle:

> Do not ask only whether a hypothesis works. Ask where it can fail.



A successful prediction increases confidence.

A decisive counterexample can eliminate a hypothesis.

Therefore the most valuable experiment is often not the one that confirms the current model, but the one that best separates the surviving alternatives.

This gives the system an explicitly experimental character.


---

17. What ForgeMind is trying to discover

The long-term objective is not merely to reproduce known programs.

It is to investigate whether a machine can discover compact computational structure through an autonomous loop of:

Generate
   ↓
Predict
   ↓
Experiment
   ↓
Observe
   ↓
Falsify
   ↓
Compress
   ↓
Compose
   ↓
Repeat

In the strongest formulation:

\[
\boxed{
\text{Discovery}
=
\text{Hypothesis generation}
+
\text{active falsification}
+
\text{compression}
+
\text{composition}
}
\]


---

18. Status

Development status: Experimental / Research Prototype

Current capabilities:

[x] Compositional program representation

[x] Program execution

[x] Canonicalization

[x] Mutation

[x] Hypothesis populations

[x] Distractor generation

[x] Active hypothesis partitioning

[x] Information-gain scoring

[x] Active experiment selection

[x] Counterexample-based falsification

[x] Passive baseline

[x] Active vs passive benchmark

[x] Adversarial benchmark

[x] Automated tests

[x] Reproducible seeds

[ ] Robust discovery benchmark

[ ] Large-scale search

[ ] Formal equivalence engine

[ ] Learned experiment proposal

[ ] Multi-stage program composition

[ ] Statistical evaluation across larger task suites


The project should therefore be regarded as an experimental research platform, not as a finished automated discovery system.


---

19. Roadmap

Phase I — Experimental foundation

stabilize program representation

stabilize active falsification

establish reproducible benchmarks

measure oracle efficiency


Phase II — Discovery

improve hypothesis generation

introduce structured search

separate candidate programs from hypothesis metadata

implement robust discovery protocols

measure discovery rate


Phase III — Composition

combine surviving programs

discover reusable primitives

construct hierarchical programs

introduce abstraction


Phase IV — Adaptive experimentation

learned probe generation

uncertainty-aware experiment selection

adversarial search against hypotheses

adaptive query budgets


Phase V — Scientific evaluation

Compare against:

random search

passive program synthesis

genetic programming

enumeration

active learning baselines

synthesis systems using fixed example sets


Primary metrics:

\[
\text{Discovery Rate}
\]

\[
\text{Queries to Discovery}
\]

\[
\text{Eliminations / Query}
\]

\[
\text{Program Complexity}
\]

\[
\text{Generalization Accuracy}
\]

\[
\text{Robustness}
\]

\[
\text{Compute Cost}
\]


---

20. Repository

GitHub

https://github.com/mechmind-dwv/ForgeMind

Current experimental branch:

feat/adversarial-arena

Latest published milestone:

0750be2
feat: add active falsification and discovery benchmarks


---

21. License

See the repository license for the current licensing terms.


---

22. Citation

ForgeMind is an experimental research project.

If you use the system, benchmark methodology, or experimental results in research, please cite the repository and the corresponding version/commit so that experiments remain reproducible.


---

ForgeMind

> Generate hypotheses. Design experiments. Find counterexamples. Kill bad programs. Keep what survives.



### Lo que cambiaría respecto al README anterior

Este README posiciona ForgeMind correctamente como **infraestructura experimental de investigación**, y no como un simple framework de generación de código.

Además, deja explícita una distinción científica importante: el resultado de `1.19x` es un **resultado preliminar del protocolo actual**, no una afirmación de que el método activo ya haya demostrado superioridad general.

Y mantendría separado `discovery` del benchmark `active_vs_passive`: ahora mismo es la parte que todavía está evolucionando y no conviene presentar como si estuviera completamente validada.

Si quieres aplicarlo directamente desde Termux:

```bash
cd ~/ForgeMind

cat > README.md <<'EOF'
# ForgeMind

## Active Program Synthesis through Experimental Falsification

> **A computational engine for discovering compact programs by generating hypotheses, designing discriminative experiments, and actively searching for counterexamples.**

ForgeMind is an experimental research system for **computational discovery, program synthesis, and hypothesis falsification**.

Its central question is:

> **Can a system discover compact programs more efficiently by actively searching for informative counterexamples rather than relying only on passive examples?**

Instead of treating program synthesis as a pure search problem, ForgeMind treats it as an **experimental cycle**:

```text
Generate → Predict → Discriminate → Test → Falsify → Select → Compose

The objective is not merely to find a program that fits known examples.

It is to find a compact hypothesis that survives attempts to falsify it.


---

Research hypothesis

Let the current hypothesis population be:

\[
\mathcal{H} = \{H_1,H_2,\ldots,H_n\}
\]

Each hypothesis represents a candidate program.

For an input (x):

\[
H_i(x) \rightarrow y_i
\]

ForgeMind searches for an input (x^*) that maximizes disagreement between surviving hypotheses:

\[
x^* =
\arg\max_x
\operatorname{Disagreement}
(H_1(x),\ldots,H_n(x))
\]

The oracle provides the actual result (y^*).

Any hypothesis satisfying:

\[
H_i(x^*) \neq y^*
\]

is falsified and removed.

The central loop is:

\[
\boxed{
\text{Generate}
\rightarrow
\text{Predict}
\rightarrow
\text{Experiment}
\rightarrow
\text{Falsify}
\rightarrow
\text{Select}
\rightarrow
\text{Compose}
}
\]


---

Active vs passive search

ForgeMind explicitly compares two strategies.

Passive

Inputs are selected randomly.

\[
x \sim \text{RandomGenerator}
\]

Active

Inputs are selected according to disagreement between current hypotheses.

\[
x^* =
\arg\max_x H(Predictions(H,x))
\]

where (H) is the Shannon entropy of the prediction partition.

The principal metric is:

\[
Efficiency =
\frac{\text{hypotheses eliminated}}
{\text{oracle queries}}
\]


---

Current experimental results

A current active/passive baseline produced:

active mean eliminations     = 61.125
passive mean eliminations    = 61.125

active mean survivors        = 2.875
passive mean survivors       = 2.875

active elimination/query     = 5.0102
passive elimination/query    = 4.2102

active/passive efficiency    = 1.190x

This corresponds to an observed:

\[
\boxed{1.19\times}
\]

active/passive efficiency ratio under the current benchmark configuration.

Information-selection experiments produced approximately:

target 0   ratio = 1.03x
target 1   ratio = 1.03x
target 2   ratio = 1.04x
target 3   ratio = 1.02x
target 4   ratio = 1.04x
target 5   ratio = 1.02x
target 6   ratio = 1.03x
target 7   ratio = 1.03x
target 8   ratio = 1.03x
target 9   ratio = 1.03x

These are experimental observations, not a final scientific conclusion.


---

Adversarial evaluation

Current adversarial baseline:

cases                = 40
random mean          = 1.0
adversarial mean     = 1.0
equivalence gap      = 0.0

perfect random       = 40 / 40
perfect adversarial  = 40 / 40

discovery found      = 0 / 160000
discovery rate       = 0.0

The system is intentionally designed so that experiments can falsify its own claims.


---

Architecture

ForgeMind/
├── forgemind/
│   ├── core.py
│   └── active.py
│
├── tests/
│   ├── test_core.py
│   └── test_active.py
│
├── benchmarks/
│   ├── active_vs_passive.py
│   ├── active_vs_passive/
│   │   └── results.json
│   ├── discovery/
│   │   ├── active_vs_passive_v2.py
│   │   └── results.json
│   └── adversarial/
│       ├── arena.py
│       └── results.json
│
└── backups/
    └── 0.9.1-active-baseline/

Core

forgemind/core.py contains:

program representation

Node

Hyp

execution

canonicalization

mutation

generation

complexity

target programs


Active engine

forgemind/active.py contains:

hypothesis partitioning

prediction signatures

information gain

informative experiment selection

falsification

passive baseline

distractor generation



---

Active falsification API

partition_hypotheses(...)
information_gain(...)
select_experiment(...)
select_informative_probe(...)
falsify_once(...)
build_distractors(...)
run_active_protocol(...)
run_passive_protocol(...)


---

Parsimony

ForgeMind optimizes more than empirical correctness.

Conceptually:

\[
Score(H)
=
-\lambda_E E(H,D)
-\lambda_C Complexity(H)
+\lambda_R Robustness(H)
\]

This creates pressure toward compact hypotheses that continue to survive adversarial evaluation.


---

Testing

Current test suite:

28 passed

Run:

cd ~/ForgeMind
python -m pytest -q


---

Benchmarks

Active vs passive

PYTHONPATH=. python -m benchmarks.active_vs_passive

Results:

benchmarks/active_vs_passive/results.json

Adversarial

PYTHONPATH=. python benchmarks/adversarial/arena.py

Results:

benchmarks/adversarial/results.json

Discovery

PYTHONPATH=. python -m benchmarks.discovery.active_vs_passive_v2

Results:

benchmarks/discovery/results.json

The discovery benchmark remains an experimental development area.


---

Research questions

RQ1 — Active falsification

Can informative counterexample selection eliminate competing hypotheses more efficiently than passive random testing?

RQ2 — Generalization

Does active falsification reduce overfitting?

RQ3 — Compression

Does falsification pressure produce smaller programs?

RQ4 — Discovery

Can the system discover a target program rather than identify it among supplied candidates?

RQ5 — Composition

Can surviving programs be recombined into progressively better abstractions?

RQ6 — Scaling

Does active experimentation become more valuable as the hypothesis space grows?


---

Scientific position

ForgeMind should not be described simply as an evolutionary program generator.

Its central abstraction is:

hypothesis space
       ↓
competing models
       ↓
active experiment design
       ↓
counterexample
       ↓
falsification
       ↓
surviving models
       ↓
compression / composition
       ↓
next experiment

The project sits at the intersection of:

program synthesis

inductive programming

evolutionary computation

active learning

experimental design

automated reasoning

falsification

minimum-description-length principles



---

Status

Experimental / Research Prototype

Implemented:

[x] Compositional program representation

[x] Program execution

[x] Canonicalization

[x] Mutation

[x] Hypothesis populations

[x] Distractor generation

[x] Active hypothesis partitioning

[x] Information-gain scoring

[x] Active experiment selection

[x] Counterexample-based falsification

[x] Passive baseline

[x] Active vs passive benchmark

[x] Adversarial benchmark

[x] Automated tests

[x] Reproducible seeds

[ ] Robust discovery benchmark

[ ] Large-scale search

[ ] Formal equivalence engine

[ ] Learned experiment proposal

[ ] Multi-stage program composition



---

Roadmap

Phase I — Experimental foundation

stabilize program representation

stabilize active falsification

establish reproducible benchmarks

measure oracle efficiency


Phase II — Discovery

improve hypothesis generation

introduce structured search

separate candidate programs from hypothesis metadata

implement robust discovery protocols

measure discovery rate


Phase III — Composition

combine surviving programs

discover reusable primitives

construct hierarchical programs

introduce abstraction


Phase IV — Adaptive experimentation

learned probe generation

uncertainty-aware experiment selection

adversarial search against hypotheses

adaptive query budgets


Phase V — Scientific evaluation

Compare against:

random search

passive program synthesis

genetic programming

enumeration

active-learning baselines


Primary metrics:

\[
Discovery\ Rate
\]

\[
Queries\ to\ Discovery
\]

\[
Eliminations / Query
\]

\[
Program\ Complexity
\]

\[
Generalization
\]

\[
Robustness
\]

\[
Compute\ Cost
\]


---

Repository

GitHub:

https://github.com/mechmind-dwv/ForgeMind

Current experimental branch:

feat/adversarial-arena

Latest published milestone:

0750be2
feat: add active falsification and discovery benchmarks


---

License

See the repository license for current licensing terms.


---

Citation

ForgeMind is an experimental research project.

For reproducible research, cite the repository together with the relevant version or commit.


---

ForgeMind

> Generate hypotheses. Design experiments. Find counterexamples. Kill bad programs. Keep what survives.
