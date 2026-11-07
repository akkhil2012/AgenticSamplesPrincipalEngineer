"""Small offline concept lab. See README.md for boundaries and production extensions."""
def collect(tasks,previous=None):
    results=dict(previous or {}); failures={}
    for name,fn in tasks.items():
        if name in results: continue
        try: results[name]=fn()
        except TimeoutError as exc: failures[name]=str(exc)
    return {'results':results,'failures':failures,'status':'partial' if failures else 'completed'}
def fail(): raise TimeoutError('retryable')
def demo():
    first=collect({'sales':lambda:10,'support':fail})
    second=collect({'sales':lambda:1/0,'support':lambda:3},first['results'])
    return {'first':first,'recovered':second}

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
