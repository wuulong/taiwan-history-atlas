import os
import sys

# Add scripts directory to path for portability
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config

DB_PATH = config.DB_PATH


# Add scripts directory to path for portability

import sqlite3
import json
import re


def parse_economy_data():
    # Paths to the dumped MD files
    files = {
        "榷賣志": "tmp/kuemai_zhi_full.md",
        "商務志": "tmp/shangwu_zhi_full.md",
        "虞衡志": "tmp/yuheng_zhi_full.md",
        "農業志": "tmp/agriculture_zhi_full.md"
    }
    
    economy_assets = []
    
    # 1. 鹽業 (Salt) - From 榷賣志
    with open(files["榷賣志"], 'r', encoding='utf-8') as f:
        kuemai_content = f.read()
    
    salt_matches = re.finditer(r"曰(瀨口|州南|州北|瀨北|瀨南|瀨東|井仔腳|布袋嘴|北門嶼|虎仔山)", kuemai_content)
    salt_sites = []
    for m in salt_matches:
        site = m.group(1)
        if site not in salt_sites: salt_sites.append(site)
    
    economy_assets.append({
        "category": "Economy_Salt",
        "subject": "清代臺灣鹽場分佈",
        "data": {
            "origin": "陳永華於永曆19年教民曬鹽 (瀨口)",
            "major_fields": ["州南", "州北", "瀨北", "瀨南", "瀨東 (井仔腳)", "布袋嘴", "北門嶼", "虎仔山"],
            "management": "雍正4年歸官辦，設鹽總館與分館"
        },
        "summary": "記錄臺灣鹽業從鄭氏時期的瀨口起源，到清代四大場及後續布袋、北門等場的演進。涉及鹽課管理與各地銷量。"
    })

    # 2. 樟腦 (Camphor) - From 榷賣志
    economy_assets.append({
        "category": "Economy_Camphor",
        "subject": "樟腦產業與官辦體系",
        "data": {
            "origins": "傳自泉州，鄭氏時期已配售日本",
            "production_centers": ["大嵙崁", "三角湧", "南莊", "彰化", "集集", "罩蘭", "埔里社"],
            "monopoly_history": [
                {"period": "清初", "policy": "封禁番地，私熬者死"},
                {"period": "咸豐5年", "policy": "英商德記洋行開始購腦"},
                {"period": "光緒13年", "policy": "劉銘傳設全臺腦磺總局，改官辦"},
                {"period": "光緒16年", "policy": "廢官辦改民辦，改課釐金"}
            ]
        },
        "summary": "樟腦為臺灣特產，經歷封禁、軍工採伐、洋商競爭到劉銘傳官辦改革。是清代中後期撫番經費的主要來源。"
    })

    # 3. 糖業 (Sugar) - From 農業志
    economy_assets.append({
        "category": "Economy_Sugar",
        "subject": "糖業體制與糖組織",
        "data": {
            "types_of_sugar_mills": [
                {"name": "公司", "desc": "合股而設"},
                {"name": "頭家", "desc": "業主所設"},
                {"name": "牛奔", "desc": "蔗農合設，九奔互助法"}
            ],
            "products": ["青糖", "白糖 (頭擋、二擋、三擋)", "府玉 (台南郡治名產)", "冰糖", "赤沙"],
            "trade": "由三郊之「糖郊」主導，販運至京津、日本"
        },
        "summary": "詳述臺灣糖業的生產組織（糖）、產品等級與貿易脈絡。台南郡治所製之「府玉」馳名內外。"
    })

    # 4. 茶業 (Tea) - From 農業志
    economy_assets.append({
        "category": "Economy_Tea",
        "subject": "茶業興起與國際貿易",
        "data": {
            "origin": "嘉慶時柯朝自福建武夷引入，植於魚坑",
            "early_centers": ["水沙連 (崠頂佳)", "石碇", "文山", "八里坌", "新竹 (埔茶)"],
            "market_transformation": "同治間英商德克來勸農種植並貸費，烏龍茶外銷美國，包種茶外銷南洋",
            "economic_impact": "帶動艋舺、大稻埕商業繁榮，年值兩百萬圓"
        },
        "summary": "記錄臺灣茶業從武夷引種到外商經營促成烏龍茶與包種茶盛世的過程，成就了台北盆地的繁榮。"
    })

    return economy_assets

def ingest_economy_to_atlas():
    assets = parse_economy_data()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for asset in assets:
        cursor.execute("""
            INSERT INTO ai_knowledge_atlas (category, subject, scope_vol_id, data_payload, semantic_summary, version_tag)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            asset["category"],
            asset["subject"],
            None, # Cross-volume
            json.dumps(asset["data"], ensure_ascii=False),
            asset["summary"],
            '2026-02-22-v1'
        ))
    
    conn.commit()
    conn.close()
    print(f"✅ 成功入庫 {len(assets)} 項【Economy】產業特產資產。")

if __name__ == "__main__":
    ingest_economy_to_atlas()
