import os
import sys

# Add scripts directory to path for portability
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config

DB_PATH = config.DB_PATH

import sqlite3
import re


def init_db(conn):
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS contents_fts")
    cursor.execute("DROP TABLE IF EXISTS mentions")
    cursor.execute("DROP TABLE IF EXISTS spatial_links")
    cursor.execute("DROP TABLE IF EXISTS chronology")
    cursor.execute("DROP TABLE IF EXISTS contents")
    cursor.execute("DROP TABLE IF EXISTS entities")
    cursor.execute("DROP TABLE IF EXISTS volumes")

    cursor.execute("""
    CREATE TABLE volumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vol_num_str TEXT,     -- 卷一, 卷二
        title TEXT,           -- 開闢紀, 貨殖列傳
        category TEXT,        -- 紀/志/傳/序
        summary TEXT,
        meta_data TEXT        -- JSON metadata
    )""")

    cursor.execute("""
    CREATE TABLE contents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vol_id INTEGER,
        line_num INTEGER,
        sub_title TEXT,
        raw_text TEXT,
        meta_data TEXT,       -- JSON metadata
        FOREIGN KEY(vol_id) REFERENCES volumes(id)
    )""")

    cursor.execute("""
    CREATE VIRTUAL TABLE contents_fts USING fts5(
        raw_text, 
        content='contents', 
        content_rowid='id'
    )""")

    cursor.execute("CREATE TABLE entities (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, type TEXT, description TEXT, meta_data TEXT)")
    cursor.execute("CREATE TABLE mentions (id INTEGER PRIMARY KEY AUTOINCREMENT, entity_id INTEGER, content_id INTEGER, snippet TEXT, confidence REAL, meta_data TEXT, FOREIGN KEY(entity_id) REFERENCES entities(id), FOREIGN KEY(content_id) REFERENCES contents(id))")
    cursor.execute("CREATE TABLE spatial_links (id INTEGER PRIMARY KEY AUTOINCREMENT, entity_id INTEGER, longitude REAL, latitude REAL, accuracy TEXT, dtm_elevation REAL, meta_data TEXT, FOREIGN KEY(entity_id) REFERENCES entities(id))")
    cursor.execute("CREATE TABLE chronology (id INTEGER PRIMARY KEY AUTOINCREMENT, content_id INTEGER, year_ad INTEGER, year_era TEXT, event_summary TEXT, meta_data TEXT, FOREIGN KEY(content_id) REFERENCES contents(id))")
    
    conn.commit()

def get_category(title):
    if not title: return "其他"
    if "紀" in title: return "紀"
    if "志" in title: return "志"
    if "列傳" in title or "傳" in title: return "傳"
    return "其他"

def import_text(conn):
    cursor = conn.cursor()
    
    with open(TXT_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    toc_map = {}
    # Increased range for TOC parsing just in case
    toc_regex = re.compile(r"^(卷[一二三四五六七八九十]+)(.+)$")
    for line in lines[:340]:
        match = toc_regex.match(line.strip())
        if match:
            # Clean title: strip extra colons or spaces
            v_num = match.group(1).strip()
            v_title = match.group(2).strip().strip('：').strip()
            toc_map[v_num] = v_title
    
    print(f"Parsed TOC: {len(toc_map)} items found.")

    current_vol_id = None
    # Flexible regex: matches '# 史卷一' or '# 卷一' or '# 卷三十一'
    vol_marker_regex = re.compile(r"^#\s*(?:史)?\s*(卷[一二三四五六七八九十]+)$")
    current_sub_titles = []
    current_sub = None

    for i, line in enumerate(lines):
        line = line.strip()
        if not line: continue
        
        match = vol_marker_regex.match(line)
        if match:
            vol_num_str = match.group(1).strip()
            vol_title = toc_map.get(vol_num_str, "未知章節")
            category = get_category(vol_title)
            
            cursor.execute("INSERT INTO volumes (vol_num_str, title, category) VALUES (?, ?, ?)", 
                           (vol_num_str, vol_title, category))
            current_vol_id = cursor.lastrowid
            
            # Reset sub-titles for new volume
            # Find sub-titles for this volume from TOC
            current_sub_titles = []
            found_vol = False
            for l in lines[4:335]: # TOC section
                l = l.strip()
                if not l: continue
                if l.startswith(vol_num_str):
                    found_vol = True
                    continue
                if found_vol:
                    if l.startswith("卷"): break # Next volume
                    current_sub_titles.append(l)
            
            current_sub = vol_title # Default
            print(f"Importing {vol_num_str} {vol_title}... ({len(current_sub_titles)} sub-sections)")
            continue
        
        if current_vol_id:
            # Check for sub-title match
            for st in current_sub_titles:
                pos = line.find(st)
                if 0 <= pos <= 50:
                    current_sub = st
                    break
                    
            cursor.execute("INSERT INTO contents (vol_id, line_num, sub_title, raw_text) VALUES (?, ?, ?, ?)",
                           (current_vol_id, i+1, current_sub, line))
    
    cursor.execute("INSERT INTO contents_fts(contents_fts) VALUES('rebuild')")
    conn.commit()

def main():
    if not os.path.exists(TXT_PATH):
        print(f"Error: {TXT_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    print("Initializing Database...")
    init_db(conn)
    print("Importing Text (Phase 1: Structural Import)...")
    import_text(conn)
    conn.close()
    print("Successfully built historical database.")

if __name__ == "__main__":
    main()
