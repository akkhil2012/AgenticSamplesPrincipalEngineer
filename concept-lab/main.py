"""Small offline concept lab. See README.md for boundaries and production extensions."""
import sqlite3, json
class Queue:
    def __init__(self):
        self.db=sqlite3.connect(':memory:')
        self.db.execute('CREATE TABLE actions(id TEXT PRIMARY KEY,payload TEXT,status TEXT,reviewer TEXT)')
    def propose(self,aid,payload):
        with self.db: self.db.execute('INSERT INTO actions VALUES (?,?,?,NULL)',(aid,json.dumps(payload,sort_keys=True),'pending'))
    def approve(self,aid,reviewer):
        with self.db:
            if self.db.execute("UPDATE actions SET status='approved', reviewer=? WHERE id=? AND status='pending'",(reviewer,aid)).rowcount!=1:
                raise PermissionError('Not pending')
    def consume(self,aid):
        with self.db:
            row=self.db.execute("SELECT payload,reviewer FROM actions WHERE id=? AND status='approved'",(aid,)).fetchone()
            if not row: raise PermissionError('Approval required or consumed')
            self.db.execute("UPDATE actions SET status='consumed' WHERE id=?",(aid,))
        return {'payload':json.loads(row[0]),'reviewer':row[1]}
def demo():
    q=Queue(); q.propose('a',{'close':'INC-7'}); q.approve('a','bob'); return q.consume('a')

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
