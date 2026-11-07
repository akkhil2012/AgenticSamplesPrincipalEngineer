"""Small offline concept lab. See README.md for boundaries and production extensions."""
import math
EDGES={'alice':['team-a'],'team-a':['project-x'],'bob':['team-b']}
VECTORS={'project-x':[1.,0.], 'project-y':[0.,1.]}
def traverse(start,hops):
    nodes={start}
    for _ in range(hops): nodes={v for n in nodes for v in EDGES.get(n,[])}
    return sorted(nodes)
def cosine(a,b):
    if len(a)!=len(b): raise ValueError('Dimension mismatch')
    denom=math.sqrt(sum(x*x for x in a)*sum(x*x for x in b))
    return sum(x*y for x,y in zip(a,b))/denom if denom else 0.
def semantic(query): return sorted(VECTORS,key=lambda k:(-cosine(query,VECTORS[k]),k))
def demo(): return {'graph_relationship':traverse('alice',2),'vector_similarity':semantic([.9,.1])}

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
