"""Small offline concept lab. See README.md for boundaries and production extensions."""
def current(docs,now):
    valid=[d for d in docs if d['expires']>now and d['updated']<=now]
    latest={}
    for d in valid:
        if d['key'] not in latest or d['version']>latest[d['key']]['version']: latest[d['key']]=d
    return list(latest.values())
def answer(docs,now):
    rows=current(docs,now)
    return {'status':'grounded','sources':[d['id'] for d in rows]} if rows else {'status':'abstain','sources':[]}
def demo():
    return answer([{'id':'old','key':'policy','version':1,'updated':0,'expires':20},
                   {'id':'new','key':'policy','version':2,'updated':5,'expires':30}],10)

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
