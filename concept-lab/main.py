"""Small offline concept lab. See README.md for boundaries and production extensions."""
def acceptable(answer): return answer.startswith('Evidence:') and len(answer)<=100
def reflect(draft,reviser,max_revisions=2):
    history=[draft]
    for _ in range(max_revisions):
        if acceptable(draft): break
        draft=reviser(draft,'Include evidence and keep under 100 characters'); history.append(draft)
    return {'answer':draft,'accepted':acceptable(draft),'revisions':len(history)-1}
def demo(): return reflect('Unsupported claim',lambda draft,critique:'Evidence: ticket INC-7 is open.')

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
