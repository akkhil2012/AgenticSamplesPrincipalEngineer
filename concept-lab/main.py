"""Small offline concept lab. See README.md for boundaries and production extensions."""
def apply(proposal, state):
    if set(proposal)!={'action','amount'} or proposal['action']!='refund':
        raise ValueError('Invalid proposal')
    amount=proposal['amount']
    if type(amount) is not int or not 0 < amount <= 100:
        raise PermissionError('Refund cap')
    state['refunded']+=amount
    return state.copy()
def demo():
    state={'refunded':0}
    return apply({'action':'refund','amount':40},state)

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
