"""Small offline concept lab. See README.md for boundaries and production extensions."""
import hashlib
def route(tenant, percent, stable='1.0', candidate='1.1'):
    if not 0<=percent<=100: raise ValueError('Invalid rollout')
    bucket=int(hashlib.sha256(tenant.encode()).hexdigest(),16)%100
    return candidate if bucket<percent else stable
def accept(version):
    if version.split('.')[0]!='1': raise ValueError('Unsupported major')
    return version
def demo():
    return {'canary':accept(route('tenant-a',100)), 'rollback':accept(route('tenant-a',0))}

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
