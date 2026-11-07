"""Small offline concept lab. See README.md for boundaries and production extensions."""
import sqlite3, tempfile
from pathlib import Path
def resume(path,wid,steps):
    db=sqlite3.connect(path); executed=[]
    try:
        db.execute('CREATE TABLE IF NOT EXISTS steps(workflow TEXT,step TEXT,result TEXT,PRIMARY KEY(workflow,step))')
        for name,fn in steps:
            if db.execute('SELECT 1 FROM steps WHERE workflow=? AND step=?',(wid,name)).fetchone(): continue
            value=fn()
            with db: db.execute('INSERT INTO steps VALUES (?,?,?)',(wid,name,value))
            executed.append(name)
    finally: db.close()
    return executed
def crash(): raise RuntimeError('Worker crashed')
def demo():
    with tempfile.TemporaryDirectory() as tmp:
        path=Path(tmp)/'workflow.db'
        try: resume(path,'w',[('lookup',lambda:'ok'),('report',crash)])
        except RuntimeError: pass
        return {'resumed_steps':resume(path,'w',[('lookup',lambda:1/0),('report',lambda:'done')])}

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
