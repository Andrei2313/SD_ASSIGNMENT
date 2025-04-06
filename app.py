from flask import Flask, render_template, request, redirect, url_for
import os
from master import FileSearchMaster

app = Flask(__name__)

workers_config = [
    {'directory': os.getcwd(), 'port': 5001},
    {'directory': os.path.join(os.getcwd(), "C:\\test"), 'port': 5002}

]
master = FileSearchMaster(workers_config)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query', '').strip()
    if not query:
        return redirect(url_for('index'))
    results = master.search(query)
    return render_template('results.html', query=query, results=results)

if __name__ == '__main__':
    master.start_workers()
    try:
        app.run(port=8000, debug=True)
    finally:
        master.stop_workers()
