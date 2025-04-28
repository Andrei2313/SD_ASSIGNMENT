class TextFileSearch:
    def __init__(self, db_connector):
        self.db = db_connector

    def search(self, name_q='', content_q='', path_q='', ext_q=''):
        sql = "SELECT id, filename, filepath FROM text_files WHERE TRUE"
        params = []
        if name_q:
            sql += " AND filename ILIKE %s"
            params.append(f"%{name_q}%")
        if content_q:
            sql += " AND content ILIKE %s"
            params.append(f"%{content_q}%")
        if path_q:
            sql += " AND filepath ILIKE %s"
            params.append(f"%{path_q}%")
        if ext_q:
            if not ext_q.startswith('.'):
                ext_q = '.' + ext_q
            sql += " AND extension = %s"
            params.append(ext_q.lower())
        sql += " ORDER BY ranking_score DESC;"
        return self.db.fetch_query(sql, tuple(params))

    def get_file_by_id(self, file_id):
        rows = self.db.fetch_query(
            "SELECT id, filename, filepath, content FROM text_files WHERE id = %s",
            (file_id,)
        )
        return rows[0] if rows else None


def parse_advanced_query(q):
    qualifiers = {'path': [], 'content': [], 'name': [], 'ext': []}
    for tok in q.split():
        if ':' in tok:
            key, val = tok.split(':', 1)
            if key in qualifiers:
                qualifiers[key].append(val)
            else:
                qualifiers['content'].append(tok)
        else:
            qualifiers['content'].append(tok)
    return {k: ' '.join(v) for k, v in qualifiers.items()}
