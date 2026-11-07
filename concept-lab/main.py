"""Small offline concept lab. See README.md for boundaries and production extensions."""
class Retriever:
    def __init__(self,docs): self.docs=docs; self.cache={}
    def search(self,tenant,user,query,acl_revision):
        key=(tenant,user,query,acl_revision)
        if key not in self.cache:
            self.cache[key]=tuple(d['id'] for d in self.docs if d['tenant']==tenant and user in d['readers'] and query in d['text'])
        return list(self.cache[key])
def demo():
    r=Retriever([{'id':'secret-a','tenant':'a','readers':['alice'],'text':'policy'}])
    return {'alice':r.search('a','alice','policy',1),'bob':r.search('b','bob','policy',1)}

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
