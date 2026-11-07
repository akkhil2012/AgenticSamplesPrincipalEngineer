"""Small offline concept lab. See README.md for boundaries and production extensions."""
import hashlib, json
def fingerprint(change): return hashlib.sha256(json.dumps(change,sort_keys=True).encode()).hexdigest()
class Production:
    def __init__(self): self.version=1; self.value='old'; self.consumed=set()
    def apply(self,change,approval,scopes,now):
        if 'prod:write' not in scopes or approval['expires']<=now or approval['digest']!=fingerprint(change):
            raise PermissionError('Live authorization or bound approval denied')
        if approval['id'] in self.consumed: raise PermissionError('Approval replay')
        if change['expected_version']!=self.version: raise RuntimeError('Resource changed; re-review')
        self.value=change['value']; self.version+=1; self.consumed.add(approval['id'])
        return {'version':self.version,'value':self.value}
def demo():
    change={'expected_version':1,'value':'new'}
    return Production().apply(change,{'id':'a1','expires':100,'digest':fingerprint(change)},{'prod:write'},50)

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
