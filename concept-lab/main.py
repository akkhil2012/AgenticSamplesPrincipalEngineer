"""Small offline concept lab. See README.md for boundaries and production extensions."""
TOOLS={'sales':lambda:120, 'support':lambda:3}
def invoke(role, tool):
    permissions={'generalist':set(TOOLS), 'sales':{'sales'}, 'support':{'support'}}
    if tool not in permissions[role]: raise PermissionError('Specialist boundary')
    return TOOLS[tool]()
def single():
    return {'sales':invoke('generalist','sales'), 'support':invoke('generalist','support')}
def multi():
    return {role:invoke(role, role) for role in TOOLS}
def demo():
    return {'single':single(), 'multi':multi(), 'delegations':2}

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
