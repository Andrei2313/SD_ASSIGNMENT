import os

REPORT_FORMAT = os.getenv('INDEX_REPORT_FORMAT', 'simple').lower()

TEXT_EXTENSIONS = {
    '.txt', '.md', '.py', '.java', '.c', '.cpp',
    '.html', '.js', '.css', '.json', '.xml', '.csv'
}

ROOT_DIRECTORY = r'C:\Games\lab_mips'
