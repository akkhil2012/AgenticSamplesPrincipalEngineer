"""Small offline concept lab. See README.md for boundaries and production extensions."""
class Gateway:
    def __init__(self): self.routes={'count':len}; self.audit=[]
    def call(self,tool,args,user_scopes,agent_scopes):
        allowed=tool in user_scopes and tool in agent_scopes and tool in self.routes
        self.audit.append({'tool':tool,'allowed':allowed})
        if not allowed: raise PermissionError('Gateway denied')
        if not isinstance(args,list): raise ValueError('Expected list')
        return self.routes[tool](args)
def demo():
    g=Gateway(); value=g.call('count',[1,2],{'count'},{'count'})
    return {'value':value,'audit':g.audit}

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
