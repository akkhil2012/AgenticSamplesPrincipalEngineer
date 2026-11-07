"""Small offline concept lab. See README.md for boundaries and production extensions."""
class Capability:
    def __init__(self, tools, remaining): self.tools=frozenset(tools); self.remaining=remaining
    def call(self, tool, workload_scopes):
        if tool not in self.tools or tool not in workload_scopes or self.remaining<=0:
            raise PermissionError('Privilege or agency denied')
        self.remaining-=1
        return tool+' executed'
def demo():
    cap=Capability({'read'},1)
    return {'result':cap.call('read',{'read','write'}),'remaining':cap.remaining}

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
