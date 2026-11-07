"""Small offline concept lab. See README.md for boundaries and production extensions."""
class Memory:
    def __init__(self): self.short={}; self.long={}
    def remember(self,user,key,value,consent=False):
        if not consent or key not in {'language','timezone'}: raise PermissionError('Long-term memory consent/schema')
        self.long[(user,key)]=value
    def context(self,user,now):
        row=self.short.get(user)
        return {'session':row[1] if row and row[0]>now else [],
                'preferences':{k:v for (u,k),v in self.long.items() if u==user}}
def demo():
    m=Memory(); m.short['alice']=(10,['hello']); m.remember('alice','language','English',True)
    return {'active':m.context('alice',1),'after_ttl':m.context('alice',10)}

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
