import sqlite3
import json
import os

DB_PATH = "data/history_atlas.db"
GEO_DIR = "data/geojson"
MD_DIR = "data/markdown"

def slugify(text):
    import re
    return re.sub(r'[^\w\s-]', '', text).strip().replace(' ', '_')

def export_atlas():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, subject, category, data_payload, semantic_summary, author_agent, updated_at FROM knowledge_atlas")
    rows = cursor.fetchall()

    for row in rows:
        a_id, subject, category, payload_str, summary, author, updated = row
        slug = slugify(subject)
        
        try:
            payload = json.loads(payload_str)
        except Exception as e:
            print(f"Skipping {subject}: Invalid JSON payload. Error: {e}")
            continue

        if not isinstance(payload, list):
            print(f"Skipping {subject}: Payload is not a list (it is {type(payload)}).")
            continue

        # 1. Export GeoJSON
        geojson = {
            "type": "FeatureCollection",
            "name": subject,
            "features": []
        }

        has_coordinates = False
        for item in payload:
            if not isinstance(item, dict):
                continue
            
            lon = item.get("longitude")
            lat = item.get("latitude")
            if lon is not None and lat is not None:
                try:
                    has_coordinates = True
                    feature = {
                        "type": "Feature",
                        "properties": {k: v for k, v in item.items() if k not in ["longitude", "latitude"]},
                        "geometry": {
                            "type": "Point",
                            "coordinates": [float(lon), float(lat)]
                        }
                    }
                    geojson["features"].append(feature)
                except (ValueError, TypeError):
                    continue

        if has_coordinates:
            geo_filename = os.path.join(GEO_DIR, f"{slug}.geojson")
            with open(geo_filename, "w", encoding="utf-8") as f:
                json.dump(geojson, f, ensure_ascii=False, indent=2)
            print(f"Exported GeoJSON: {geo_filename}")

        # 2. Export Markdown
        md_filename = os.path.join(MD_DIR, f"{slug}.md")
        with open(md_filename, "w", encoding="utf-8") as f:
            f.write(f"# {subject}\n\n")
            f.write(f"**類別**: {category}  \n")
            f.write(f"**摘要**: {summary}  \n")
            f.write(f"**更新時間**: {updated}  \n")
            f.write(f"**維護者**: {author}  \n\n")
            
            if payload:
                # Filter to only dict items for the table, others as list
                dict_items = [i for i in payload if isinstance(i, dict)]
                if dict_items:
                    # Get headers from the union of all keys in first 10 items to be safe
                    all_keys = []
                    for i in dict_items[:10]:
                        for k in i.keys():
                            if k not in all_keys:
                                all_keys.append(k)
                    
                    headers = all_keys
                    f.write("| " + " | ".join(headers) + " |\n")
                    f.write("| " + " | ".join(["---"] * len(headers)) + " |\n")
                    # Limit markdown table to 500 rows to avoid giant files
                    for item in dict_items[:500]:
                        cols = []
                        for h in headers:
                            val = str(item.get(h, "")).replace("\n", " ").replace("|", "\\|")
                            if len(val) > 200: val = val[:197] + "..."
                            cols.append(val)
                        f.write("| " + " | ".join(cols) + " |\n")
                    
                    if len(dict_items) > 500:
                        f.write(f"\n*... 還有 {len(dict_items) - 500} 筆資料未顯示，請參考完整資料集。*\n")
                else:
                    f.write("## 資料列表\n\n")
                    for item in payload:
                        f.write(f"- {item}\n")

        print(f"Exported Markdown: {md_filename}")

    conn.close()

if __name__ == "__main__":
    export_atlas()
