"""Small offline concept lab. See README.md for boundaries and production extensions."""
REGISTRY = {'ticket_status': lambda ticket: {'ticket': ticket, 'status': 'open'}}
def handle(request, principal):
    if set(request) != {'intent', 'ticket'}:
        raise ValueError('Invalid request contract')
    intent = request['intent']
    if intent not in principal['scopes']:
        raise PermissionError('Scope denied')
    if intent not in REGISTRY:
        raise ValueError('Unknown capability')
    result = REGISTRY[intent](request['ticket'])
    return {'result': result, 'trace': ['validated', 'routed', 'authorized', 'executed']}
def demo():
    return handle({'intent': 'ticket_status', 'ticket': 'INC-7'}, {'scopes': ['ticket_status']})

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
