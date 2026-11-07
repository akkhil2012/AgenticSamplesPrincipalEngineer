"""Small offline concept lab. See README.md for boundaries and production extensions."""
ALLOWED={'lookup','summarize'}
def execute(plan):
    if not 1 <= len(plan) <= 3 or any(step not in ALLOWED for step in plan):
        raise ValueError('Invalid or unbounded plan')
    return ['done:'+step for step in plan]
def route(kind, planner):
    plan=['lookup','summarize'] if kind=='report' else planner()
    return execute(plan)
def demo():
    return {'fixed':route('report',lambda:[]), 'planned':route('research',lambda:['lookup'])}

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
