"""Small offline concept lab. See README.md for boundaries and production extensions."""
def planner(goal):
    if goal!='report': raise ValueError('Unsupported goal')
    return [{'tool':'count','rows':[1,2,3]},{'tool':'format'}]
def executor(plan):
    if not plan or len(plan)>3: raise ValueError('Plan size')
    for step in plan:
        if step['tool'] not in {'count','format'}: raise PermissionError('Tool denied')
    value=None
    for step in plan:
        if step['tool']=='count': value=len(step['rows'])
        else: value=f'Count: {value}'
    return value
def demo(): return {'plan':planner('report'),'result':executor(planner('report'))}

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
