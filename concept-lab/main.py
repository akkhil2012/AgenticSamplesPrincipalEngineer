"""Small offline concept lab. See README.md for boundaries and production extensions."""
import hashlib, hmac, json, secrets
class Journal:
    def __init__(self): self.key=secrets.token_bytes(32); self.rows=[]
    def mac(self,previous,event):
        body=json.dumps({'previous':previous,'event':event},sort_keys=True,separators=(',',':'))
        return hmac.new(self.key,body.encode(),hashlib.sha256).hexdigest()
    def append(self,event):
        previous=self.rows[-1]['hash'] if self.rows else 'GENESIS'
        event=json.loads(json.dumps(event))
        self.rows.append({'event':event,'hash':self.mac(previous,event)})
        return self.rows[-1]['hash']
    def verify(self,checkpoint):
        previous='GENESIS'
        for row in self.rows:
            expected=self.mac(previous,row['event'])
            if not hmac.compare_digest(expected,row['hash']): return False
            previous=row['hash']
        return hmac.compare_digest(previous,checkpoint)
def demo():
    j=Journal(); j.append({'action':'read'}); checkpoint=j.append({'action':'close'})
    before=j.verify(checkpoint); j.rows[0]['event']['action']='delete'
    return {'before':before,'after_tamper':j.verify(checkpoint)}

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
