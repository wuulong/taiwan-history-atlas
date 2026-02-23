import sqlite3
import os

def load_all_hsinchu_books(db_path, data_dir):
    books = [
        {
            "filename": "新竹縣採訪冊.txt",
            "title": "新竹縣採訪冊",
            "author": "陳培桂",
            "dynasty": "清",
            "category": "地方志",
            "description": "記載新竹地區之地理、人文、建設與物產。",
            "vol_pattern": r"^# 卷"
        },
        {
            "filename": "淡水廳志.txt",
            "title": "淡水廳志",
            "author": "陳培桂",
            "dynasty": "清",
            "category": "廳志",
            "description": "北台灣最重要的官方志書，記載淡水廳（含新竹）之全貌。",
            "vol_pattern": r"^# 淡水廳志卷"
        },
        {
            "filename": "樹杞林志.txt",
            "title": "樹杞林志",
            "author": "林百川、林學源",
            "dynasty": "清/日治",
            "category": "地方志",
            "description": "記載樹杞林（今竹東）地區之專門志書。",
            "vol_pattern": r"^=树杞林志="  # 樹杞林志較特殊，只有單一卷
        },
        {
            "filename": "新竹縣志初稿.txt",
            "title": "新竹縣志初稿",
            "author": "陳朝龍",
            "dynasty": "日治初期",
            "category": "地方志",
            "description": "日治初期延續清代架構編纂的新竹縣志草稿。",
            "vol_pattern": r"^# 卷"
        },
        {
            "filename": "新竹縣制度考.txt",
            "title": "新竹縣制度考",
            "author": "不詳",
            "dynasty": "清/日治",
            "category": "制度考",
            "description": "關於新竹縣行政制度、衙門組織與租稅的詳細考證。",
            "vol_pattern": r"^# 新竹縣制度考"
        }
    ]

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for book in books:
        text_path = os.path.join(data_dir, book["filename"])
        if not os.path.exists(text_path):
            print(f"Skipping: {book['filename']} (Not found)")
            continue

        # 1. Insert/Get Document
        cursor.execute("SELECT id FROM documents WHERE title = ?", (book["title"],))
        doc_row = cursor.fetchone()
        if not doc_row:
            cursor.execute("""
                INSERT INTO documents (title, author, dynasty, category, description)
                VALUES (?, ?, ?, ?, ?)
            """, (book["title"], book["author"], book["dynasty"], book["category"], book["description"]))
            doc_id = cursor.lastrowid
        else:
            doc_id = doc_row[0]
            # Clear existing data for this book to avoid duplicates on re-run
            cursor.execute("DELETE FROM contents WHERE vol_id IN (SELECT id FROM volumes WHERE doc_id = ?)", (doc_id,))
            cursor.execute("DELETE FROM volumes WHERE doc_id = ?", (doc_id,))

        # 2. Parse Text
        with open(text_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        current_vol_id = None
        # 對於只有單卷的書，先建立一個預設卷
        if book["title"] in ["樹杞林志", "新竹縣制度考"]:
             cursor.execute("INSERT INTO volumes (doc_id, vol_num_str, title) VALUES (?, ?, ?)", 
                            (doc_id, "全一卷", book["title"]))
             current_vol_id = cursor.lastrowid

        line_count = 0
        vol_count = 0 if current_vol_id is None else 1

        import re
        for i, line in enumerate(lines):
            line = line.strip()
            if not line: continue
            if line.startswith("=") or line.startswith("---") or line.startswith("來源:"): continue

            # Detect Volume Marker
            if re.match(book["vol_pattern"], line):
                vol_num = line.replace("#", "").strip()
                vol_title = "未知"
                # Look ahead for a title line
                for next_idx in range(i + 1, min(i + 5, len(lines))):
                    next_line = lines[next_idx].strip()
                    if next_line and not next_line.startswith("#") and len(next_line) < 20:
                        vol_title = next_line
                        break
                
                cursor.execute("INSERT INTO volumes (doc_id, vol_num_str, title) VALUES (?, ?, ?)", 
                               (doc_id, vol_num, vol_title))
                current_vol_id = cursor.lastrowid
                vol_count += 1
                continue

            if current_vol_id:
                cursor.execute("INSERT INTO contents (vol_id, line_num, raw_text) VALUES (?, ?, ?)", 
                               (current_vol_id, i + 1, line))
                line_count += 1

        print(f"Loaded: {book['title']} ({vol_count} vols, {line_count} lines)")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    DB_PATH = "/Users/wuulong/github/bmad-pa/data/history_texts/hsinchu_history.db"
    DATA_DIR = "/Users/wuulong/github/bmad-pa/data/history_texts"
    load_all_hsinchu_books(DB_PATH, DATA_DIR)
