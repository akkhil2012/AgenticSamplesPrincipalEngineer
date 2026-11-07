"""Small offline concept lab. See README.md for boundaries and production extensions."""
import hashlib, json
REQUIRED={'identity','policy_decision','approval','execution','review_owner'}
def evidence_bundle(run):
    missing=sorted(REQUIRED-set(run))
    payload=json.dumps(run,sort_keys=True,separators=(',',':'))
    return {'run':run,'missing':missing,'evidence_complete':not missing,
            'checksum':hashlib.sha256(payload.encode()).hexdigest(),
            'assessment':'Evidence inventory only; requires control review'}
def demo():
    return evidence_bundle({'identity':'alice','policy_decision':'allow@v3','approval':'a1',
                            'execution':'ticket-closed','review_owner':'bob'})

if __name__ == '__main__':
    import json
    print(json.dumps(demo(), indent=2))
