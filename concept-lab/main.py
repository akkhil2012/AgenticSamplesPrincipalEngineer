"""Small offline concept lab. See README.md for boundaries and production extensions."""
def delegate(start,next_agent,max_hops=5):
    seen=set(); path=[]; agent=start
    for _ in range(max_hops):
        if agent in seen: return {'status':'cycle','path':path}
        seen.add(agent); path.append(agent)
        agent=next_agent(agent)
        if agent is None: return {'status':'completed','path':path}
    return {'status':'hop_limit','path':path}
def demo(): return delegate('a',lambda a: {'a':'b','b':'a'}[a])

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
