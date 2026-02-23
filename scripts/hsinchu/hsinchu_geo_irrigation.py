import sqlite3
import geopandas as gpd
import os
import json

DB_PATH = "/Users/wuulong/github/bmad-pa/data/history_texts/hsinchu_history.db"
TAIWAN_DB_PATH = "/Users/wuulong/github/bmad-pa/data/history_texts/taiwan_history.db"
SHP_OAZA = "/Users/wuulong/github/bmad-pa/data/open-data/Historical_Boundaries/1920a_1.shp"

def clean_water_name(name):
    """移除水利特徵綴詞與冗言，留下核心地名"""
    # 移除前綴字眼
    for prefix in ["二十五里", "引水入", "所謂", "在"]:
         if name.startswith(prefix):
             name = name[len(prefix):]
    
    # 移除描述性字眼
    name = name.replace('水瀦為陂', '').replace('溪', '')
             
    # 移除後綴字眼
    res = name.replace('陂', '').replace('圳', '').replace('潭', '').replace('水池', '').replace('水門', '')
    
    return res.strip()

def main():
    if not os.path.exists(SHP_OAZA):
        print(f"Error: 1920s SHP not found at {SHP_OAZA}")
        return

    # 1. Load Oaza
    print("Loading 1920 Oazas SHP...")
    oaza_gdf = gpd.read_file(SHP_OAZA, encoding='big5')
    oaza_gdf.set_crs(epsg=4326, allow_override=True, inplace=True)
    try:
        if oaza_gdf.crs is None: oaza_gdf.set_crs(epsg=4326, inplace=True)
        oaza_gdf_proj = oaza_gdf.to_crs(epsg=3826)
        oaza_gdf['centroid_wgs'] = oaza_gdf_proj.geometry.centroid.to_crs(epsg=4326)
    except:
        oaza_gdf['centroid_wgs'] = oaza_gdf.geometry.centroid

    oaza_dict = {}
    for idx, row in oaza_gdf.iterrows():
        n1 = str(row['NAME']) if row['NAME'] else ''
        n2 = str(row['NAMEB']) if row.get('NAMEB') else ''
        lon = row['centroid_wgs'].x
        lat = row['centroid_wgs'].y
        
        c_n1 = n1.replace('庄', '').replace('莊', '').replace('街', '').replace('社', '')
        if c_n1 and c_n1 not in oaza_dict:
            oaza_dict[c_n1] = (n1, n2, lon, lat)

    # 2. Load MOI Settlements
    t_conn = sqlite3.connect(TAIWAN_DB_PATH)
    t_cursor = t_conn.cursor()
    t_cursor.execute("""
        SELECT place_name, county, town, longitude, latitude
        FROM moi_settlements
        WHERE longitude IS NOT NULL AND latitude IS NOT NULL
        AND county IN ('新竹市', '新竹縣', '苗栗縣', '桃園市')
    """)
    moi_records = t_cursor.fetchall()
    moi_dict = {}
    for r in moi_records:
        p_name, county, town, lon, lat = r
        if not p_name: continue
        clean_p = p_name.replace('庄', '').replace('莊', '').replace('街', '').replace('社', '')
        if clean_p and clean_p not in moi_dict:
            moi_dict[clean_p] = (p_name, county, town, lon, lat)
    t_conn.close()

    # 3. Connect to Hsinchu and Match Irrigation
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT e.id, e.name 
        FROM entities e
        LEFT JOIN spatial_links sl ON e.id = sl.entity_id
        WHERE e.type = 'Irrigation' AND sl.id IS NULL
    """)
    irrigations = cursor.fetchall()
    
    print(f"Start matching {len(irrigations)} Irrigation entities against spatial bases...")
    
    match_count = 0
    for ent_id, name in irrigations:
        clean_name = clean_water_name(name)
        if len(clean_name) < 2: continue # Ignore too short names
        
        matched = False
        # Try Oaza
        if clean_name in oaza_dict:
            o_name, o_nameb, lon, lat = oaza_dict[clean_name]
            meta = json.dumps({"source": "1920a_1.shp", "matched_oaza": o_name, "matched_town": o_nameb, "clean_key": clean_name}, ensure_ascii=False)
            cursor.execute("""
                INSERT INTO spatial_links (entity_id, longitude, latitude, accuracy, meta_data)
                VALUES (?, ?, ?, ?, ?)
            """, (ent_id, lon, lat, '1920_Oaza', meta))
            match_count += 1
            matched = True
            
        # Try MOI if not matched by Oaza
        if not matched and clean_name in moi_dict:
            p_name, county, town, lon, lat = moi_dict[clean_name]
            meta = json.dumps({
                "source": "MOI_Settlements",
                "matched_name": p_name,
                "county": county,
                "town": town,
                "clean_key": clean_name
            }, ensure_ascii=False)
            cursor.execute("""
                INSERT INTO spatial_links (entity_id, longitude, latitude, accuracy, meta_data)
                VALUES (?, ?, ?, ?, ?)
            """, (ent_id, lon, lat, 'MOI_Historic_Settlement', meta))
            match_count += 1

    conn.commit()
    conn.close()
    print(f"Spatial Linkage via Water Feature completed. {match_count} points linked.")

if __name__ == "__main__":
    main()
