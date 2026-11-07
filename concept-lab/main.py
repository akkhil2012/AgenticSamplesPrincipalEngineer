"""Small offline concept lab. See README.md for boundaries and production extensions."""
import sqlite3, json
class Tool:
    def __init__(self):
        self.db=sqlite3.connect(':memory:')
        self.db.execute('CREATE TABLE calls(tenant TEXT,workflow TEXT,step TEXT,payload TEXT,result INTEGER,PRIMARY KEY(tenant,workflow,step))')
        self.effects=0
    def call(self,tenant,workflow,step,payload,lose_reply=False):
        body=json.dumps(payload,sort_keys=True)
        with self.db:
            row=self.db.execute('SELECT payload,result FROM calls WHERE tenant=? AND workflow=? AND step=?',(tenant,workflow,step)).fetchone()
            if row:
                if row[0]!=body: raise ValueError('Idempotency payload conflict')
                result=row[1]
            else:
                self.effects+=1; result=self.effects
                self.db.execute('INSERT INTO calls VALUES (?,?,?,?,?)',(tenant,workflow,step,body,result))
        if lose_reply: raise TimeoutError('Effect committed; reply lost')
        return result
def demo():
    t=Tool()
    try: t.call('a','w','s',{'amount':10},True)
    except TimeoutError: pass
    return {'retry_result':t.call('a','w','s',{'amount':10}),'effects':t.effects}

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
