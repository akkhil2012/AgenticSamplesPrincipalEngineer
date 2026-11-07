"""Small offline concept lab. See README.md for boundaries and production extensions."""
import asyncio
class Budget:
    def __init__(self, steps, cents): self.steps=steps; self.cents=cents
    def reserve(self,cost):
        if cost<0 or self.steps<=0 or cost>self.cents: raise RuntimeError('Budget exhausted')
        self.steps-=1; self.cents-=cost
async def bounded(factory,budget,cost,timeout):
    budget.reserve(cost)
    return await asyncio.wait_for(factory(),timeout)
async def slow():
    await asyncio.sleep(1)
async def ready(): return 'ok'
def demo():
    b=Budget(1,5)
    return {'result':asyncio.run(bounded(ready,b,3,0.1)), 'remaining_cents':b.cents}

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
