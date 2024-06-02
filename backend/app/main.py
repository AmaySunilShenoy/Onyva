from fastapi import FastAPI
from redis import Redis
from neo4j import GraphDatabase
import pymongo
import pandas as pd

app = FastAPI()

# Connect to Redis
redis = Redis(host="redis", port=6379, decode_responses=True)

# Connect to MongoDB
mongo_client = pymongo.MongoClient("mongodb://mongodb:27017/")
# Replace "mydatabase" with your database name
mongo_db = mongo_client["mydatabase"]

# Connect to Neo4j
neo4j_uri = "neo4j://neo4j"
neo4j_auth = ("neo4j", "password")
driver = GraphDatabase.driver(neo4j_uri, auth=neo4j_auth)

def verify_neo4j_connection():
    try:
        with driver:
            driver.verify_connectivity()
            return True
    except Exception as e:
        print(f"Failed to connect to Neo4j: {e}")
        return False

# Load data
stops_df = pd.read_csv('/code/app/stops.csv')
stop_sequence_df = pd.read_csv('/code/app/stops_new.csv')

def create_stop_nodes(tx, stops):
    for stop in stops:
        tx.run(
            """
            CREATE (s:Stop {stop_id: $stop_id, stop_name: $stop_name, stop_lat: $stop_lat, stop_lon: $stop_lon})
            """,
            stop_id=stop['stop_id'],
            stop_name=stop['stop_name'],
            stop_lat=stop['stop_lat'],
            stop_lon=stop['stop_lon']
        )

def create_parent_station_relationships(tx, stops):
    for stop in stops:
        if stop['parent_station']:
            tx.run(
                """
                MATCH (a:Stop {stop_id: $stop_id})
                MATCH (b:Stop {stop_id: $parent_station})
                CREATE (a)-[:PARENT_STATION]->(b)
                """,
                stop_id=stop['stop_id'],
                parent_station=stop['parent_station']
            )

def create_next_stop_relations_batch(tx, batch):
    tx.run(
        """
        UNWIND $batch AS rel
        MATCH (a:Stop {stop_id: rel.current_stop_id})
        MATCH (b:Stop {stop_id: rel.next_stop_id})
        MERGE (a)-[:NEXT_STOP {route_id: rel.route_id, route_name: rel.route_name, route_type: rel.route_type}]->(b)
        """, batch=batch
    )

def process_relationships_in_batches(session, stop_sequence_df, batch_size=1000):
    batch = []
    total_batches = 0

    for _, row in stop_sequence_df.iterrows():
        stop_order_string = row['stop_order']
        stop_ids = stop_order_string.split(',')

        # Check if route_type is NaN and handle it
        if pd.isna(row['route_type']):
            print(f"Skipping row {row.name} due to NaN route_type")
            continue

        for i in range(len(stop_ids) - 1):
            batch.append({
                'current_stop_id': stop_ids[i],
                'next_stop_id': stop_ids[i+1],
                'route_id': row['route_id'],
                'route_name': row['route_long_name'],
                'route_type': row['route_type']
            })

            if len(batch) >= batch_size:
                session.write_transaction(create_next_stop_relations_batch, batch)
                total_batches += 1
                print(f"Processed batch {total_batches}")
                batch = []

    if batch:
        session.write_transaction(create_next_stop_relations_batch, batch)
        total_batches += 1
        print(f"Processed final batch {total_batches}")


def initialize_database(stops_df, stop_sequence_df):
    with driver.session() as session:
        # Create indexes
        
        # session.run("CREATE INDEX FOR (s:Stop) ON (s.stop_id)")

        # Create nodes for each stop
        # session.write_transaction(create_stop_nodes, stops_df.to_dict('records'))
        # print('added nodes')

        # Create parent station relationships
        # session.write_transaction(create_parent_station_relationships, stops_df.to_dict('records'))
        print('added parent_station')

        # Process relationships in batches
        process_relationships_in_batches(session, stop_sequence_df, batch_size=1000)
        print('created next_stop relationships')

# API Endpoints
@app.get("/", tags=["Users"])
async def hello():
    return {"success": True}

@app.get("/create_neo4j_database")
async def init():
    try:
        initialize_database(stops_df, stop_sequence_df)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        driver.close()

if __name__ == "__main__":
    if verify_neo4j_connection():
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        print("Exiting due to Neo4j connection failure.")
