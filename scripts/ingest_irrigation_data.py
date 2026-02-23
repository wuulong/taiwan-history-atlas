import os
import sys

# Add scripts directory to path for portability
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config

DB_PATH = config.DB_PATH


# Add scripts directory to path for portability

import sqlite3
import json
import re

FILE_PATH = "tmp/agriculture_zhi_full.md"

def parse_irrigation_table():
    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Start parsing after the table header
    table_section = content.split("臺灣各屬陂圳表")[-1]
    
    # Counties to track
    counties = [
        "安平縣", "鳳山縣", "嘉義縣", "恆春縣", "臺灣縣", 
        "彰化縣", "雲林縣", "苗慄縣", "淡水縣", "新竹縣", "宜蘭縣"
    ]
    
    results = []
    current_county = "未知"
    
    # Regular expression for entries: Name: Description
    # Example: 琉公圳：一名金合川圳。乾隆間業戶郭錫琉築...
    entry_regex = re.compile(r"([^：\n]+)：([^：\n]+)")
    
    lines = table_section.split('\n')
    for line in lines:
        line = line.strip()
        if not line: continue
        
        # Check if it marks a new county
        found_county = False
        for c in counties:
            if line.startswith(c) and len(line) < 15: # It's a header like "安平縣參差陂"
                current_county = c
                # The first entry of a county header often includes the first item
                # e.g., "安平縣參差陂：在文賢里..."
                match = entry_regex.search(line)
                if match:
                    name = match.group(1).replace(current_county, "")
                    desc = match.group(2)
                    results.append({
                        "county": current_county,
                        "name": name,
                        "description": desc
                    })
                found_county = True
                break
        
        if not found_county:
            match = entry_regex.search(line)
            if match:
                results.append({
                    "county": current_county,
                    "name": match.group(1),
                    "description": match.group(2)
                })

    return results

def ingest_to_atlas():
    irrigation_data = parse_irrigation_table()
    print(f"Parsed {len(irrigation_data)} irrigation records.")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Summary of finding
    summary = f"從《農業志‧臺灣各屬陂圳表》中精煉出的全台水利設施清單，共收錄 {len(irrigation_data)} 處。包含陂圳名稱、所在地、開鑿者、水源及灌溉範圍。"
    
    cursor.execute("""
        INSERT INTO ai_knowledge_atlas (category, subject, scope_vol_id, data_payload, semantic_summary, version_tag)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        'Eco_System', 
        '全臺重要歷史陂圳清單', 
        27, # 農業志
        json.dumps(irrigation_data, ensure_ascii=False),
        summary,
        '2026-02-22-v1'
    ))
    
    conn.commit()
    conn.close()
    print("✅ 全臺水利陂圳模型已成功入庫。")

if __name__ == "__main__":
    ingest_to_atlas()
