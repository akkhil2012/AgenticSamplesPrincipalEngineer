"""Small offline concept lab. See README.md for boundaries and production extensions."""
from dataclasses import dataclass
@dataclass(frozen=True)
class Manifest:
    name: str
    version: int
    capability: str
    active: bool=True
class Registry:
    def __init__(self): self.items={}
    def register(self,item):
        key=(item.name,item.version)
        if key in self.items: raise ValueError('Version already registered')
        self.items[key]=item
    def discover(self,capability,version):
        return [x.name for x in self.items.values() if x.active and x.capability==capability and x.version==version]
def demo():
    r=Registry(); r.register(Manifest('engagement',1,'metrics')); return r.discover('metrics',1)

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
