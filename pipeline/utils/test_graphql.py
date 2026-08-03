"""Test GraphQL API endpoints."""
import sys
sys.path.insert(0, r"C:\Users\youss\OneDrive\Desktop\Yoyo\prediction maroc")
import json
from fastapi.testclient import TestClient
from scripts.graph_api import app

client = TestClient(app)

# REST endpoint
r = client.get("/")
print("REST /:", r.json())

# GraphQL queries
queries = [
    "{ graphStats }",
    "{ sources { code } }",
    "{ domains { code } }",
    '{ indicators(limit: 5) { code unit obsCount } }',
    '{ indicator(code: "NGDP_RPCH") { code label unit yearMin yearMax source } }',
    '{ indicators(source: "IMF-WEO", limit: 3) { code label yearMin yearMax } }',
    '{ indicators(domain: "ECONOMIE", limit: 3) { code unit } }',
]

for q in queries:
    r = client.post("/graphql", json={"query": q})
    data = r.json()
    print(f'\nQuery: {q}')
    if "errors" in data:
        print(f'  ERROR: {data["errors"]}')
    else:
        d = data.get("data", {})
        key = list(d.keys())[0] if d else "?"
        val = d.get(key, "")
        if isinstance(val, list):
            print(f'  OK: {len(val)} results')
            if len(val) > 0:
                print(f'  First: {json.dumps(val[0], indent=2)}')
        else:
            print(f'  OK: {val}')
