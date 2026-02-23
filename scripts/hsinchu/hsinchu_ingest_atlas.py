import sqlite3
import json
import os
from datetime import datetime

# Configuration
HSINCHU_DB_PATH = '/Users/wuulong/github/bmad-pa/data/history_texts/hsinchu_history.db'
ATLAS_DB_PATH = '/Users/wuulong/github/bmad-pa/data/history_texts/history_atlas.db'
SOURCE_ORIGIN = 'Hsinchu'

def compile_and_ingest_atlas(category, subject, entity_type, summary_desc):
    if not os.path.exists(HSINCHU_DB_PATH) or not os.path.exists(ATLAS_DB_PATH):
        print("Error: Database files not found.")
        return

    # 1. Gather Data from Hsinchu DB
    h_conn = sqlite3.connect(HSINCHU_DB_PATH)
    h_cursor = h_conn.cursor()
    
    # We want entities that have spatial links
    h_cursor.execute("""
        SELECT e.name, s.longitude, s.latitude, s.accuracy, s.meta_data, COUNT(m.id) as mentions_count
        FROM entities e
        JOIN spatial_links s ON e.id = s.entity_id
        LEFT JOIN mentions m ON e.id = m.entity_id
        WHERE e.type = ?
        GROUP BY e.id
        ORDER BY mentions_count DESC
    """, (entity_type,))
    
    records = h_cursor.fetchall()
    
    data_payload = []
    for r in records:
        name, lon, lat, accuracy, meta, m_count = r
        try:
             meta_json = json.loads(meta) if meta else {}
        except:
             meta_json = {}
             
        data_payload.append({
            "name": name,
            "longitude": lon,
            "latitude": lat,
            "accuracy": accuracy,
            "meta_data": meta_json,
            "mentions_count": m_count
        })
        
    h_conn.close()
    
    if not data_payload:
        print(f"No spatial data found for type: {entity_type}. Skipping ingest.")
        return

    # 2. Ingest to Atlas DB
    a_conn = sqlite3.connect(ATLAS_DB_PATH)
    a_cursor = a_conn.cursor()
    
    version_tag = "Hsinchu-v2.0"
    author_agent = "Antigravity HGIS Architect"
    full_summary = f"{summary_desc}。共收錄 {len(data_payload)} 處具備座標之地理實體。"
    
    # Check if exists
    a_cursor.execute("""
        SELECT id FROM knowledge_atlas 
        WHERE source_origin = ? AND category = ? AND subject = ?
    """, (SOURCE_ORIGIN, category, subject))
    
    row = a_cursor.fetchone()
    if row:
        a_cursor.execute("""
            UPDATE knowledge_atlas 
            SET data_payload = ?, semantic_summary = ?, tags = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (json.dumps(data_payload, ensure_ascii=False), full_summary, version_tag, row[0]))
        print(f"Updated L2 Atlas Record: {subject} ({len(data_payload)} entities)")
    else:
        a_cursor.execute("""
            INSERT INTO knowledge_atlas (source_origin, source_db_path, category, subject, data_payload, semantic_summary, tags, author_agent)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (SOURCE_ORIGIN, HSINCHU_DB_PATH, category, subject, json.dumps(data_payload, ensure_ascii=False), full_summary, version_tag, author_agent))
        print(f"Inserted L2 Atlas Record: {subject} ({len(data_payload)} entities)")

    a_conn.commit()
    a_conn.close()

if __name__ == "__main__":
    compile_and_ingest_atlas("Eco_System", "竹塹歷史水利開發網", "Irrigation", "整合《新竹縣採訪冊》等五書所紀錄之陂圳與水門分布")
    compile_and_ingest_atlas("Infrastructure", "竹塹歷史交通與防禦網", "Infrastructure", "整合新竹地區清代與日治初期之城門、隘口、橋梁及古道點位")
    compile_and_ingest_atlas("Location", "竹塹歷史聚落空間分佈", "Location", "整合新竹五書內提及之歷史聚落、堡庄與番社點位")
    print("✅ Hsinchu Layer 2 Atlas Ingestion Completed.")
