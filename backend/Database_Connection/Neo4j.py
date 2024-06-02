from neo4j import GraphDatabase

class Neo4jConnectionManager:
    _driver = None

    @staticmethod
    def connect(uri="neo4j://neo4j", user="neo4j", password="password"):
        if Neo4jConnectionManager._driver is None:
            Neo4jConnectionManager._driver = GraphDatabase.driver(uri, auth=(user, password))
        return Neo4jConnectionManager._driver

    @staticmethod
    def verify_connection():
        driver = Neo4jConnectionManager.connect()
        try:
            with driver.session() as session:
                session.run("RETURN 1")
            return True
        except Exception as e:
            print(f"Failed to connect to Neo4j: {e}")
            return False

    @staticmethod
    def close():
        if Neo4jConnectionManager._driver is not None:
            Neo4jConnectionManager._driver.close()
            Neo4jConnectionManager._driver = None
    # session
    @staticmethod
    def get_session():
        if Neo4jConnectionManager._driver is None:
            raise Exception("Driver not initialized!")
        return Neo4jConnectionManager._driver.session()