"""Small offline concept lab. See README.md for boundaries and production extensions."""
class Catalog:
    def __init__(self): self.tools={('count',1):{'approved':True,'handler':len}}
    def discover(self,scopes):
        return [{'name':name,'version':v} for (name,v),x in self.tools.items() if x['approved'] and name in scopes]
    def call(self,name,version,args,scopes):
        item=self.tools.get((name,version))
        if not item or not item['approved'] or name not in scopes: raise PermissionError('Unapproved tool')
        return item['handler'](args)
def demo():
    c=Catalog(); found=c.discover({'count'}); c.tools[('count',1)]['approved']=False
    try: c.call('count',1,[],{'count'})
    except PermissionError: return {'discovered':found,'after_revocation':'denied'}

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
