"""Small offline concept lab. See README.md for boundaries and production extensions."""
import hashlib, json
def digest(action): return hashlib.sha256(json.dumps(action,sort_keys=True).encode()).hexdigest()
def approve(action, requester, reviewer, expires):
    if requester==reviewer: raise PermissionError('Independent reviewer required')
    return {'digest':digest(action),'reviewer':reviewer,'expires':expires}
def execute(action, approval, now):
    if approval['digest']!=digest(action) or now>=approval['expires']:
        raise PermissionError('Approval invalid')
    return {'action':action,'accountable_reviewer':approval['reviewer']}
def demo():
    action={'ticket':'INC-7','operation':'close'}
    return execute(action,approve(action,'alice','bob',100),50)

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
