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


def parse_zhiguan_data():
    file_path = "tmp/zhiguan_zhi_full.md"
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. 歷史行政區域與官職對照表 (Timeline of Admin)
    # Extracting logic from text summary
    admin_evolution = [
        {"period": "荷蘭時期", "structure": "知事治之, 隸爪哇總督"},
        {"period": "鄭氏時期", "structure": "延平郡王開府: 承天府 (府尹), 天興知縣, 萬年知縣, 澎湖安撫司"},
        {"period": "清初 (康熙)", "structure": "一府三縣: 臺灣府, 臺灣縣, 鳳山縣, 諸羅縣"},
        {"period": "清中 (雍正-嘉慶)", "structure": "增設彰化縣, 淡水同知, 噶瑪蘭廳"},
        {"period": "清末 (光緒)", "structure": "建省: 臺灣巡撫, 三府 (臺南, 臺北, 臺灣), 一直隸州 (臺東), 十一縣"}
    ]

    # 2. 官職清單 (POI for roles and titles)
    # Using regex to capture titles from the list at the end
    title_entries = []
    
    # Matches patterns like "臺灣巡撫一員。..." or "臺南知府一員。..."
    matches = re.finditer(r"([^\n。!]+一員)。(.*?)(?=\n[^\n。!]+一員|$)", content, re.DOTALL)
    
    for m in matches:
        full_title = m.group(1).strip()
        description = m.group(2).strip()
        
        # Clean title (remove "一員")
        clean_title = full_title.replace("一員", "").strip()
        
        title_entries.append({
            "title": clean_title,
            "description": description
        })

    # 3. 俸祿與養廉銀資料 (Economy of Power)
    salary_data = {
        "base_salary": [
            {"rank": "分巡道/知府", "amount": "62.044 兩"},
            {"rank": "知縣", "amount": "27.49 兩"}
        ],
        "yang_lian_extra": [
            {"rank": "分巡道", "amount": "1600 兩"},
            {"rank": "臺灣知縣", "amount": "1000 兩"},
            {"rank": "其他知縣", "amount": "800 兩"}
        ],
        "note": "乾隆八年以後增加養廉銀以革除貪墨"
    }

    # Package into assets
    assets = [
        {
            "category": "Gov_Structure",
            "subject": "臺灣歷史行政體系演進 (荷鄭清)",
            "data": admin_evolution,
            "summary": "整理自《職官志》，涵蓋荷蘭知事、鄭氏承天府到清末建省的三府十一縣演變。"
        },
        {
            "category": "Gov_Structure",
            "subject": "清代臺灣主要官職職掌清單",
            "data": title_entries,
            "summary": "羅列清代在臺核心文官職位（巡撫、布政使、道、府、同知、知縣、巡檢）的設立背景與權責。"
        },
        {
            "category": "Gov_Structure",
            "subject": "清代官職俸祿與養廉體制",
            "data": salary_data,
            "summary": "記錄乾隆時期增加養廉銀的具體數額，反映當時為了維持廉政所做的財政調整。"
        }
    ]
    
    return assets

def ingest():
    assets = parse_zhiguan_data()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for asset in assets:
        cursor.execute("""
            INSERT INTO ai_knowledge_atlas (category, subject, scope_vol_id, data_payload, semantic_summary, version_tag)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            asset["category"],
            asset["subject"],
            6, # 職官志
            json.dumps(asset["data"], ensure_ascii=False),
            asset["summary"],
            '2026-02-22-v1'
        ))
    
    conn.commit()
    conn.close()
    print(f"✅ 成功入庫 {len(assets)} 項【Gov_Structure】官職與權力結構資產。")

if __name__ == "__main__":
    ingest()
