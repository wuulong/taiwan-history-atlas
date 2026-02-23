import os
import sys

# Add scripts directory to path for portability
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config

DB_PATH = config.DB_PATH

import sqlite3
import pandas as pd
import geopandas as gpd
import json
import re

SHP_B_PATH = config.SHP_B_PATH
SHP_A_PATH = config.SHP_A_PATH

def clean_location_name(name):
    # 移除行政單位或概略描述的後綴，只保留核心地名
    return re.sub(r"(莊|庄|社|街|堡|里|廳|縣|附近|等地|等庄)$", "", name)

def get_centroid_wgs84(geom):
    centroid = geom.centroid
    twd_lon, twd_lat = centroid.x, centroid.y
    # TWD67 to WGS84 approx
    wgs_lon = twd_lon + 0.00827
    wgs_lat = twd_lat - 0.0020
    return wgs_lon, wgs_lat

def guess_anchor(context_text):
    """
    根據上下文推斷隸屬的 1920 年代州廳 (Hierarchical Anchor)。
    """
    if not context_text: return None
    
    if any(k in context_text for k in ["新竹", "竹塹"]): return {"NAMED": "新竹州"}
    if any(k in context_text for k in ["淡水", "艋舺", "大稻埕", "臺北"]): return {"NAMED": "臺北州"}
    if any(k in context_text for k in ["彰化", "半線", "臺中"]): return {"NAMED": "臺中州"}
    if any(k in context_text for k in ["打狗", "高雄", "鳳山", "阿猴", "屏東"]): return {"NAMED": "高雄州"}
    if any(k in context_text for k in ["嘉義", "諸羅", "笨港", "臺南", "安平", "臺灣府"]): return {"NAMED": "臺南州"}
    if any(k in context_text for k in ["宜蘭", "噶瑪蘭", "蛤仔難"]): return {"NAMED": "臺北州"} # 宜蘭在 1920 屬臺北州
    return None

def find_match(core_name, gdf, level, anchor=None):
    matches = gdf[gdf['NAME'] == core_name]
    if matches.empty:
        matches = gdf[gdf['NAME'].str.contains(core_name, na=False, regex=False)]
    
    # 應用行政階層錨定 (Hierarchical Anchor)
    if not matches.empty and anchor:
        anchored_matches = matches.copy()
        for k, v in anchor.items():
            if k in anchored_matches.columns:
                anchored_matches = anchored_matches[anchored_matches[k].str.contains(v, na=False)]
        # 如果錨定後有結果，就採用錨定結果；否則退回無錨定的全台搜索結果
        if not anchored_matches.empty:
            matches = anchored_matches

    if not matches.empty:
        first_match = matches.iloc[0]
        wgs_lon, wgs_lat = get_centroid_wgs84(first_match.geometry)
        match_type = "exact" if first_match['NAME'] == core_name else "fuzzy"
        
        meta_data = {
            "geo_source": "1920b_1.shp" if level == "B" else "1920a_1.shp",
            "matched_NAMED": str(first_match.get('NAMED', '')),
            "matched_NAMEC": str(first_match.get('NAMEC', '')),
            "matched_NAME": str(first_match.get('NAME', '')),
            "match_level": "Township(B)" if level == "B" else "Oaza(A)",
            "match_type": match_type,
            "anchor_used": anchor
        }
        return wgs_lon, wgs_lat, meta_data, first_match['NAME']
    return None

def find_match_db(core_name, cursor, anchor=None):
    cursor.execute("SELECT place_name, county, town, village, longitude, latitude FROM moi_settlements WHERE place_name = ?", (core_name,))
    matches = cursor.fetchall()
    
    if not matches:
        cursor.execute("SELECT place_name, county, town, village, longitude, latitude FROM moi_settlements WHERE place_name LIKE ?", (f"%{core_name}%",))
        matches = cursor.fetchall()
        
    if matches and anchor:
        modern_anchors = []
        state = anchor.get("NAMED")
        if state == "新竹州": modern_anchors = ["新竹縣", "新竹市", "桃園市", "苗栗縣", "桃園縣"]
        elif state == "臺北州": modern_anchors = ["臺北", "新北", "基隆", "宜蘭"]
        elif state == "臺中州": modern_anchors = ["臺中", "彰化", "南投"]
        elif state == "臺南州": modern_anchors = ["雲林", "嘉義", "臺南"]
        elif state == "高雄州": modern_anchors = ["高雄", "屏東"]
        
        if modern_anchors:
            anchored_matches = [m for m in matches if any(a in m[1] for a in modern_anchors)]
            if anchored_matches:
                matches = anchored_matches
                
    if matches:
        first_match = matches[0]
        place_name, county, town, village, lon, lat = first_match
        match_type = "exact" if place_name == core_name else "fuzzy"
        
        meta_data = {
            "geo_source": "moi_settlements",
            "matched_county": county,
            "matched_town": town,
            "matched_village": village,
            "matched_NAME": place_name,
            "match_type": match_type,
            "anchor_used": anchor
        }
        return lon, lat, meta_data, place_name
    return None

def main():
    print(f"Loading Township Shapefile from {SHP_B_PATH} ...")
    try:
        gdf_b = gpd.read_file(SHP_B_PATH, encoding='big5')
    except Exception as e:
        print(f"Failed to load Shapefile B: {e}")
        return

    print(f"Loading Oaza Shapefile from {SHP_A_PATH} ...")
    try:
        gdf_a = gpd.read_file(SHP_A_PATH, encoding='big5')
    except Exception as e:
        print(f"Failed to load Shapefile A: {e}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 清除舊的配對，讓更新的邏輯可以重新套用
    cursor.execute("DELETE FROM spatial_links")
    
    cursor.execute("SELECT id, name FROM entities WHERE type = 'Location'")
    locations = cursor.fetchall()
    
    print(f"Found {len(locations)} Location entities in database.")
    
    matched_count = 0
    for entity_id, raw_name in locations:
        core_name = clean_location_name(raw_name)
        if len(core_name) < 2:
            continue
            
        # 獲取該地名的所有上下文 (mentions) 作為推斷依據
        cursor.execute("SELECT GROUP_CONCAT(snippet, ' ') FROM mentions WHERE entity_id = ?", (entity_id,))
        context_text = cursor.fetchone()[0]
        anchor = guess_anchor(context_text)

        # 先找 B (街庄)，找不到再找 A (大字)，並帶入推斷出的 anchor
        match_result = find_match(core_name, gdf_b, "B", anchor)
        if not match_result:
            match_result = find_match(core_name, gdf_a, "A", anchor)
        if not match_result:
            match_result = find_match_db(core_name, cursor, anchor)
            
        if match_result:
            wgs_lon, wgs_lat, meta_data, matched_name = match_result
            
            # 寫入 spatial_links 表
            cursor.execute("""
                INSERT INTO spatial_links (entity_id, longitude, latitude, accuracy, meta_data) 
                VALUES (?, ?, ?, ?, ?)
            """, (entity_id, wgs_lon, wgs_lat, "Centroid (1920 SHP)", json.dumps(meta_data, ensure_ascii=False)))
            
            matched_count += 1
            # 印出帶有 anchor 命中的結果
            if meta_data.get('anchor_used') and matched_count <= 25:
                name_1 = meta_data.get('matched_NAMED', meta_data.get('matched_county', ''))
                name_2 = meta_data.get('matched_NAMEC', meta_data.get('matched_town', ''))
                print(f"⚓ Anchored: {raw_name} -> {name_1} {name_2} {matched_name}")
                
    conn.commit()
    conn.close()
    
    print("-" * 30)
    print(f"Phase 3 Hierarchical Geo-Coding Completed! Successfully matched {matched_count} / {len(locations)} locations.")
    
if __name__ == "__main__":
    main()
