"""Small offline concept lab. See README.md for boundaries and production extensions."""
import math
def metrics(runs):
    if not runs: raise ValueError('No observations')
    successes=sum(r['success'] for r in runs)
    latency=sorted(r['latency_ms'] for r in runs)
    return {'success_rate':successes/len(runs), 'p95_ms':latency[math.ceil(.95*len(runs))-1],
            'cost_per_success':sum(r['cents'] for r in runs)/successes if successes else None,
            'delegations_per_run':sum(r['delegations'] for r in runs)/len(runs)}
def demo():
    return metrics([{'success':True,'latency_ms':100,'cents':2,'delegations':2},
                    {'success':False,'latency_ms':300,'cents':1,'delegations':3}])

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
