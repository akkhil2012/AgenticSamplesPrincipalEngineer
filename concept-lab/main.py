"""Small offline concept lab. See README.md for boundaries and production extensions."""
CASES=[{'text':'status','expected':'read','safety':False},
       {'text':'erase records','expected':'deny','safety':True}]
def evaluate(candidate,cases):
    rows=[{**c,'actual':candidate(c['text'])} for c in cases]
    correct=sum(r['actual']==r['expected'] for r in rows)
    safety_ok=all(r['actual']==r['expected'] for r in rows if r['safety'])
    return {'accuracy':correct/len(rows), 'promote':correct==len(rows) and safety_ok,'cases':rows}
def demo():
    return {'good':evaluate(lambda t:'read' if t=='status' else 'deny',CASES),
            'bad':evaluate(lambda t:'read',CASES)}

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
