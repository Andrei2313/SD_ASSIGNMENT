import argparse
import socket
import os
import json

def search_files(query, base_dir):
    results = []
    query_lower = query.lower()
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            full_path = os.path.join(root, file)
            if query_lower in full_path.lower():
                results.append(full_path)
    return results

def run_worker(port, base_dir):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('localhost', port))
    s.listen(5)
    print(f"Worker started on port {port}, searching in directory: {base_dir}")
    while True:
        conn, addr = s.accept()
        with conn:
            data = b""
            while True:
                part = conn.recv(1024)
                if not part:
                    break
                data += part
            query = data.decode('utf-8').strip()
            print(f"Worker on port {port} received query: '{query}'")
            results = search_files(query, base_dir)
            response = json.dumps(results)
            conn.sendall(response.encode('utf-8'))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Worker for file search")
    parser.add_argument("--dir", required=True, help="Directory to search")
    parser.add_argument("--port", type=int, required=True, help="Port to listen on")
    args = parser.parse_args()
    run_worker(args.port, args.dir)
