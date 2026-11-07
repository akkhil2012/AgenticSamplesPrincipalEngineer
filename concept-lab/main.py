"""Small offline concept lab. See README.md for boundaries and production extensions."""
import secrets
class SecretAdapter:
    def __init__(self): self._vault={'service-token':secrets.token_hex(24)}; self.audit=[]
    def invoke(self,ref,scopes):
        if ref!='service-token' or 'service:call' not in scopes: raise PermissionError('Secret use denied')
        token=self._vault[ref]
        # A real HTTPS client consumes token here; never forward it to model context.
        authenticated=bool(token)
        self.audit.append({'reference':ref,'operation':'service_call'})
        return {'status':'ok' if authenticated else 'error'}
    def rotate(self): self._vault['service-token']=secrets.token_hex(24)
def demo():
    a=SecretAdapter(); result=a.invoke('service-token',{'service:call'}); a.rotate()
    return {'result':result,'audit':a.audit}

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
