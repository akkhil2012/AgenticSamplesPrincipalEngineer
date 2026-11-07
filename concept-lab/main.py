"""Small offline concept lab. See README.md for boundaries and production extensions."""
def sanitize(response):
    if set(response)!={'status','count'} or response['status'] not in {'ok','error'} or type(response['count']) is not int:
        raise ValueError('Untrusted tool response contract')
    return {'source':'tool-data','count':response['count'],'status':response['status']}
def next_action(data):
    return 'display_count' if data['status']=='ok' else 'report_error'
def demo(): return {'data':sanitize({'status':'ok','count':5}),'next':'display_count'}

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
