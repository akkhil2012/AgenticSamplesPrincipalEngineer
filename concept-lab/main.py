"""Small offline concept lab. See README.md for boundaries and production extensions."""
import asyncio
async def specialist(name,value):
    await asyncio.sleep(0)
    return {'agent':name,'value':value}
async def orchestrate():
    lookup=await specialist('lookup',3)
    children=await asyncio.gather(specialist('sales',lookup['value']*2),specialist('support',lookup['value']+1))
    return {'parent':'supervisor','lookup':lookup,'children':children,'total':sum(c['value'] for c in children)}
def demo(): return asyncio.run(orchestrate())

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
