"""Small offline concept lab. See README.md for boundaries and production extensions."""
from copy import deepcopy
def share(context,recipient_tenant):
    if context['tenant']!=recipient_tenant: raise PermissionError('Tenant mismatch')
    fields={'tenant','task_id','aggregate'}
    return deepcopy({k:v for k,v in context.items() if k in fields})
def demo():
    ctx={'tenant':'a','task_id':'w1','aggregate':{'count':5},'raw_email':'secret@example.com'}
    return share(ctx,'a')

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
