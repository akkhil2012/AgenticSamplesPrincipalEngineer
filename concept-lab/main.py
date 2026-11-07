"""Small offline concept lab. See README.md for boundaries and production extensions."""
class Circuit:
    def __init__(self, cooldown=10): self.until=0; self.open=False; self.cooldown=cooldown
    def call(self, upstream, now):
        if self.open and now<self.until: return {'value':'cached','degraded':True}
        try: value=upstream()
        except TimeoutError:
            self.open=True; self.until=now+self.cooldown
            return {'value':'cached','degraded':True}
        self.open=False
        return {'value':value,'degraded':False}
def unavailable(): raise TimeoutError('upstream')
def demo():
    c=Circuit()
    return [c.call(unavailable,0),c.call(lambda:'live',1),c.call(lambda:'live',11)]

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
