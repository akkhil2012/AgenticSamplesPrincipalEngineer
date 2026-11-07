"""Small offline concept lab. See README.md for boundaries and production extensions."""
def normalize(message):
    version=message.get('version')
    if version==1 and set(message)=={'version','query'}:
        text=message['query']
    elif version==2 and set(message)=={'version','input'} and set(message['input'])=={'text'}:
        text=message['input']['text']
    else: raise ValueError('Unsupported integration contract')
    if not isinstance(text,str): raise ValueError('Text required')
    return {'text':text}
def demo(): return [normalize({'version':1,'query':'status'}),normalize({'version':2,'input':{'text':'status'}})]

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
