"""Small offline concept lab. See README.md for boundaries and production extensions."""
class Supervisor:
    def __init__(self): self.registry={}
    def register(self,capability,handler): self.registry[capability]=handler
    def dispatch(self,goal):
        if goal['capability'] not in self.registry: raise ValueError('No specialist')
        result=self.registry[goal['capability']](goal['input'])
        return {'delegated_to':goal['capability'],'result':result}
def demo():
    s=Supervisor(); s.register('engagement',lambda rows:sum(rows))
    return s.dispatch({'capability':'engagement','input':[4,6]})

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
