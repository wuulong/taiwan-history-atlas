import sqlite3
import json
import re

DB_PATH = "data/history_texts/taiwan_history.db"

def parse_toponym_data():
    file_path = "tmp/jiangyu_zhi_full.md"
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Core Toponym Evolution (The "Big Changes")
    core_evolutions = [
        {"old": "赤崁", "new": "安平/承天府", "period": "鄭氏/清初"},
        {"old": "諸羅", "new": "嘉義", "period": "乾隆52年改"},
        {"old": "半線", "new": "彰化", "period": "雍正元年設"},
        {"old": "竹塹", "new": "新竹", "period": "光緒4年設"},
        {"old": "蛤仔難/甲子蘭", "new": "宜蘭", "period": "嘉慶15年設廳, 光緒元年改縣"},
        {"old": "雞籠", "new": "基隆", "period": "光緒初年改"},
        {"old": "貓裏", "new": "苗慄", "period": "光緒14年設"},
        {"old": "琅嶠", "new": "恆春", "period": "光緒元年設"},
        {"old": "卑南", "new": "臺東", "period": "光緒13年設"},
        {"old": "水沙連/埔裏社", "new": "埔裏", "period": "光緒初年設"},
        {"old": "打狗", "new": "鳳山/旗後", "period": "清代地理描述"}
    ]

    # 2. Extracting "Bao/Li" Lists for each county
    # Pattern: [County Name]轄[N]堡/里：[List...]
    county_regex = r"([^\n。!]+(?:縣|廳|州))轄(?:[^\n。!]+(?:堡|里|澳|鄉))：(.*?)(?=\n[^\n。!]+(?:縣|廳|州)轄|$)"
    county_matches = re.finditer(county_regex, content, re.DOTALL)
    
    county_subdivisions = {}
    for m in county_matches:
        county_name = m.group(1).strip()
        raw_list = m.group(2).strip()
        # Clean up the list (remove notes like "南隸安平")
        items = [item.strip() for item in re.split(r'、|，', raw_list) if item.strip()]
        county_subdivisions[county_name] = items

    # 3. Geo-Semantic Insights
    insights = [
        "地名多源自原住民社名 (如諸羅、半線、竹塹、貓裏、蛤仔難)。",
        "『堡 (Bao)』與『里 (Li)』的分佈：南部多稱『里』(承襲鄭氏制度)；中北部及新開發區多稱『堡』。",
        "地名命名邏輯：早期以社名為主，清中葉後出現寓意吉祥與皇恩地名 (如嘉義、彰化、恆春、宜蘭)。",
        "微地形與產業影響地名 (如大嵙崁、港崗、鹽水港、葫蘆墩)。"
    ]

    assets = [
        {
            "category": "Toponym_Ref",
            "subject": "臺灣歷史大行政區地名演進矩陣",
            "data": core_evolutions,
            "summary": "整理自《疆域志》，記錄臺灣主要府縣名稱從早期原住民社名到鄭氏、清代命名邏輯的轉變。"
        },
        {
            "category": "Toponym_Ref",
            "subject": "清末全臺堡里澳鄉分佈名錄",
            "data": county_subdivisions,
            "summary": "詳列清末全台三府、一州、三廳、十一縣所轄之具體堡、里、澳、鄉名稱，是 HGIS 空間定位的基礎層。"
        },
        {
            "category": "Toponym_Ref",
            "subject": "臺灣地名命名學與地理維度洞察",
            "data": insights,
            "summary": "歸納地名背後的族群、地形、產業與政治意志，解釋『里』與『堡』的地緣分佈差異。"
        }
    ]

    return assets

def ingest():
    assets = parse_toponym_data()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for asset in assets:
        cursor.execute("""
            INSERT INTO ai_knowledge_atlas (category, subject, scope_vol_id, data_payload, semantic_summary, version_tag)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            asset["category"],
            asset["subject"],
            5, # 疆域志
            json.dumps(asset["data"], ensure_ascii=False),
            asset["summary"],
            '2026-02-22-v1'
        ))
    
    conn.commit()
    conn.close()
    print(f"✅ 成功入庫 {len(assets)} 項【Toponym_Ref】地名與演進資產。")

if __name__ == "__main__":
    ingest()
