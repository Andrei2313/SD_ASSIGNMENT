from flask import Flask, request, render_template
from config import ROOT_DIRECTORY
from database import PostgresDBConnector
from crawler import FileCrawler
from search import TextFileSearch, parse_advanced_query
from observer import SearchObserver, SearchLogger, get_recent_searches

app = Flask(__name__)

HOST = 'localhost'
PORT = 5432
DBNAME = 'SearchEngine'
USER = 'postgres'
PASSWORD = 'Andrei2313'

db_connector = PostgresDBConnector(HOST, PORT, DBNAME, USER, PASSWORD)
db_connector.connect()

db_connector.execute_query("""
CREATE TABLE IF NOT EXISTS text_files (
  id SERIAL PRIMARY KEY,
  filename VARCHAR(255) NOT NULL,
  filepath TEXT UNIQUE NOT NULL,
  extension VARCHAR(16),
  content TEXT,
  ranking_score DOUBLE PRECISION DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")
db_connector.execute_query("""
CREATE TABLE IF NOT EXISTS search_history (
  id SERIAL PRIMARY KEY,
  query_text TEXT NOT NULL,
  search_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

crawler = FileCrawler(db_connector, ROOT_DIRECTORY)
crawler.index_all_files()

searcher = TextFileSearch(db_connector)
search_subject = SearchObserver()
search_subject.observers = []
search_subject.attach = lambda obs: search_subject.observers.append(obs)
search_subject.notify = lambda q: [o.update(q) for o in search_subject.observers]

logger = SearchLogger(db_connector)
search_subject.attach(logger)

@app.route('/')
def home():
    suggestions = get_recent_searches(db_connector)
    return render_template('home.html', suggestions=suggestions)

@app.route('/search')
def search_route():
    q = request.args.get('q', '').strip()
    if q:
        quals = parse_advanced_query(q)
        name_q = quals['name']
        content_q = quals['content']
        path_q = quals['path']
        ext_q = quals['ext']
        display = q
    else:
        name_q = request.args.get('name_query', '').strip()
        content_q = request.args.get('content_query', '').strip()
        ext_q = request.args.get('ext_query', '').strip()
        path_q = ''
        display = f"name:{name_q} content:{content_q} ext:{ext_q}"
    results = searcher.search(name_q, content_q, path_q, ext_q)
    search_subject.notify(display)
    suggestions = get_recent_searches(db_connector)
    return render_template('home.html', results=results, suggestions=suggestions)

@app.route('/view/<int:file_id>')
def view_file(file_id):
    file = searcher.get_file_by_id(file_id)
    if not file:
        return "File not found.", 404
    return render_template('view.html', file=file)

if __name__ == '__main__':
    try:
        app.run(debug=True)
    finally:
        db_connector.close()
