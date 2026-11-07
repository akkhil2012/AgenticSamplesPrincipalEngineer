"""Small offline concept lab. See README.md for boundaries and production extensions."""
from copy import deepcopy
class SharedMemory:
    def __init__(self): self.rows={}
    def read(self,tenant,key): return deepcopy(self.rows.get((tenant,key),(0,None)))
    def write(self,tenant,key,expected,value):
        version,_=self.read(tenant,key)
        if version!=expected: raise RuntimeError('Version conflict; reread and reconcile')
        self.rows[(tenant,key)]=(version+1,deepcopy(value)); return version+1
def demo():
    mem=SharedMemory(); mem.write('a','task',0,{'owner':'agent-1'})
    version,value=mem.read('a','task'); value['reviewed_by']='agent-2'
    mem.write('a','task',version,value); return mem.read('a','task')

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
