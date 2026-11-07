"""Small offline concept lab. See README.md for boundaries and production extensions."""
def verify(identity,resource,now):
    if not identity['verified'] or identity['expires']<=now or identity['audience']!='tools':
        raise PermissionError('Identity denied')
    if identity['tenant']!=resource['tenant'] or resource['action'] not in identity['scopes']:
        raise PermissionError('Resource policy denied')
    return 'allowed'
def demo():
    identity={'verified':True,'expires':10,'audience':'tools','tenant':'a','scopes':['read']}
    return verify(identity,{'tenant':'a','action':'read'},1)

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
