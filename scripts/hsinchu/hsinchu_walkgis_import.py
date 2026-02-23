import sqlite3
import json
import os
from datetime import datetime

# Configuration
HSINCHU_DB_PATH = '/Users/wuulong/github/bmad-pa/data/history_texts/hsinchu_history.db'
WALKGIS_DB_PATH = '/Users/wuulong/github/bmad-pa/events/notes/wuulong-notes-blog/static/walkgis_prj/walkgis.db'
FEATURES_DIR = '/Users/wuulong/github/bmad-pa/events/notes/wuulong-notes-blog/static/walkgis_prj/features/'
MAP_ID = '20260223_hsinchu_historical_atlas'

def export_to_md(fid, name, desc, lng, lat, properties):
    """
    Saves the feature to a .md file with frontmatter to stick to the standard workflow.
    """
    if not os.path.exists(FEATURES_DIR):
        os.makedirs(FEATURES_DIR)
        
    content = f"""---
name: "{name}"
description: "{desc}"
geometry:
  type: Point
  coordinates: [{lng}, {lat}]
properties:
{json.dumps(properties, ensure_ascii=False, indent=2)}
---

{desc}
"""
    filepath = os.path.join(FEATURES_DIR, f"{fid}.md")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    return filepath

def sync_all():
    if not os.path.exists(WALKGIS_DB_PATH):
        print(f"Error: Database not found at {WALKGIS_DB_PATH}")
        return
        
    if not os.path.exists(HSINCHU_DB_PATH):
        print(f"Error: Database not found at {HSINCHU_DB_PATH}")
        return

    # WalkGIS DB Connection
    walk_conn = sqlite3.connect(WALKGIS_DB_PATH)
    walk_cursor = walk_conn.cursor()

    # 1. Ensure Map exists
    walk_cursor.execute("""
        INSERT OR REPLACE INTO walking_maps (map_id, name, description, cover_image, region)
        VALUES (?, ?, ?, ?, ?)
    """, (MAP_ID, "竹塹五書歷史知識地圖", "整合《新竹縣採訪冊》等五大新竹方志，標靶 1920 堡圖與內政部古地名的 HGIS 歷史地景。", "", "新竹"))

    # Get max display order for the map
    walk_cursor.execute("SELECT MAX(display_order) FROM walking_map_relations WHERE map_id = ?", (MAP_ID,))
    row = walk_cursor.fetchone()
    current_order = (row[0] if row and row[0] is not None else -1) + 1

    # Hsinchu DB Connection
    h_conn = sqlite3.connect(HSINCHU_DB_PATH)
    h_cursor = h_conn.cursor()
    
    # 2. Extract Spatially-linked entities
    h_cursor.execute("""
        SELECT e.id, e.name, e.type, s.longitude, s.latitude, s.accuracy, s.meta_data 
        FROM entities e
        JOIN spatial_links s ON e.id = s.entity_id
    """)
    entities = h_cursor.fetchall()
    
    print(f"Processing {len(entities)} Hsinchu Historical entities...")
    
    count = 0
    for ent_id, name, type_val, lon, lat, accuracy, meta_json in entities:
        display_name = f"{name} (古)"
        fid = f"20260223_hsinchu_{ent_id}_{name}"
        
        # Parse Meta
        meta = {}
        if meta_json:
            try:
                meta = json.loads(meta_json)
            except:
                pass
                
        # Construct Description
        desc_lines = [f"【類別】: {type_val}"]
        desc_lines.append(f"【對合來源】: {accuracy}")
        if "matched_name" in meta:
            desc_lines.append(f"【對合地名】: {meta['matched_name']} ({meta.get('county', '')}{meta.get('town', '')})")
        elif "matched_oaza" in meta:
            desc_lines.append(f"【對合大字】: {meta['matched_oaza']} ({meta.get('matched_town', '')})")
            
        # Get mentions snippets
        h_cursor.execute("""
            SELECT v.title, c.raw_text 
            FROM mentions m
            JOIN contents c ON m.content_id = c.id
            JOIN volumes v ON c.vol_id = v.id
            WHERE m.entity_id = ?
            LIMIT 5
        """, (ent_id,))
        mentions = h_cursor.fetchall()
        
        if mentions:
            desc_lines.append("\n=== 史料記載 ===")
            for v_title, text in mentions:
                desc_lines.append(f"[{v_title}] {text[:100]}...")
                
        desc = "\n".join(desc_lines)
        
        props = {
            "category": "歷史與文化",
            "subcategory": type_val,
            "accuracy": accuracy,
            "dataset_version": "v260223.1-Hsinchu"
        }

        # Save MD
        export_to_md(fid, display_name, desc, lon, lat, props)
        
        # Sync to DB
        meta_json_str = json.dumps(props, ensure_ascii=False)
        layer_id = 2 # History/Culture
        
        walk_cursor.execute("""
            INSERT OR REPLACE INTO walking_map_features 
            (feature_id, name, description, layer_id, geometry_type, geometry_wkt, meta_data, updated_at) 
            VALUES (?, ?, ?, ?, 'Point', ?, ?, CURRENT_TIMESTAMP)
        """, (fid, display_name, desc, layer_id, f"POINT({lon} {lat})", meta_json_str))

        walk_cursor.execute("""
            INSERT OR REPLACE INTO walking_map_relations (map_id, feature_id, display_order)
            VALUES (?, ?, ?)
        """, (MAP_ID, fid, current_order))
        current_order += 1
        count += 1
        
    print(f"Successfully imported {count} historical features to WalkGIS.")

    walk_conn.commit()
    walk_conn.close()
    h_conn.close()
    print(f"✅ All Hsinchu features imported to Map: {MAP_ID}")

if __name__ == "__main__":
    sync_all()
