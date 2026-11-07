"""Small offline concept lab. See README.md for boundaries and production extensions."""
import sqlite3, tempfile
from pathlib import Path
def connect(path):
    db=sqlite3.connect(path)
    db.execute('CREATE TABLE IF NOT EXISTS workflows(id TEXT PRIMARY KEY, state TEXT NOT NULL)')
    return db
def transition(db, wid, expected, target):
    if (expected,target) not in {('pending','running'),('running','completed')}:
        raise ValueError('Invalid transition')
    with db:
        if db.execute('UPDATE workflows SET state=? WHERE id=? AND state=?',(target,wid,expected)).rowcount!=1:
            raise RuntimeError('Stale state')
def demo():
    with tempfile.TemporaryDirectory() as tmp:
        path=Path(tmp)/'state.db'
        with connect(path) as db: db.execute('INSERT INTO workflows VALUES (?,?)',('w1','pending'))
        db.close(); db=connect(path)
        transition(db,'w1','pending','running'); transition(db,'w1','running','completed')
        state=db.execute('SELECT state FROM workflows').fetchone()[0]; db.close()
        return {'recovered':state}

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
