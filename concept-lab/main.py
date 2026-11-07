"""Small offline concept lab. See README.md for boundaries and production extensions."""
def authorize(user,agent,tool,resource):
    if agent not in user['delegates']: raise PermissionError('Level 1: delegation denied')
    if (tool,resource) not in user['grants'] or tool not in agent_tools(agent):
        raise PermissionError('Level 2: tool/resource denied')
    return 'allowed'
def agent_tools(agent): return {'analyst':{'read'},'operator':{'read','write'}}.get(agent,set())
def demo():
    return authorize({'delegates':{'analyst'},'grants':{('read','r1')}},'analyst','read','r1')

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
