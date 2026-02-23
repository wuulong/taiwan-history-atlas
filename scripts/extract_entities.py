import os
import sys

# Add scripts directory to path for portability
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config

DB_PATH = config.DB_PATH

import sqlite3
import re

# Add scripts directory to path for portability


ERA_BASE = {
    "康熙": 1661,
    "雍正": 1722,
    "乾隆": 1735,
    "嘉慶": 1795,
    "道光": 1820,
    "咸豐": 1850,
    "同治": 1861,
    "光緒": 1874,
    "宣統": 1908
}

def convert_year(era_name, year_num_str):
    if year_num_str == "元" or year_num_str == "初":
        year_num = 1
    else:
        mapping = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}
        if len(year_num_str) == 1:
            year_num = mapping.get(year_num_str, 0)
        elif len(year_num_str) == 2:
            if year_num_str[0] == "十":
                year_num = 10 + mapping.get(year_num_str[1], 0)
            elif year_num_str[1] == "十":
                year_num = mapping.get(year_num_str[0], 0) * 10
        elif len(year_num_str) == 3:
             year_num = mapping.get(year_num_str[0], 0) * 10 + mapping.get(year_num_str[2], 0)
        else:
            year_num = 0
            
    if era_name in ERA_BASE and year_num > 0:
        return ERA_BASE[era_name] + year_num
    return None


def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all volumes
    cursor.execute("SELECT id, title FROM volumes")
    volumes = cursor.fetchall()
    
    print(f"Starting expanded extraction for {len(volumes)} volumes...")
    
    for vol_id, vol_title in volumes:
        cursor.execute("SELECT id, raw_text FROM contents WHERE vol_id = ?", (vol_id,))
        rows = cursor.fetchall()
        
        if not rows: continue
        print(f" - Volume {vol_id}: {vol_title} ({len(rows)} lines)")
        
        for c_id, text in rows:
            # 1. Chronology Extraction (Universal)
            d_matches = re.finditer(r"(康熙|雍正|乾隆|嘉慶|道光|咸豐|同治|光緒|宣統)([一二三四五六七八九十元初\d]+)年", text)
            for m in d_matches:
                era = m.group(1)
                y_str = m.group(2)
                ad = convert_year(era, y_str)
                if ad:
                    cursor.execute("INSERT OR REPLACE INTO chronology (content_id, year_ad, year_era, event_summary) VALUES (?, ?, ?, ?)",
                                   (c_id, ad, era + y_str + "年", f"[{vol_title}] " + text[:80] + "..."))

            # 2. People Extraction
            # Pattern A: Sentence start (Pioneers)
            p_matches = re.finditer(r"^([\u4e00-\u9fa5]{2,4})(?:，|者|字|人)", text)
            for p in p_matches:
                p_name = p.group(1)
                if len(p_name) >= 2:
                    cursor.execute("INSERT OR IGNORE INTO entities (name, type) VALUES (?, ?)", (p_name, "Person"))
                    cursor.execute("SELECT id FROM entities WHERE name = ?", (p_name,))
                    ent_id = cursor.fetchone()[0]
                    cursor.execute("INSERT INTO mentions (entity_id, content_id, snippet, confidence) VALUES (?, ?, ?, ?)",
                                   (ent_id, c_id, text[:150], 0.8))


            # 3. Location Extraction
            # Keywords: 莊, 社, 街, 庄, 堡, 里, 廳, 縣
            l_matches = re.finditer(r"([\u4e00-\u9fa5]{2,6})(?:莊|社|街|庄|附近|等地|等庄|堡|里)", text)
            for l in l_matches:
                loc_name = l.group(0) # Use the whole match to include the suffix
                if len(loc_name) >= 3 and not any(c in loc_name for c in "一二三四五六七八九十"):
                    cursor.execute("INSERT OR IGNORE INTO entities (name, type) VALUES (?, ?)", (loc_name, "Location"))
                    cursor.execute("SELECT id FROM entities WHERE name = ?", (loc_name,))
                    ent_id = cursor.fetchone()[0]
                    cursor.execute("INSERT INTO mentions (entity_id, content_id, snippet, confidence) VALUES (?, ?, ?, ?)",
                                   (ent_id, c_id, text[:150], 0.6))
            
            # 4. Infrastructure Extraction (Water/Walls/Forts)
            # Pattern: [地名] + (圳, 埤, 陂, 甽, 城, 砲臺, 水門)
            i_matches = re.finditer(r"([\u4e00-\u9fa5]{2,6}(?:圳|埤|陂|甽|埤圳|城|砲臺|水門))", text)
            for i in i_matches:
                infra_name = i.group(1)
                if len(infra_name) >= 3:
                    cursor.execute("INSERT OR IGNORE INTO entities (name, type) VALUES (?, ?)", (infra_name, "Infrastructure"))
                    cursor.execute("SELECT id FROM entities WHERE name = ?", (infra_name,))
                    ent_id = cursor.fetchone()[0]
                    cursor.execute("INSERT INTO mentions (entity_id, content_id, snippet, confidence) VALUES (?, ?, ?, ?)",
                                   (ent_id, c_id, text[:150], 0.8))

    conn.commit()
    conn.close()
    print("Expanded entity extraction completed.")

if __name__ == "__main__":
    main()
