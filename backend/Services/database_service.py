# Load data
from Database_Connection.Neo4j import Neo4jConnectionManager
import pandas as pd

# Create nodes for each stop (loaded from csv file)
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

# Create parent station relationships between parent and child stations
def create_parent_station_relationships(tx, stops):
    for stop in stops:
        if stop['parent_station']:
            tx.run(
                """
                MATCH (a:Stop {stop_id: $stop_id})
                MATCH (b:Stop {stop_id: $parent_station})
                CREATE (a)-[:PARENT_STATION {parent: $parent_station, child: $stop_id}]->(b)
                CREATE (b)-[:CHILD_STATION {parent: $parent_station, child: $stop_id}]->(a)
                """,
                stop_id=stop['stop_id'],
                parent_station=stop['parent_station']
            )

# Create next stop relationships between stops (using the stop sequence data from csv file)
def create_next_stop_relations_batch(tx, batch):
    tx.run(
        """
        UNWIND $batch AS rel
        MATCH (a:Stop {stop_id: rel.current_stop_id})
        MATCH (b:Stop {stop_id: rel.next_stop_id})
        MERGE (a)-[:NEXT_STOP {route_id: rel.route_id, route_name: rel.route_name, route_type: rel.route_type}]->(b)
        """, batch=batch
    )

# Process relationships in batches
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

# Initialize the database with stops and stop sequence data (and creating indexes)
def initialize_database(stops_df, stop_sequence_df):
    with Neo4jConnectionManager.get_session() as session:
        # Create indexes
        
        session.run("CREATE INDEX index_stop_id FOR (s:Stop) ON (s.stop_id)")
        session.run("CREATE INDEX index_stop_location FOR (s:Stop) ON (s.stop_lat, s.stop_lon)")
        session.run("CREATE INDEX index_next_stop FOR ()-[r:NEXT_STOP]-() ON (r.route_id)")
        # Create nodes for each stop
        session.write_transaction(create_stop_nodes, stops_df.to_dict('records'))
        print('added nodes')

        # Create parent station relationships
        session.write_transaction(create_parent_station_relationships, stops_df.to_dict('records'))
        print('added parent_station')

        # Process relationships in batches
        process_relationships_in_batches(session, stop_sequence_df, batch_size=1000)
        print('created next_stop relationships')

