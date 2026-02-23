import sqlite3
import json
import os

HSINCHU_DB_PATH = "/Users/wuulong/github/bmad-pa/data/history_texts/hsinchu_history.db"
TAIWAN_DB_PATH = "/Users/wuulong/github/bmad-pa/data/history_texts/taiwan_history.db"

def clean_place_name(name):
    """移除行政區綴詞以進行無行政區劃模糊匹配"""
    if not name: return ""
    return name.replace('庄', '').replace('莊', '').replace('街', '').replace('堡', '').replace('社', '').replace('坑', '').replace('窩', '')

def main():
    if not os.path.exists(HSINCHU_DB_PATH) or not os.path.exists(TAIWAN_DB_PATH):
        print("Error: Database files not found.")
        return

    print("Connecting to Hsinchu and Taiwan DBs...")
    
    # We will connect to Hsinchu, and ATTACH Taiwan DB
    conn = sqlite3.connect(HSINCHU_DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"ATTACH DATABASE '{TAIWAN_DB_PATH}' AS taiwan_db")

    # Fetch all MOI settlements in Hsinchu Area (Hsinchu City, Hsinchu County, Miaoli County might be relevant)
    # The historical Hsinchu area roughly covers Taoyuan partly, Hsinchu County/City, Miaoli.
    # To be safe and maximize matches, let's load all MOI settlements.
    cursor.execute("""
        SELECT id, place_name, county, town, longitude, latitude, place_mean 
        FROM taiwan_db.moi_settlements
        WHERE longitude IS NOT NULL AND latitude IS NOT NULL
        AND county IN ('新竹市', '新竹縣', '苗栗縣', '桃園市') -- Scope optimization
    """)
    moi_records = cursor.fetchall()
    print(f"Loaded {len(moi_records)} MOI settlement records around Hsinchu basin.")
    
    # Build a lookup table logic
    moi_dict = {}
    for r in moi_records:
        r_id, p_name, county, town, lon, lat, p_mean = r
        clean_p = clean_place_name(p_name)
        if clean_p and clean_p not in moi_dict:
             moi_dict[clean_p] = []
        if clean_p:
            moi_dict[clean_p].append({
                "source": "moi_settlements",
                "place_name": p_name,
                "county": county,
                "town": town,
                "lon": lon,
                "lat": lat,
                "place_mean": p_mean[:50] if p_mean else ""
            })

    # Fetch all Location entities in Hsinchu DB that don't have spatial links yet
    cursor.execute("""
        SELECT e.id, e.name 
        FROM entities e
        LEFT JOIN spatial_links sl ON e.id = sl.entity_id
        WHERE sl.id IS NULL
    """)
    unlinked_locations = cursor.fetchall()
    print(f"Attempting to link {len(unlinked_locations)} unlinked Location entities via MOI...")

    match_count = 0
    for ent_id, name in unlinked_locations:
        clean_name = clean_place_name(name)
        
        # Exact match preferred, clean match fallback
        if clean_name in moi_dict:
            # We take the first match for simplicity, or we can use county/town logic if we have more context
            matched = moi_dict[clean_name][0]
            
            meta = json.dumps({
                "source": "MOI_Settlements",
                "matched_name": matched["place_name"],
                "county": matched["county"],
                "town": matched["town"],
                "clean_key": clean_name
            }, ensure_ascii=False)
            
            cursor.execute("""
                INSERT INTO spatial_links (entity_id, longitude, latitude, accuracy, meta_data)
                VALUES (?, ?, ?, ?, ?)
            """, (ent_id, matched["lon"], matched["lat"], 'MOI_Historic_Settlement', meta))
            match_count += 1
            
    conn.commit()
    conn.close()
    
    print(f"MOI Spatial Linkage completed. {match_count} points linked.")

if __name__ == "__main__":
    main()
