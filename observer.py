class SearchObserver:
    def update(self, query_text):
        pass

class SearchLogger(SearchObserver):
    def __init__(self, db_connector):
        self.db = db_connector

    def update(self, query_text):
        self.db.execute_query(
            "INSERT INTO search_history (query_text) VALUES (%s);",
            (query_text,)
        )


def get_recent_searches(db, limit=5):
    rows = db.fetch_query("""
      SELECT query_text
        FROM search_history
       GROUP BY query_text
       ORDER BY MAX(search_time) DESC
       LIMIT %s;
    """, (limit,))
    return [r[0] for r in rows]
