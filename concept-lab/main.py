"""Small offline concept lab. See README.md for boundaries and production extensions."""
def receive(task):
    required={'version','task_id','capability','input'}
    if set(task)!=required or task['version']!=1:
        return {'status':'failed','error':{'code':'CONTRACT_INVALID','retryable':False}}
    if task['capability']!='count' or not isinstance(task['input'],list):
        return {'status':'failed','error':{'code':'UNSUPPORTED_TASK','retryable':False}}
    return {'status':'completed','task_id':task['task_id'],'output':len(task['input'])}
def demo():
    return receive({'version':1,'task_id':'t1','capability':'count','input':[1,2]})

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
