"""Small offline concept lab. See README.md for boundaries and production extensions."""
from copy import deepcopy
class TenantStore:
    def __init__(self,quota=2): self.rows={}; self.quota=quota
    def put(self,tenant,key,value):
        partition=self.rows.setdefault(tenant,{})
        if key not in partition and len(partition)>=self.quota: raise RuntimeError('Tenant quota')
        partition[key]=deepcopy(value)
    def get(self,tenant,key): return deepcopy(self.rows.get(tenant,{}).get(key))
def demo():
    s=TenantStore(); s.put('a','session','private-a'); s.put('b','session','private-b')
    return {'a':s.get('a','session'),'b':s.get('b','session')}

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
