
import json,statistics
from .core import benchmark
rows=benchmark()
with open("results.json","w") as f: json.dump(rows,f,indent=2)
v=[r["hidden"] for r in rows]
print("ForgeMind 0.8.0")
print("experiments =",len(rows))
print("hidden mean =",round(statistics.mean(v),3))
print("hidden median =",round(statistics.median(v),3))
print("hidden min =",round(min(v),3))
print("hidden max =",round(max(v),3))
print("perfect tasks =",sum(x==1 for x in v),"/",len(v))
for s in sorted(set(r["seed"] for r in rows)):
    q=[r["hidden"] for r in rows if r["seed"]==s]
    print("seed",s,"mean",round(statistics.mean(q),3))
