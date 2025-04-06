import os
import socket
import json
import time
from multiprocessing import Process

class FileSearchMaster:
    def __init__(self, workers_config):
        self.workers_config = workers_config
        self.workers = []
        self.cache = {}

    def start_workers(self):
        from worker import run_worker
        for config in self.workers_config:
            p = Process(target=run_worker, args=(config['port'], config['directory']))
            p.daemon = True
            p.start()
            self.workers.append(p)
            time.sleep(0.5)
        print("[Master] All workers started.")

    def stop_workers(self):
        print("[Master] Terminating worker processes...")
        for p in self.workers:
            p.terminate()
            p.join()
        print("[Master] All workers terminated.")

    def query_worker(self, host, port, query):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, port))
            s.sendall(query.encode('utf-8'))
            s.shutdown(socket.SHUT_WR)
            result_data = b""
            while True:
                data = s.recv(4096)
                if not data:
                    break
                result_data += data
            s.close()
            return json.loads(result_data.decode('utf-8'))
        except Exception as e:
            print(f"[Master] Error connecting to worker at {host}:{port} - {e}")
            return []

    def rank_results(self, query, results):
        query_lower = query.lower()
        def score(path):
            idx = path.lower().find(query_lower)
            return idx if idx != -1 else float('inf')
        unique_results = list(dict.fromkeys(results))
        sorted_results = sorted(unique_results, key=lambda x: (score(x), x))
        return sorted_results

    def search(self, query):
        if query in self.cache:
            return self.cache[query]
        results = []
        for config in self.workers_config:
            results.extend(self.query_worker('localhost', config['port'], query))
        ranked_results = self.rank_results(query, results)
        self.cache[query] = ranked_results
        return ranked_results

if __name__ == '__main__':
    workers_config = [
        {'directory': os.getcwd(), 'port': 5001},
        {'directory': os.path.join(os.getcwd(), "sample_dir"), 'port': 5002}
    ]
    master = FileSearchMaster(workers_config)
    master.start_workers()
    try:
        while True:
            query = input("Enter search query (or 'exit' to quit): ").strip()
            if query.lower() == 'exit':
                break
            results = master.search(query)
            print("\nSearch results:")
            if results:
                for r in results:
                    print(r)
            else:
                print("No matching files found.")
            print()
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        master.stop_workers()
