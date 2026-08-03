"""
Graph API: Neo4j graph DB + GraphQL endpoint for RASD-Maroc.
Builds graph relationships from MongoDB data and exposes via GraphQL.
"""
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from neo4j import GraphDatabase
from pymongo import MongoClient
from strawberry.fastapi import GraphQLRouter
import strawberry

ROOT = Path(__file__).resolve().parent.parent
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/rasd_maroc")
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASS", "password123")
MONGO_TLS = os.getenv("MONGODB_TLS", "false").lower() == "true"

mongo_client = MongoClient(MONGODB_URI, tls=MONGO_TLS)
neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))


# ── Neo4j Graph Building ──────────────────────────────────────────────

def build_graph():
    """Extract entities from MongoDB and create graph in Neo4j."""
    db = mongo_client["rasd_maroc"]
    with neo4j_driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
        print("Cleared existing graph")

    # 1. Sources
    sources = set()
    for doc in db.economie.find({}, {"source_code": 1, "unite": 1, "_id": 0}):
        if doc.get("source_code"):
            sources.add(doc["source_code"])
    with neo4j_driver.session() as session:
        for s in sources:
            session.run("MERGE (:Source {code: $code})", code=s)
        print(f"Created {len(sources)} Source nodes")

    # 2. Domain codes
    domains = set()
    for doc in db.economie.find({}, {"domaine_code": 1, "_id": 0}):
        if doc.get("domaine_code") and doc["domaine_code"] != "?":
            domains.add(doc["domaine_code"])
    with neo4j_driver.session() as session:
        for d in domains:
            session.run("MERGE (:Domain {code: $code})", code=d)
        print(f"Created {len(domains)} Domain nodes")

    # 3. Indicators + relationships
    indicators = db.economie.aggregate([
        {"$group": {
            "_id": "$code_indicateur",
            "unite": {"$first": "$unite"},
            "source_code": {"$first": "$source_code"},
            "domaine_code": {"$first": "$domaine_code"},
            "count": {"$sum": 1},
            "date_min": {"$min": "$date"},
            "date_max": {"$max": "$date"},
        }}
    ])
    ind_count = 0
    with neo4j_driver.session() as session:
        for ind in indicators:
            code = ind["_id"]
            if not code:
                continue
            session.run(
                "MERGE (i:Indicator {code: $code}) "
                "SET i.unit = $unit, i.obs_count = $count, "
                "i.date_min = $dmin, i.date_max = $dmax",
                code=code, unit=ind.get("unite"),
                count=ind["count"], dmin=str(ind.get("date_min", "")),
                dmax=str(ind.get("date_max", ""))
            )
            if ind.get("source_code"):
                session.run(
                    "MATCH (i:Indicator {code: $code}) "
                    "MATCH (s:Source {code: $source}) "
                    "MERGE (i)-[:FROM_SOURCE]->(s)",
                    code=code, source=ind["source_code"]
                )
            if ind.get("domaine_code") and ind["domaine_code"] != "?":
                session.run(
                    "MATCH (i:Indicator {code: $code}) "
                    "MATCH (d:Domain {code: $domain}) "
                    "MERGE (i)-[:BELONGS_TO]->(d)",
                    code=code, domain=ind["domaine_code"]
                )
            ind_count += 1
        print(f"Created {ind_count} Indicator nodes with relationships")

    # 4. IMF indicators
    imf_indicators = db.imf_weo.aggregate([
        {"$group": {
            "_id": "$code",
            "indicator": {"$first": "$indicator"},
            "unit": {"$first": "$unit"},
            "year_min": {"$min": "$year"},
            "year_max": {"$max": "$year"},
        }}
    ])
    imf_count = 0
    with neo4j_driver.session() as session:
        for ind in imf_indicators:
            code = ind.get("_id")
            if not code:
                continue
            session.run(
                "MERGE (i:Indicator {code: $code}) "
                "SET i.unit = $unit, i.label = $label, "
                "i.year_min = $ymin, i.year_max = $ymax, "
                "i.source = 'IMF-WEO'",
                code=code, unit=ind.get("unit"),
                label=ind.get("indicator"),
                ymin=ind.get("year_min"), ymax=ind.get("year_max")
            )
            session.run(
                "MERGE (s:Source {code: 'IMF-WEO'}) "
                "WITH s "
                "MATCH (i:Indicator {code: $code}) "
                "MERGE (i)-[:FROM_SOURCE]->(s)",
                code=code
            )
            imf_count += 1
        print(f"Created {imf_count} IMF Indicator nodes")

    print("Graph build complete")


# ── GraphQL Schema ───────────────────────────────────────────────────

@strawberry.type
class Indicator:
    code: str
    label: str | None = None
    unit: str | None = None
    obs_count: int | None = None
    source: str | None = None
    domain: str | None = None
    year_min: int | None = None
    year_max: int | None = None

@strawberry.type
class Source:
    code: str
    indicators: list[Indicator] | None = None

@strawberry.type
class Domain:
    code: str
    indicators: list[Indicator] | None = None

@strawberry.type
class Query:
    @strawberry.field
    def indicators(self, source: str | None = None, domain: str | None = None, limit: int = 50) -> list[Indicator]:
        with neo4j_driver.session() as session:
            query = "MATCH (i:Indicator)"
            params = {}
            if source and domain:
                query += "-[:FROM_SOURCE]->(:Source {code: $source})"
                query += ", "
            elif source:
                query += "-[:FROM_SOURCE]->(:Source {code: $source})"
            if domain and source:
                query += "(i)-[:BELONGS_TO]->(:Domain {code: $domain})"
            elif domain:
                query += "-[:BELONGS_TO]->(:Domain {code: $domain})"
            if source:
                params["source"] = source
            if domain:
                params["domain"] = domain
            query += " RETURN i.code, i.label, i.unit, i.obs_count, i.year_min, i.year_max "
            query += f"LIMIT {limit}"
            result = session.run(query, **params)
            return [
                Indicator(
                    code=rec["i.code"],
                    label=rec.get("i.label"),
                    unit=rec.get("i.unit"),
                    obs_count=rec.get("i.obs_count"),
                    year_min=rec.get("i.year_min"),
                    year_max=rec.get("i.year_max"),
                )
                for rec in result
            ]

    @strawberry.field
    def indicator(self, code: str) -> Indicator | None:
        with neo4j_driver.session() as session:
            result = session.run(
                "MATCH (i:Indicator {code: $code}) "
                "OPTIONAL MATCH (i)-[:FROM_SOURCE]->(s:Source) "
                "OPTIONAL MATCH (i)-[:BELONGS_TO]->(d:Domain) "
                "RETURN i, s.code AS source, d.code AS domain",
                code=code
            )
            row = result.single()
            if row:
                n = row["i"]
                return Indicator(
                    code=n["code"],
                    label=n.get("label"),
                    unit=n.get("unit"),
                    obs_count=n.get("obs_count"),
                    source=row.get("source"),
                    domain=row.get("domain"),
                    year_min=n.get("year_min"),
                    year_max=n.get("year_max"),
                )
            return None

    @strawberry.field
    def sources(self) -> list[Source]:
        with neo4j_driver.session() as session:
            result = session.run(
                "MATCH (s:Source) "
                "OPTIONAL MATCH (s)<-[:FROM_SOURCE]-(i:Indicator) "
                "RETURN s.code AS code, COLLECT(DISTINCT i.code) AS indicators "
                "ORDER BY code"
            )
            return [
                Source(code=rec["code"]) for rec in result
            ]

    @strawberry.field
    def domains(self) -> list[Domain]:
        with neo4j_driver.session() as session:
            result = session.run(
                "MATCH (d:Domain) RETURN d.code AS code ORDER BY code"
            )
            return [Domain(code=rec["code"]) for rec in result]

    @strawberry.field
    def graph_stats(self) -> str:
        with neo4j_driver.session() as session:
            nodes = session.run("MATCH (n) RETURN count(n) AS c").single()["c"]
            rels = session.run("MATCH ()-[r]->() RETURN count(r) AS c").single()["c"]
            return f"Graph: {nodes} nodes, {rels} relationships"


# ── FastAPI App ──────────────────────────────────────────────────────

schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)

app = FastAPI(title="RASD-Maroc Graph API", version="1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(graphql_app, prefix="/graphql")


@app.get("/")
def root():
    return {
        "name": "RASD-Maroc Graph API",
        "endpoints": {
            "GET /": "This info",
            "GET /build": "Build/rebuild Neo4j graph from MongoDB",
            "GET /graphql": "GraphQL playground",
            "POST /graphql": "GraphQL endpoint",
        },
    }


@app.get("/build")
def build():
    build_graph()
    return {"status": "Graph rebuilt from MongoDB"}


@app.on_event("startup")
def startup():
    # Check Neo4j connection
    try:
        with neo4j_driver.session() as session:
            session.run("RETURN 1")
        print(f"Neo4j connected: {NEO4J_URI}")
    except Exception as e:
        print(f"WARNING: Neo4j unavailable: {e}")
    # Check MongoDB
    try:
        mongo_client.admin.command("ping")
        print(f"MongoDB connected: {MONGODB_URI}")
    except Exception as e:
        print(f"WARNING: MongoDB unavailable: {e}")
    # Auto-build graph
    try:
        build_graph()
    except Exception as e:
        print(f"WARNING: Graph build failed: {e}")


@app.on_event("shutdown")
def shutdown():
    neo4j_driver.close()
    mongo_client.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
