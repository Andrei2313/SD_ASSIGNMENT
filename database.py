import psycopg2

class PostgresDBConnector:
    def __init__(self, host, port, dbname, user, password):
        self.params = {
            'host': host, 'port': port,
            'dbname': dbname, 'user': user,
            'password': password
        }
        self.conn = None

    def connect(self):
        try:
            self.conn = psycopg2.connect(**self.params)
            print("Connected to Postgres.")
        except Exception as e:
            print("Error connecting to DB:", e)
            raise SystemExit(1)

    def execute_query(self, query, params=None):
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, params)
                self.conn.commit()
        except Exception as e:
            print("Error executing query:", e)
            if self.conn:
                self.conn.rollback()

    def fetch_query(self, query, params=None):
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchall()
        except Exception as e:
            print("Error fetching data:", e)
            if self.conn:
                self.conn.rollback()
            return []

    def close(self):
        if self.conn:
            self.conn.close()

            print("DB connection closed.")
