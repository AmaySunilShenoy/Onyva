from Database_Connection.Neo4j import Neo4jConnectionManager

# Main function to find the path between two stops
def find_path_between_stops(start: str, end: str, time: str):
    # Check if the time is between 00:00:00 and 05:00:00 to determine if it should only use night buses
    if time >= "00:00:00" and time <= "05:00:00":
        time = "(r.route_type = 'Night Bus' OR r.parent IS NOT NULL) AND "

    # If the time is not between 00:00:00 and 05:00:00, use all routes except night buses
    else:
        time = "(r.route_type <> 'Night Bus' OR r.parent IS NOT NULL) AND "

    # Query to find the path between two stops
    query = f"""
            MATCH (startNode:Stop {{stop_id: $start}}), (endNode:Stop {{stop_id: $end}})
            CALL {{
                WITH startNode
                OPTIONAL MATCH (startNode)-[startRoute : NEXT_STOP]-()
                RETURN startRoute.route_id as routes
                UNION
                WITH endNode
                OPTIONAL MATCH (endNode)-[endRoute : NEXT_STOP]-()
                RETURN endRoute.route_id as routes
            }}
            WITH startNode, endNode, COLLECT(routes) AS allRoutes
            OPTIONAL MATCH path = SHORTESTPATH ((startNode)-[*]-(endNode))
            WHERE ALL(r IN RELATIONSHIPS(path) WHERE {time} (r.route_id IN allRoutes OR r.parent IS NOT NULL))

            WITH startNode, endNode, path, LENGTH(path) AS nbstations, allRoutes

            OPTIONAL MATCH temppath2 = SHORTESTPATH ((startNode)-[*]-(endNode))
            WHERE ALL(r in relationships(temppath2) WHERE {time} (r.route_id IS NOT NULL OR r.parent IS NOT NULL))
            UNWIND relationships(temppath2) AS allRoutesAlt

            WITH DISTINCT allRoutesAlt.route_id AS correspondance, startNode, endNode, allRoutes, path, nbstations, allRoutesAlt

            OPTIONAL MATCH path2 = SHORTESTPATH ((startNode)-[*]-(endNode))
            WHERE ALL(r IN RELATIONSHIPS(path2) WHERE {time} (r.route_id IN allRoutes OR r.route_id = correspondance OR r.parent IS NOT NULL))
            WITH path2, LENGTH(path2) AS nbstations2, path, nbstations, allRoutes, allRoutesAlt
            ORDER BY nbstations2
            LIMIT 1

            WITH path, nbstations, path2, nbstations2, allRoutes, allRoutesAlt,
            CASE
                WHEN nbstations <= nbstations2 + 5 THEN path
                ELSE path2
            END AS finalPath
            RETURN finalPath, allRoutes
            """
    try:
        # Dictionary to store the time taken for each type of transport
        time_transport = {'Metro': 1, 'RER': 3, 'Tram': 2, 'Bus': 3, 'Night Bus': 3}

        # Get the session and run the query
        with Neo4jConnectionManager.get_session() as session:
            result = session.run(
                query,
                start=start,
                end=end,
                time=time,
                routing_="r",
            )
            # If the result is empty, return None
            if result.peek() is None:
                return None
            
            # Interleave the nodes and relationships to get the path
            interleaved_list = []

            # Initialize journey time
            journey_time = 0

            # Loop through the result and get the path
            for record in result:
                path = record['finalPath']
                if path is None:
                    return None
                nodes = path.nodes
                relationships = path.relationships

                # Loop through the nodes and relationships to get the path
                for i in range(max(len(nodes), len(relationships))):
                    if i < len(nodes):
                        if i < len(relationships):
                            nodes_attributes =['stop_id', 'stop_name', 'stop_lat', 'stop_lon']
                            if relationships[i]['route_id']:
                                relationships_attributes = ['route_id', 'route_name', 'route_type']
                                journey_time += time_transport[relationships[i]['route_type']]
                            else:
                                relationships_attributes = ['parent', 'child']
                                journey_time += 5

                            # Interleave the nodes and relationships
                            path_info = {
                                "stop": {nodes_attributes[j]: nodes[i][nodes_attributes[j]] for j in range(len(nodes_attributes))},
                                "route": {relationships_attributes[j]: relationships[i][relationships_attributes[j]] for j in range(len(relationships_attributes))}
                            }

                        else:
                            path_info = {
                                "stop": {nodes_attributes[j]: nodes[i][nodes_attributes[j]] for j in range(len(nodes_attributes))},
                                "route": {relationships_attributes[j]: relationships[i-1][relationships_attributes[j]] for j in range(len(relationships_attributes))}
                            }
                        interleaved_list.append(path_info)

            return interleaved_list, journey_time

    except Exception as e:
        print(f"Failed to find path: {e}")
        return None

# Function to find the closest stops to a given latitude and longitude
def find_closest_stops(lat: float, lon: float):
    with Neo4jConnectionManager.get_session() as session:

        # Query to find the 5 closest stops to the given latitude and longitude
        result = session.run(
            """
                MATCH (s:Stop)
                WITH s, point.distance(point({latitude: $lat, longitude: $lon}), point({latitude: s.stop_lat, longitude: s.stop_lon})) AS distance
                ORDER BY distance
                RETURN s, distance
                LIMIT 5
                """,
            lat=lat,
            lon=lon
        )
        stops = []
        # Loop through the result and get the stops
        for record in result:
            stop = {"stop_id": record[0]['stop_id'], "stop_name": record[0]['stop_name'],
                    "stop_lat": record[0]['stop_lat'], "stop_lon": record[0]['stop_lon']}
            stop['distance'] = record[1]
            stops.append(stop)

        # return the stops with their properties
        return stops
