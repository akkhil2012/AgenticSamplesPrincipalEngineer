import json
from datetime import date


class KnowledgeService:
    def __init__(self, data_dir):
        self.path = data_dir / "policies"

    def retrieve(self, tenant, query="credit consent approval exclusion"):
        terms = set(query.lower().split())
        latest = {}
        for path in sorted(self.path.glob("*.json")):
            doc = json.loads(path.read_text())
            if doc["tenant"] != tenant:
                continue
            previous = latest.get(doc["id"])
            if previous and previous["version"] == doc["version"]:
                raise ValueError("Ambiguous duplicate policy version")
            if not previous or doc["version"] > previous["version"]:
                latest[doc["id"]] = doc
        # Version selection precedes validity filtering: never downgrade to an old active policy.
        candidates = []
        for doc in latest.values():
            if not doc["active"] or doc["valid_until"] < date.today().isoformat():
                continue
            score = sum(t in (doc["text"] + " " + doc["id"]).lower() for t in terms)
            if score:
                candidates.append((score, doc))
        selected = [doc for _, doc in sorted(candidates, key=lambda x: -x[0])]
        if not {"eligibility", "consent", "approval", "exclusion"}.issubset({d["id"] for d in selected}):
            raise ValueError("Current mandatory tenant policies unavailable")
        return selected
