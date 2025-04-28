import os
from config import TEXT_EXTENSIONS, REPORT_FORMAT
from ranking import compute_ranking

class FileCrawler:
    def __init__(self, db_connector, root_directory):
        self.db = db_connector
        self.root = root_directory

    def index_all_files(self):
        count = 0
        report = []
        for root, _, files in os.walk(self.root):
            for fn in files:
                abs_path = os.path.abspath(os.path.join(root, fn))
                ext = os.path.splitext(fn)[1].lower()
                content = ''
                if ext in TEXT_EXTENSIONS:
                    try:
                        with open(abs_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                    except Exception as e:
                        print(f"Warning: could not read {abs_path}: {e}")
                score = compute_ranking(abs_path)
                self._upsert_file(fn, abs_path, ext, content, score)
                report.append((fn, ext, abs_path, score))
                count += 1
        print(f"Indexed {count} files.")
        if REPORT_FORMAT == 'detailed':
            for fn, ext, path, sc in report:
                print(f"{fn} ({ext}) @ {path} → {sc:.2f}")

    def _upsert_file(self, filename, filepath, extension, content, ranking_score):
        sql = """
        INSERT INTO text_files
          (filename, filepath, extension, content, ranking_score)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (filepath) DO UPDATE SET
          filename = EXCLUDED.filename,
          extension = EXCLUDED.extension,
          content = EXCLUDED.content,
          ranking_score = EXCLUDED.ranking_score,
          updated_at = CURRENT_TIMESTAMP;
        """
        self.db.execute_query(sql, (filename, filepath, extension, content, ranking_score))
