"""Small offline concept lab. See README.md for boundaries and production extensions."""
from copy import deepcopy
class Sessions:
    def __init__(self): self.data={}
    def put(self,tenant,user,sid,messages,now,ttl):
        if ttl<=0: raise ValueError('TTL must be positive')
        self.data[(tenant,user,sid)]=(now+ttl,deepcopy(messages))
    def get(self,tenant,user,sid,now):
        key=(tenant,user,sid); row=self.data.get(key)
        if not row: return []
        if row[0]<=now: del self.data[key]; return []
        return deepcopy(row[1])
    def delete(self,tenant,user,sid): self.data.pop((tenant,user,sid),None)
def demo():
    s=Sessions(); s.put('a','alice','s1',['hello'],0,10)
    return {'active':s.get('a','alice','s1',1),'expired':s.get('a','alice','s1',10)}

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
