"""Small offline concept lab. See README.md for boundaries and production extensions."""
def retrieve(docs,principal,query,k=2):
    terms=set(query.lower().split())
    candidates=[d for d in docs if d['tenant']==principal['tenant'] and principal['user'] in d['readers']]
    ranked=sorted(candidates,key=lambda d:(-len(terms & set(d['text'].lower().split())),d['id']))
    return [d['id'] for d in ranked if terms & set(d['text'].lower().split())][:k]
DOCS=[{'id':'a1','tenant':'a','readers':['alice'],'text':'refund policy'},
      {'id':'b1','tenant':'b','readers':['bob'],'text':'refund policy confidential'}]
def demo(): return retrieve(DOCS,{'tenant':'a','user':'alice'},'refund')

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
