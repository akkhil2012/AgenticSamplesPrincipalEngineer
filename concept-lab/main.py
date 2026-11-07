"""Small offline concept lab. See README.md for boundaries and production extensions."""
def estimate(text):
    # UTF-8 bytes deliberately overestimate many tokenizers; replace with the serving model tokenizer.
    return len(text.encode('utf-8'))
def pack(system,messages,window,output_reserve):
    remaining=window-output_reserve-estimate(system)
    if output_reserve<0 or remaining<0: raise ValueError('System plus reserve exceeds window')
    chosen=[]
    for message in reversed(messages):
        size=estimate(message)
        if size>remaining: break
        chosen.append(message); remaining-=size
    return {'system':system,'messages':list(reversed(chosen)),'output_reserve':output_reserve}
def demo(): return pack('policy',['old message','recent','now'],20,4)

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
