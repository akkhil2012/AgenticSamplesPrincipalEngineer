"""Small offline concept lab. See README.md for boundaries and production extensions."""
def chatbot(message):
    return 'I can explain ticket closure; no action was executed.'

def platform(action, scopes, audit):
    if action != 'close_ticket' or action not in scopes:
        raise PermissionError('Action denied')
    result = {'ticket': 'INC-7', 'status': 'closed'}
    audit.append({'action': action, 'result': result.copy()})
    return result

def demo():
    audit = []
    return {'chatbot': chatbot('close it'),
            'platform': platform('close_ticket', {'close_ticket'}, audit), 'audit': audit}

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
