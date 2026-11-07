"""Small offline concept lab. See README.md for boundaries and production extensions."""
import hashlib, hmac, json, secrets
class Channel:
    def __init__(self): self.key=secrets.token_bytes(32); self.seen=set()
    def sign(self,payload):
        body=json.dumps(payload,sort_keys=True,separators=(',',':'))
        return {'body':body,'mac':hmac.new(self.key,body.encode(),hashlib.sha256).hexdigest()}
    def receive(self,envelope,audience,now):
        expected=hmac.new(self.key,envelope['body'].encode(),hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected,envelope['mac']): raise PermissionError('Signature invalid')
        p=json.loads(envelope['body'])
        if p['aud']!=audience or p['expires']<=now or p['nonce'] in self.seen:
            raise PermissionError('Audience, expiry, or replay denied')
        self.seen.add(p['nonce']); return p['task']
def demo():
    c=Channel(); e=c.sign({'aud':'worker','expires':100,'nonce':'n1','task':'count'})
    return {'verified_task':c.receive(e,'worker',50)}

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
