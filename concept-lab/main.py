"""Small offline concept lab. See README.md for boundaries and production extensions."""
SCHEMA={'name':'add','inputSchema':{'type':'object','properties':{'a':{'type':'integer'},'b':{'type':'integer'}},'required':['a','b'],'additionalProperties':False}}
def dispatch(method,params):
    if method=='tools/list': return {'tools':[SCHEMA]}
    if method!='tools/call' or params.get('name')!='add': raise ValueError('Unknown method/tool')
    args=params['arguments']
    if set(args)!={'a','b'} or any(type(v) is not int for v in args.values()): raise ValueError('Invalid arguments')
    return {'content':[{'type':'text','text':str(args['a']+args['b'])}],'isError':False}
def demo():
    return {'discovery':dispatch('tools/list',{}),'call':dispatch('tools/call',{'name':'add','arguments':{'a':2,'b':3}})}

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
