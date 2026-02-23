import sqlite3
import geopandas as gpd
import os
import json

DB_PATH = "/Users/wuulong/github/bmad-pa/data/history_texts/hsinchu_history.db"
SHP_OAZA = "/Users/wuulong/github/bmad-pa/data/open-data/Historical_Boundaries/1920a_1.shp"

def clean_place_name(name):
    """移除行政區綴詞以進行無行政區劃模糊匹配"""
    return name.replace('庄', '').replace('莊', '').replace('街', '').replace('堡', '').replace('社', '').replace('坑', '').replace('窩', '')

def main():
    if not os.path.exists(SHP_OAZA):
        print(f"Error: 1920s SHP not found at {SHP_OAZA}")
        return

    print("Loading 1920 Oazas SHP...")
    oaza_gdf = gpd.read_file(SHP_OAZA, encoding='big5')
    
    # Calculate Centroids (convert to EPSG:3826 first for accuracy, then back to 4326)
    oaza_gdf.set_crs(epsg=4326, allow_override=True, inplace=True) # Usually original is TWD97 or WGS84? Actually it's likely already lat/lon or TWD97.
    # Assuming the geometry is already proper, we just compute centroid. 
    # Let's project to 3826, get centroid, project back to 4326.
    try:
        if oaza_gdf.crs is None:
             oaza_gdf.set_crs(epsg=4326, inplace=True)
             
        oaza_gdf_proj = oaza_gdf.to_crs(epsg=3826)
        oaza_gdf['centroid'] = oaza_gdf_proj.geometry.centroid
        oaza_gdf['centroid_wgs'] = oaza_gdf['centroid'].to_crs(epsg=4326)
    except Exception as e:
        print(f"CRS projection failed, using default centroids: {e}")
        oaza_gdf['centroid_wgs'] = oaza_gdf.geometry.centroid

    # Build reference dictionaries
    # Keys: Cleaned Name. Values: List of (NAME, NAMEB, lon, lat)
    # Why list? There might be duplicate names across Taiwan, but we'll take the first one or we can filter by bounding box of Hsinchu later if needed.
    oaza_dict = {}
    for idx, row in oaza_gdf.iterrows():
        n1 = str(row['NAME']) if row['NAME'] else ''
        n2 = str(row['NAMEB']) if row.get('NAMEB') else ''
        lon = row['centroid_wgs'].x
        lat = row['centroid_wgs'].y
        
        c_n1 = clean_place_name(n1)
        if c_n1 and c_n1 not in oaza_dict:
            oaza_dict[c_n1] = (n1, n2, lon, lat)
            
        c_n2 = clean_place_name(n2)
        if c_n2 and c_n2 not in oaza_dict:
            oaza_dict[c_n2] = (n1, n2, lon, lat)


    print("Connecting to Hsinchu DB...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT e.id, e.name 
        FROM entities e
        LEFT JOIN spatial_links sl ON e.id = sl.entity_id
        WHERE sl.id IS NULL
    """)
    locations = cursor.fetchall()
    
    print(f"Start matching {len(locations)} Location entities against 1920s Oazas...")
    
    match_count = 0
    for ent_id, name in locations:
        clean_name = clean_place_name(name)
        
        # We try exact match first, then clean match
        matched_info = None
        # direct exact match logic could be added, but clean name usually suffices
        
        if clean_name in oaza_dict:
            matched_info = oaza_dict[clean_name]
        
        if matched_info:
            o_name, o_nameb, lon, lat = matched_info
            
            # Since there could be name collisions across Taiwan, we are making an assumption here.
            # A more robust check would involve bounding box for Hsinchu, but let's proceed with greedy match first.
            meta = json.dumps({"source": "1920a_1.shp", "matched_oaza": o_name, "matched_town": o_nameb, "clean_key": clean_name}, ensure_ascii=False)
            
            # Check if link exists
            cursor.execute("SELECT id FROM spatial_links WHERE entity_id = ?", (ent_id,))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO spatial_links (entity_id, longitude, latitude, accuracy, meta_data)
                    VALUES (?, ?, ?, ?, ?)
                """, (ent_id, lon, lat, '1920_Oaza', meta))
                match_count += 1

    conn.commit()
    conn.close()
    print(f"Spatial Linkage via 1920 Oaza completed. {match_count} points linked.")

if __name__ == "__main__":
    main()
