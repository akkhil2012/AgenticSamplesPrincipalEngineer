"""Small offline concept lab. See README.md for boundaries and production extensions."""
from dataclasses import dataclass
@dataclass(frozen=True)
class Identity:
    subject: str
    tenant: str
    scopes: frozenset
    actors: tuple=()
def delegate(parent,actor,requested):
    if not set(requested)<=parent.scopes: raise PermissionError('Scope escalation')
    return Identity(parent.subject,parent.tenant,frozenset(requested),parent.actors+(actor,))
def demo():
    root=Identity('alice','a',frozenset({'read','write'}))
    worker=delegate(delegate(root,'supervisor',{'read'}),'specialist',{'read'})
    return {'subject':worker.subject,'tenant':worker.tenant,'scopes':sorted(worker.scopes),'actors':worker.actors}

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
