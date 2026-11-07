"""Small offline concept lab. See README.md for boundaries and production extensions."""
def tool_call(name,args):
    if name!='count' or not isinstance(args.get('rows'),list): raise ValueError('Tool contract')
    return len(args['rows'])
class Agent:
    def __init__(self): self.tasks={}
    def delegate(self,task_id,goal):
        if goal['capability']!='report': raise ValueError('Unsupported capability')
        if task_id in self.tasks: return self.tasks[task_id]
        count=tool_call('count',{'rows':goal['rows']})
        self.tasks[task_id]={'state':'completed','artifact':f'Report count: {count}'}
        return self.tasks[task_id]
def demo():
    return {'tool':tool_call('count',{'rows':[1,2]}),'delegation':Agent().delegate('t1',{'capability':'report','rows':[1,2]})}

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
