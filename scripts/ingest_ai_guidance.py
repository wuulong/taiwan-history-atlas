import os
import sys

# Add scripts directory to path for portability
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config

DB_PATH = config.DB_PATH


# Add scripts directory to path for portability

import sqlite3
import json


def ingest_ai_guidance():
    # Synthetic meta-knowledge extracted from the task report
    guidance_data = {
        "database_navigation": {
            "core_tables": ["volumes", "contents", "entities", "mentions", "ai_knowledge_atlas"],
            "navigation_logic": "Use contents.sub_title (extracted from TOC) for precise section filtering.",
            "sql_example": "SELECT c.sub_title, e.name FROM entities e JOIN mentions m ON e.id = m.entity_id JOIN contents c ON m.content_id = c.id WHERE c.vol_id = 27 AND e.type = 'Person';"
        },
        "attribute_extraction": {
            "method": "Use json_extract on entities.meta_data.",
            "fields": ["summary", "geo_params", "spatial_ref"],
            "sql_example": "SELECT name, json_extract(meta_data, '$.summary') as brief FROM entities WHERE type = 'Irrigation';"
        },
        "data_nuances": [
            "Handle name variations (e.g., 瑠公圳 vs 琉公圳) using LIKE.",
            "Be aware of entity prefixes in raw extraction (e.g., '乃鑿大安圳').",
            "Volumes 27 (Agriculture) contains 90% of irrigation entities."
        ],
        "common_snippets": {
            "entity_stats": "SELECT type, count(*) FROM entities GROUP BY type;",
            "person_mentions": "SELECT m.snippet FROM mentions m JOIN entities e ON m.entity_id = e.id WHERE e.name = '王世傑';"
        },
        "layer2_usage": {
            "instruction": "Before performing complex HGIS analysis, always check ai_knowledge_atlas first for synthesized models.",
            "categories": ["Eco_System", "Economy", "Gov_Structure", "Conflict_Logic", "Toponym_Ref"]
        }
    }

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO ai_knowledge_atlas (category, subject, scope_vol_id, data_payload, semantic_summary, version_tag)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        'AI_Guidance',
        '數位臺灣通史資料庫導航與 AI 作業模式',
        None,
        json.dumps(guidance_data, ensure_ascii=False),
        "為後續 AI 代理程式提供資料庫操作的最佳實踐、導航模式與 SQL 指令範例，確保知識解析的連續性與深度。",
        '2026-02-22-v1'
    ))
    
    conn.commit()
    conn.close()
    print("✅ AI 作業模式與導航指引已成功入庫，達成知識傳承目標。")

if __name__ == "__main__":
    ingest_ai_guidance()
