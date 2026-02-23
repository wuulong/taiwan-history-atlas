import os
import sys

# Add scripts directory to path for portability
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config

DB_PATH = config.DB_PATH


# Add scripts directory to path for portability

import sqlite3
import json
import datetime


def ingest_fuken_poi():
    poi_data = [
        {"name": "撫墾總局", "location": "桃園大溪", "note": "全臺撫墾事務指揮中樞"},
        {"name": "大嵙崁撫墾局", "location": "桃園大溪", "note": "北路番界治安與開墾"},
        {"name": "三角湧分局", "location": "新北三峽", "note": "泰雅族與漢人交界重鎮"},
        {"name": "咸菜甕分局", "location": "新竹關西", "note": "泰雅地區行政重心"},
        {"name": "南莊分局", "location": "苗栗南莊", "note": "賽夏族與泰雅族招撫"},
        {"name": "東勢角撫墾局", "location": "台中東勢", "note": "中路大甲溪流域開發"},
        {"name": "大湖分局", "location": "苗栗大湖", "note": "樟腦產量極大區域"},
        {"name": "埔裏社撫墾局", "location": "南投埔里", "note": "管理中部盆地熟番與生番"},
        {"name": "叭哩沙撫墾局", "location": "宜蘭三星", "note": "宜蘭泰雅族接觸最前線"},
        {"name": "恆春撫墾局", "location": "屏東恆春", "note": "極南地區十八社招撫"},
        {"name": "臺東撫墾局", "location": "台東市", "note": "後山理番總部"}
        # ... 僅列出代表性據點作為測試
    ]
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. 寫入撫墾局 POI 清單
    cursor.execute("""
        INSERT INTO ai_knowledge_atlas (category, subject, scope_vol_id, data_payload, semantic_summary, version_tag)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        'Gov_Org', 
        '清代臺灣撫墾局據點 POI 清單', 
        15, # 撫墾志
        json.dumps(poi_data, ensure_ascii=False),
        '整理自《撫墾志》末尾管轄表，包含總局、各級撫墾局及分局之歷史名稱與現代地名對照。',
        '2026-02-22-v1'
    ))

    # 2. 寫入原住民生活特徵矩陣
    ethnography_data = [
        {"group": "流求住民", "habit": "深目長鼻, 盤髮鳥羽冠", "social": "戰鬥殺人祭神, 牆壁聚髑髏", "tech": "火燒引水灌田, 石刃插墾"},
        {"group": "斗尾龍岸番", "habit": "齥面文身", "social": "以頭作飲器, 鄰社畏之", "notability": "強悍, 居大甲溪北"},
        {"group": "岸裏番", "habit": "勇敢驍捷", "social": "能越山度澗, 官方重要盟友", "tech": "擅長山後襲擊"}
    ]
    
    cursor.execute("""
        INSERT INTO ai_knowledge_atlas (category, subject, scope_vol_id, data_payload, semantic_summary, version_tag)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        'Ethnography', 
        '臺灣通史原住民生活特徵矩陣', 
        1, # 開闢紀為主，撫墾志為輔
        json.dumps(ethnography_data, ensure_ascii=False),
        '跨卷次整理之原住民習俗、社會結構與工藝技術描述，包含早期流求文明與清代強悍部落對照。',
        '2026-02-22-v1'
    ))

    conn.commit()
    conn.close()
    print("✅ 分析成果已成功「入庫」至 ai_knowledge_atlas")

if __name__ == "__main__":
    ingest_fuken_poi()
