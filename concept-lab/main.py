"""Small offline concept lab. See README.md for boundaries and production extensions."""
import uuid
def perform(action, allowed, events):
    trace=str(uuid.uuid4())
    events.append({'trace':trace,'event':'proposed','action':action})
    decision=action in allowed
    events.append({'trace':trace,'event':'policy','allowed':decision})
    if not decision: return {'trace':trace,'status':'denied'}
    events.append({'trace':trace,'event':'executed','result':'ok'})
    return {'trace':trace,'status':'completed'}
def demo():
    events=[]; result=perform('read',{'read'},events)
    return {'result':result,'events':events}

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
