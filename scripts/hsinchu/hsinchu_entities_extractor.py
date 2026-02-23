import sqlite3
import re
import os

DB_PATH = "/Users/wuulong/github/bmad-pa/data/history_texts/hsinchu_history.db"

def extract_entities():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id, title, doc_id FROM volumes")
    volumes = {r[0]: (r[1], r[2]) for r in cursor.fetchall()}

    cursor.execute("SELECT id, title FROM documents")
    docs = {r[0]: r[1] for r in cursor.fetchall()}

    cursor.execute("SELECT id, vol_id, raw_text FROM contents")
    contents = cursor.fetchall()

    print(f"Start extracting entities from {len(contents)} text fragments...")

    # Statistics
    stats = {"Infrastructure": 0, "Location": 0, "Irrigation": 0}

    for c_id, vol_id, text in contents:
        doc_id = volumes[vol_id][1]
        doc_title = docs[doc_id]

        def add_entity(name, e_type):
            if len(name) < 2 or len(name) > 10: return
            cursor.execute("INSERT OR IGNORE INTO entities (name, type) VALUES (?, ?)", (name, e_type))
            cursor.execute("SELECT id FROM entities WHERE name = ?", (name,))
            ent_id = cursor.fetchone()[0]
            cursor.execute("INSERT INTO mentions (entity_id, content_id, snippet, confidence) VALUES (?, ?, ?, ?)",
                           (ent_id, c_id, text[:150], 0.8))
            stats[e_type] += 1

        # 3. 基礎建設 (Infrastructure: 橋, 道路, 城, 隘口等)
        # Matches ending with 橋, 崎, 嶺, 渡, 土城, 門, 隘
        i_matches = re.finditer(r"([\u4e00-\u9fa5]{2,6}(?:橋|崎|嶺|渡口|渡|土城|城門|隘))", text)
        for i in i_matches:
            add_entity(i.group(1), "Infrastructure")

        # 2. 空間與聚落 (Location: 堡, 庄, 莊, 街, 社, 坑, 壢)
        l_matches = re.finditer(r"([\u4e00-\u9fa5]{2,6}(?:堡|庄|莊|街|番社|社|坑|壢|窩))", text)
        for l in l_matches:
            loc = l.group(1)
            # Exclude false positives that are likely not places
            if not any(c in loc for c in "一二三四五六七八九十") and "者" not in loc and "之" not in loc:
                add_entity(loc, "Location")

        # 1. 水利開發史 (Irrigation: 圳, 埤, 陂, 潭, 水門)
        w_matches = re.finditer(r"([\u4e00-\u9fa5]{2,6}(?:圳|陂|埤|潭|水門))", text)
        for w in w_matches:
            add_entity(w.group(1), "Irrigation")

    conn.commit()
    conn.close()

    print("Extraction completed.")
    print(f"Stats: {stats}")

if __name__ == "__main__":
    if os.path.exists(DB_PATH):
        extract_entities()
    else:
        print("Database not found.")
