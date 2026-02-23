import sqlite3
import os
import re

def load_hsinchu_data(db_path, text_path):
    if not os.path.exists(text_path):
        print(f"Error: Text file not found at {text_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Insert Document
    doc_title = "新竹縣採訪冊"
    cursor.execute("SELECT id FROM documents WHERE title = ?", (doc_title,))
    doc_row = cursor.fetchone()
    if not doc_row:
        cursor.execute("""
            INSERT INTO documents (title, author, dynasty, category, description)
            VALUES (?, ?, ?, ?, ?)
        """, (doc_title, "陳培桂", "清", "地方志", "記載新竹地區之地理、人文、建設與物產。"))
        doc_id = cursor.lastrowid
    else:
        doc_id = doc_row[0]

    # 2. Parse Text and Insert Volumes & Contents
    with open(text_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    current_vol_id = None
    line_count = 0
    vol_count = 0

    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        # Detect Volume Marker: # 卷X
        if line.startswith("# 卷"):
            vol_num = line.replace("#", "").strip()
            # The next line is often the title or "目錄"
            vol_title = "未知"
            if i + 1 < len(lines):
                vol_title = lines[i+1].strip()
            
            cursor.execute("""
                INSERT INTO volumes (doc_id, vol_num_str, title)
                VALUES (?, ?, ?)
            """, (doc_id, vol_num, vol_title))
            current_vol_id = cursor.lastrowid
            vol_count += 1
            print(f"Adding Volume: {vol_num} - {vol_title}")
            continue

        if current_vol_id:
            # Skip the title line we just used
            if i > 0 and lines[i-1].strip().startswith("# 卷"):
                continue
                
            cursor.execute("""
                INSERT INTO contents (vol_id, line_num, raw_text)
                VALUES (?, ?, ?)
            """, (current_vol_id, i + 1, line))
            line_count += 1

    conn.commit()
    conn.close()
    print(f"Successfully loaded {vol_count} volumes and {line_count} content lines into {db_path}.")

if __name__ == "__main__":
    DB_PATH = "/Users/wuulong/github/bmad-pa/data/history_texts/hsinchu_history.db"
    TEXT_PATH = "/Users/wuulong/github/bmad-pa/data/history_texts/新竹縣採訪冊.txt"
    load_hsinchu_data(DB_PATH, TEXT_PATH)
