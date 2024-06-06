from Database_Connection.Neo4j import Neo4jConnectionManager


def find_path_between_stops(start: str, end: str):
    try:
        with Neo4jConnectionManager.get_session() as session:
            result = session.run(
                """
                MATCH (startNode:Stop {stop_id:$start}), (endNode:Stop {stop_id:$end})
                    CALL  {
                        WITH startNode
                        OPTIONAL MATCH (startNode)-[startRoute : NEXT_STOP]-()
                        RETURN startRoute.route_id as routes
                        UNION
                        WITH endNode
                        OPTIONAL MATCH (endNode)-[endRoute : NEXT_STOP]-()
                        RETURN endRoute.route_id as routes
                    }
                    WITH startNode, endNode,  COLLECT(routes) AS allRoutes
                    OPTIONAL MATCH path = SHORTESTPATH ((startNode)-[*]-(endNode))
                    WHERE ALL(r IN RELATIONSHIPS(path) WHERE r.route_id IN allRoutes OR r.parent IS NOT NULL)

                    WITH startNode, endNode, path, LENGTH(path) AS nbstations, allRoutes

                    OPTIONAL MATCH temppath2 = SHORTESTPATH ((startNode)-[*]-(endNode))
                    UNWIND relationships(temppath2) AS allRoutesAlt

                    WITH DISTINCT allRoutesAlt.route_id AS correspondance, startNode, endNode, allRoutes, path, nbstations, allRoutesAlt

                    OPTIONAL MATCH path2 = SHORTESTPATH ((startNode)-[*]-(endNode))
                    WHERE ALL(r IN RELATIONSHIPS(path2) WHERE r.route_id IN allRoutes OR r.route_id = correspondance OR r.parent IS NOT NULL)
                    WITH path2, LENGTH(path2) AS nbstations2, path, nbstations, allRoutes, allRoutesAlt
                    ORDER BY nbstations2
                    LIMIT 1

                    WITH path, nbstations, path2, nbstations2,allRoutes, allRoutesAlt,
                    CASE
                        WHEN nbstations <= nbstations2 + 5 THEN  path
                        ELSE path2
                    END AS finalPath
                    RETURN finalPath, allRoutes
                """,
                start=start,
                end=end,
                routing_="r",
            )
            if result.peek() is None:
                return None
            interleaved_list = []
            for record in result:
                print('record', record)
                path = record['finalPath']
                allRoutes = record['allRoutes']
                nodes = path.nodes
                relationships = path.relationships
                print('node length', len(nodes))    
                print('relationship length', len(relationships))
                
                for i in range(max(len(nodes), len(relationships))):
                    if i < len(nodes):
                        if i < len(relationships):
                            path_info = {"stop": nodes[i], "route": relationships[i]}
                        else:
                            path_info = {"stop": nodes[i], "route": relationships[i-1]}
                        interleaved_list.append(path_info)
                return interleaved_list
    except Exception as e:
        print(f"Failed to find path: {e}")
        return None


def find_closest_stops(lat: float, lon: float):
        with Neo4jConnectionManager.get_session() as session:
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
            for record in result:
                stop = {"stop_id": record[0]['stop_id'], "stop_name": record[0]['stop_name'], "stop_lat": record[0]['stop_lat'], "stop_lon": record[0]['stop_lon']}
                stop['distance'] = record[1]
                stops.append(stop)
            return stops