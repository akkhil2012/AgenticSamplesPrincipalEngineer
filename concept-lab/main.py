"""Small offline concept lab. See README.md for boundaries and production extensions."""
class Run:
    def __init__(self,scopes,max_actions,max_amount):
        self.scopes=frozenset(scopes); self.remaining=max_actions; self.amount=max_amount
    def refund(self,amount):
        if 'refund' not in self.scopes or self.remaining<=0 or type(amount) is not int or not 0<amount<=self.amount:
            raise PermissionError('Privilege/agency limit')
        self.remaining-=1; self.amount-=amount
        return {'refunded':amount}
def demo():
    run=Run({'refund'},2,100); run.refund(40); run.refund(60)
    return {'actions_left':run.remaining,'amount_left':run.amount}

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
