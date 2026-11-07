"""Small offline concept lab. See README.md for boundaries and production extensions."""
def run(model, tools, allowed, max_steps=4):
    memory=[]; events=[]
    for step in range(max_steps):
        proposal=model(list(memory))
        events.append({'step':step, 'proposal':proposal})
        if proposal['kind']=='answer':
            return {'state':'completed', 'answer':proposal['text'], 'events':events}
        name=proposal['tool']
        if name not in allowed: raise PermissionError(name)
        memory.append(tools[name]())
    raise RuntimeError('Step budget exhausted')
def demo():
    return run(lambda history: {'kind':'answer','text':history[0]} if history else
               {'kind':'tool','tool':'status'}, {'status':lambda:'ticket open'}, {'status'})

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
