from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "adminadmin"))


class Neo4jUser:
    @staticmethod
    def create_user(username, password, email):
        with driver.session() as session:
            session.run(
                "CREATE (u:User {username: $username, password: $password, email: $email})",
                username=username, password=password, email=email
            )
