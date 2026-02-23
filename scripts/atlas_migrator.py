import sqlite3
import json
import os
import argparse
from datetime import datetime

def migrate_knowledge_atlas(source_db_path, target_db_path, origin_tag):
    """
    將來源資料庫的 ai_knowledge_atlas 表遷徙至目標資料庫的 knowledge_atlas 表。
    """
    if not os.path.exists(source_db_path):
        print(f"Error: Source DB not found at {source_db_path}")
        return

    src_conn = sqlite3.connect(source_db_path)
    src_cursor = src_conn.cursor()

    tgt_conn = sqlite3.connect(target_db_path)
    tgt_cursor = tgt_conn.cursor()

    # 檢查目標表是否存在
    tgt_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='knowledge_atlas'")
    if not tgt_cursor.fetchone():
        print("Error: Target table 'knowledge_atlas' does not exist in target DB.")
        return

    # 讀取來源數據
    src_cursor.execute("SELECT id, category, subject, data_payload, semantic_summary, version_tag FROM ai_knowledge_atlas")
    rows = src_cursor.fetchall()

    print(f"Migrating {len(rows)} records from {source_db_path} ({origin_tag})...")

    count = 0
    for row in rows:
        orig_id, category, subject, payload, summary, version = row
        
        # 檢查是否已存在 (避免重複遷徙)
        tgt_cursor.execute("SELECT id FROM knowledge_atlas WHERE source_origin=? AND original_id=?", (origin_tag, orig_id))
        if tgt_cursor.fetchone():
            continue

        tgt_cursor.execute("""
            INSERT INTO knowledge_atlas (source_origin, source_db_path, original_id, category, subject, data_payload, semantic_summary, author_agent, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (origin_tag, source_db_path, orig_id, category, subject, payload, summary, "Antigravity Atlas Migrator", datetime.now().isoformat()))
        count += 1

    tgt_conn.commit()
    src_conn.close()
    tgt_conn.close()
    print(f"Successfully migrated {count} new records.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HGIS Atlas Migrator (L1 -> L2)")
    parser.add_argument("--src", required=True, help="Path to the source L1 SQLite database")
    parser.add_argument("--tgt", required=True, help="Path to the target L2 Atlas database")
    parser.add_argument("--origin", required=True, help="Origin tag (e.g., Global, Regional:Hsinchu)")

    args = parser.parse_args()

    migrate_knowledge_atlas(args.src, args.tgt, args.origin)
