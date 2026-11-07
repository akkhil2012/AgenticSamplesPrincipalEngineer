"""Small offline concept lab. See README.md for boundaries and production extensions."""
class Index:
    def __init__(self,model,dim,rows):
        if any(len(v)!=dim for v in rows.values()): raise ValueError('Dimension mismatch')
        self.model=model; self.dim=dim; self.rows=rows
    def search(self,model,vector):
        if model!=self.model or len(vector)!=self.dim: raise ValueError('Embedding space mismatch')
        return min(self.rows,key=lambda k:sum((a-b)**2 for a,b in zip(self.rows[k],vector)))
class Migration:
    def __init__(self,old,new): self.active=old; self.old=old; self.new=new
    def promote(self,recall):
        if recall<.95: raise ValueError('Recall gate failed')
        self.active=self.new
    def rollback(self): self.active=self.old
def demo():
    old=Index('v1',2,{'d1':[1,0]}); new=Index('v2',3,{'d1':[1,0,0]})
    migration=Migration(old,new); migration.promote(1.0)
    shadow=new.search('v2',[1,0,0]); migration.rollback()
    return {'shadow_result':shadow,'after_rollback':migration.active.model}

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
