"""Small offline concept lab. See README.md for boundaries and production extensions."""
def deputy(user,agent,request):
    if request['tenant']!=user['tenant'] or request['resource'] not in user['resources']:
        raise PermissionError('Original user resource boundary')
    if request['action'] not in user['scopes'] or request['action'] not in agent['scopes']:
        raise PermissionError('Delegation scope boundary')
    return {'resource':request['resource'],'action':request['action'],'on_behalf_of':user['id']}
def demo():
    return deputy({'id':'alice','tenant':'a','resources':['t1'],'scopes':['read']},
                  {'scopes':['read','delete']},{'tenant':'a','resource':'t1','action':'read'})

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
