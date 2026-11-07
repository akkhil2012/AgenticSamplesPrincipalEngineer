"""Small offline concept lab. See README.md for boundaries and production extensions."""
from dataclasses import dataclass
@dataclass(frozen=True)
class Definition:
    version: int
    tools: frozenset
class ControlPlane:
    def __init__(self):
        self.versions = {}
        self.revoked = set()
    def publish(self, version, tools):
        if version in self.versions: raise ValueError('Immutable version')
        self.versions[version] = Definition(version, frozenset(tools))
    def execute(self, version, tool):
        if tool in self.revoked or tool not in self.versions[version].tools:
            raise PermissionError('Live policy denied')
        return {'version': version, 'tool': tool}
def demo():
    cp=ControlPlane(); cp.publish(1, ['read'])
    before=cp.execute(1, 'read'); cp.revoked.add('read')
    try: cp.execute(1, 'read')
    except PermissionError: return {'before':before, 'after':'revoked'}

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
