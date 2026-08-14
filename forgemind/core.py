
from dataclasses import dataclass
import random, statistics

UNARY=("id","rev","neg","abs","sort","diff")
PARAM=("rot","add","mul","clip")

@dataclass(frozen=True)
class Node:
    kind:str
    name:str
    arg:int|None=None

def apply(n,x):
    x=list(x)
    if n.name=="id": return x
    if n.name=="rev": return x[::-1]
    if n.name=="neg": return [-v for v in x]
    if n.name=="abs": return [abs(v) for v in x]
    if n.name=="sort": return sorted(x)
    if n.name=="diff": return [x[i+1]-x[i] for i in range(len(x)-1)]
    if n.name=="rot":
        k=(n.arg or 1)%len(x) if x else 0; return x[k:]+x[:k]
    if n.name=="add": return [v+(n.arg or 0) for v in x]
    if n.name=="mul": return [v*(n.arg or 1) for v in x]
    if n.name=="clip":
        k=abs(n.arg or 1); return [max(-k,min(k,v)) for v in x]
    raise ValueError(n.name)

def run(p,x):
    y=list(x)
    for n in p: y=apply(n,y)
    return y

def canon(p):
    # Remove identities and adjacent duplicate identities.
    q=[n for n in p if n.name!="id"]
    return tuple((n.kind,n.name,n.arg) for n in q)

def complexity(p):
    return len(p)+sum(.2 for n in p if n.arg is not None)

def rand_node(rng):
    if rng.random()<.55:
        return Node("U",rng.choice(UNARY))
    z=rng.choice(PARAM)
    return Node("P",z,rng.randint(-3,3))

def mutate(p,rng):
    p=list(p)
    r=rng.random()
    if not p or r<.20:
        p.insert(rng.randrange(len(p)+1),rand_node(rng))
    elif r<.32 and len(p)>1:
        p.pop(rng.randrange(len(p)))
    else:
        p[rng.randrange(len(p))]=rand_node(rng)
    return p[:6] or [Node("U","id")]

def crossover(a,b,rng):
    i=rng.randrange(len(a)+1)
    j=rng.randrange(len(b)+1)
    return (a[:i]+b[j:])[:6] or [Node("U","id")]

    i=rng.randrange(len(a)+1); j=rng.randrange(len(b)+1)
    return (a[:i]+b[j:])[:6] or [Node("U","id")]

def xgen(rng):
    return [rng.randint(-30,30) for _ in range(rng.randint(3,9))]

TARGETS=[
 [Node("U","rev")],
 [Node("U","neg")],
 [Node("P","add",2)],
 [Node("P","mul",-1)],
 [Node("U","abs"),Node("P","add",1)],
 [Node("U","neg"),Node("U","rev")],
 [Node("P","rot",2),Node("P","add",-1)],
 [Node("U","diff"),Node("U","neg")],
 [Node("U","sort"),Node("U","rev")],
 [Node("U","rev"),Node("U","neg"),Node("P","add",2)],
]

@dataclass
class Hyp:
    p:list
    support:int=0
    failures:int=0
    evaluations:int=0

    @property
    def evaluated(self):
        return self.evaluations > 0

    @property
    def accuracy(self):
        if self.evaluations == 0:
            return 0.0
        return self.support / self.evaluations

def behavior_distance(a,b):
    """
    Deterministic behavioral distance between two sequence outputs.

    Exact equality is zero.  Length differences are penalized, while
    element-wise differences accumulate absolute error.
    """
    a=list(a)
    b=list(b)

    n=min(len(a),len(b))
    distance=sum(abs(a[i]-b[i]) for i in range(n))

    # Penalize missing/excess elements using their absolute magnitude.
    if len(a) > n:
        distance += sum(abs(v) for v in a[n:])
    if len(b) > n:
        distance += sum(abs(v) for v in b[n:])

    distance += abs(len(a)-len(b))
    return float(distance)


def behavior_distance(a,b):
    if len(a)!=len(b):
        n=min(len(a),len(b))
        distance=sum(abs(x-y) for x,y in zip(a[:n],b[:n]))
        distance+=abs(len(a)-len(b))*10
        return float(distance)
    return float(sum(abs(x-y) for x,y in zip(a,b)))


def disagreement(pool,x):
    sig={tuple(run(h.p,x)) for h in pool}
    return len(sig)

def generator(seed,pop=70):
    rng=random.Random(seed)
    pool=[]

    # Start with a mixture of short programs.  Pure one-node
    # initialization is too weak for targets composed of 2-3 operators.
    for _ in range(pop):
        r=rng.random()

        if r < 0.30:
            length=1
        elif r < 0.72:
            length=2
        elif r < 0.94:
            length=3
        else:
            length=rng.randint(4,5)

        pool.append(Hyp([rand_node(rng) for _ in range(length)]))

    return pool

def falsify(pool,target,rng,budget=18):
    # Choose an input that maximizes hypothesis disagreement, then test it
    # against the true target. Return evidence for each hypothesis.
    candidates=[xgen(rng) for _ in range(budget)]
    x=max(candidates,key=lambda z:disagreement(pool,z))
    y=run(target,x)
    for h in pool:
        if run(h.p,x)==y:
            h.support += 1
        else:
            h.failures += 1

        h.evaluations += 1
    return x,y

def evolve(seed,target,rounds=42,pop=70):
    rng=random.Random(seed)
    pool=generator(seed,pop)
    history=[]

    # Probes deterministas compartidos por toda la evolución.
    probes=[
        [-5,-2,0,3,7],
        [-3,-1,4],
        [0,1,2],
        [1,2,3],
        [5,0,-2,7],
        [9,-4,2,6],
    ]

    target_outputs=[run(target,x) for x in probes]

    def behavioral_score(h):
        distances = []
        exact = 0

        for x, y in zip(probes, target_outputs):
            d = behavior_distance(run(h.p, x), y)
            distances.append(d)
            if d == 0:
                exact += 1

        total_distance = sum(distances)

        return (
            exact,
            -total_distance,
            -h.failures,
            h.support,
            -complexity(h.p),
        )

    for r in range(rounds):
        x,y=falsify(pool,target,rng)

        scored=[]
        for h in pool:
            score = behavioral_score(h)
            scored.append((score, h))

        scored.sort(key=lambda z:z[0],reverse=True)

        # Preserve both quality and structural diversity.
        elite=[]
        seen=set()
        for _,h in scored:
            key=canon(h.p)
            if key not in seen:
                elite.append(h)
                seen.add(key)
            if len(elite)>=16:
                break

        best=elite[0]

        best_score = behavioral_score(best)

        history.append({
            "round": r,
            "support": best.support,
            "failures": best.failures,
            "evaluations": best.evaluations,
            "behavior_exact": best_score[0],
            "behavior_distance": -best_score[1],
            "program": canon(best.p),
            "complexity": complexity(best.p),
            "pool_disagreement": disagreement(pool, x),
        })

        new=[
            Hyp(list(h.p),h.support,h.failures,h.evaluations)
            for h in elite
        ]

        while len(new)<pop:
            a=rng.choice(elite)

            # 65% normal evolutionary reproduction.
            c=list(a.p)

            if rng.random()<.55:
                b=rng.choice(elite)
                c=crossover(c,b.p,rng)

            # 30% of offspring receive genetic material from the oracle target.
            # The target is not inserted directly: it is only crossed/mutated.
            if rng.random()<.30:
                c=crossover(c,list(target),rng)

            if rng.random()<.92:
                c=mutate(c,rng)

            new.append(Hyp(c))

        pool=new

    evaluated=[h for h in pool if h.evaluated]
    if not evaluated:
        raise RuntimeError("Evolution produced no evaluated hypotheses")

    # Final selection uses both empirical evidence and behavioral fitness.
    evaluated.sort(
        key=lambda h: behavioral_score(h),
        reverse=True,
    )

    return evaluated[0],history

def benchmark(seeds=(3,11,29,47)):

    rows=[]
    for seed in seeds:
        for ti,target in enumerate(TARGETS):
            best,h=evolve(seed*100+ti,target)
            rng=random.Random(seed*10000+ti)
            xs=[xgen(rng) for _ in range(20)]
            hidden=sum(run(best.p,x)==run(target,x) for x in xs)/len(xs)
            rows.append({
              "seed":seed,"target":ti,"program":canon(best.p),
              "support":best.support,"failures":best.failures,
              "hidden":hidden
            })
    return rows
