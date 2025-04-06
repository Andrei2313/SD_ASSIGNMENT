import os
import psycopg2
from flask import Flask, request, render_template_string

class PostgresDBConnector:
    def __init__(self, host, port, dbname, user, password):
        self.host = host
        self.port = port
        self.dbname = dbname
        self.user = user
        self.password = password
        self.conn = None

    def connect(self):
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                dbname=self.dbname,
                user=self.user,
                password=self.password
            )
            print("Connected to Postgres.")
        except Exception as e:
            print("Error connecting to DB:", e)

    def execute_query(self, query, params=None):
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, params)
                self.conn.commit()
        except Exception as e:
            print("Error executing query:", e)
            self.conn.rollback()

    def fetch_query(self, query, params=None):
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchall()
        except Exception as e:
            print("Error fetching data:", e)
            return []

    def close(self):
        if self.conn:
            self.conn.close()
            print("DB connection closed.")

class FileCrawler:
    def __init__(self, db_connector, root_directory):
        self.db_connector = db_connector
        self.root_directory = root_directory

    def index_text_files(self):
        count = 0
        for root, _, files in os.walk(self.root_directory):
            for file in files:
                if file.lower().endswith('.txt'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        self._store_file(file, file_path, content)
                        count += 1
                    except Exception as e:
                        print(f"Error processing file {file_path}: {e}")
        print(f"Indexing complete. Processed {count} text files.")

    def _store_file(self, filename, filepath, content):
        insert_sql = """
        INSERT INTO text_files (filename, filepath, content)
        VALUES (%s, %s, %s)
        ON CONFLICT (filepath) DO UPDATE SET
            filename = EXCLUDED.filename,
            content = EXCLUDED.content,
            updated_at = CURRENT_TIMESTAMP;
        """
        try:
            self.db_connector.execute_query(insert_sql, (filename, filepath, content))
            print(f"Indexed: {filepath}")
        except Exception as e:
            print(f"Error inserting {filepath}: {e}")

class TextFileSearch:
    def __init__(self, db_connector):
        self.db_connector = db_connector

    def search(self, name_query="", content_query=""):
        query = "SELECT id, filename, filepath, content FROM text_files WHERE 1=1"
        params = []
        if name_query:
            query += " AND filename ILIKE %s"
            params.append(f"%{name_query}%")
        if content_query:
            query += " AND content ILIKE %s"
            params.append(f"%{content_query}%")
        query += " ORDER BY filename;"
        return self.db_connector.fetch_query(query, tuple(params))

    def get_file_by_id(self, file_id):
        query = "SELECT id, filename, filepath, content FROM text_files WHERE id = %s"
        result = self.db_connector.fetch_query(query, (file_id,))
        return result[0] if result else None

app = Flask(__name__)

HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Text File Searcher</title>
  </head>
  <body>
    <h1>Search .txt Files</h1>
    <form method="get" action="/search">
      <div>
        <label for="name_query">Search by File Name:</label>
        <input type="text" id="name_query" name="name_query">
      </div>
      <div>
        <label for="content_query">Search by Content:</label>
        <input type="text" id="content_query" name="content_query">
      </div>
      <div>
        <button type="submit">Search</button>
      </div>
    </form>
    {% if results is defined %}
      <h2>Results:</h2>
      {% if results %}
      <ul>
        {% for file in results %}
          <li>
            <strong>{{ file[1] }}</strong> ({{ file[2] }})<br>
            <pre>{{ file[3][:200] }}{% if file[3]|length > 200 %}...{% endif %}</pre>
            <a href="/view/{{ file[0] }}">View Full Content</a>
          </li>
        {% endfor %}
      </ul>
      {% else %}
        <p>No matching files found.</p>
      {% endif %}
    {% endif %}
  </body>
</html>
"""

VIEW_TEMPLATE = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>{{ file[1] }}</title>
  </head>
  <body>
    <h1>{{ file[1] }}</h1>
    <p><strong>Path:</strong> {{ file[2] }}</p>
    <pre>{{ file[3] }}</pre>
    <p><a href="/">Back to Search</a></p>
  </body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/search')
def search():
    name_query = request.args.get("name_query", "")
    content_query = request.args.get("content_query", "")
    results = searcher.search(name_query, content_query)
    return render_template_string(HTML_TEMPLATE, results=results)

@app.route('/view/<int:file_id>')
def view_file(file_id):
    file = searcher.get_file_by_id(file_id)
    if file:
        return render_template_string(VIEW_TEMPLATE, file=file)
    return "File not found.", 404

if __name__ == '__main__':
    HOST = 'localhost'
    PORT = 5432
    DBNAME = 'SearchEngine'
    USER = 'postgres'
    PASSWORD = 'Andrei2313'

    db_connector = PostgresDBConnector(HOST, PORT, DBNAME, USER, PASSWORD)
    db_connector.connect()

    create_table_sql = """
    CREATE TABLE IF NOT EXISTS text_files (
        id SERIAL PRIMARY KEY,
        filename VARCHAR(255) NOT NULL,
        filepath TEXT UNIQUE NOT NULL,
        content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    db_connector.execute_query(create_table_sql)

    ROOT_DIRECTORY = r"C:\test"
    crawler = FileCrawler(db_connector, ROOT_DIRECTORY)
    crawler.index_text_files()

    searcher = TextFileSearch(db_connector)
    app.run(debug=True)

    db_connector.close()
