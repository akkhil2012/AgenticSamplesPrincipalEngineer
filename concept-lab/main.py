"""Small offline concept lab. See README.md for boundaries and production extensions."""
def pdp(subject,action,resource):
    allowed=subject['tenant']==resource['tenant'] and action in subject['scopes']
    return {'allow':allowed,'policy_version':3,'reason':'matched' if allowed else 'scope_or_tenant'}
def pep(subject,action,resource,decision_service,effects):
    try: decision=decision_service(subject,action,resource)
    except TimeoutError: raise PermissionError('Policy unavailable; fail closed') from None
    if decision.get('allow') is not True: raise PermissionError('Policy denied')
    effects.append(action)
    return {'executed':action,'policy_version':decision['policy_version']}
def unavailable(*args): raise TimeoutError('PDP offline')
def demo(): return pep({'tenant':'a','scopes':['read']},'read',{'tenant':'a'},pdp,[])

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
