import sqlite3
import json

DB_PATH = "data/history_texts/taiwan_history.db"

def parse_conflict_logic():
    # Synthetic analysis based on 軍備志, 撫墾志, and 經營紀
    conflict_patterns = [
        {
            "type": "Civil_Rebellion (民變)",
            "subject": "官逼民反與天地會體制",
            "logic": {
                "triggers": ["官吏貪婪", "賦稅過重", "糧價騰貴", "嚴苛禁令"],
                "catalysts": ["天地會等祕密結社", "地方豪強號召", "流民聚集"],
                "dynamics": "一處發難，全台響應；因官兵平日不練，初期多能攻陷城池。",
                "suppression_model": "調撥內地大軍 (如各省班兵) + 徵調地方義民 (Yimin) 協力。"
            },
            "key_events": ["朱一貴事件 (1721)", "林爽文事件 (1786)", "戴潮春事件 (1862)"],
            "summary": "清代三大民變顯示了基層治理失能與祕密社會的深根。"
        },
        {
            "type": "Ethnic_Clash (分類械鬥)",
            "subject": "族群邊界與資源爭奪",
            "logic": {
                "triggers": ["水利灌溉爭端", "土地界址模糊", "語言地緣差異"],
                "groupings": ["漳泉械鬥", "閩粵械鬥", "同鄉聚落對立"],
                "impact": "形成地方武裝化的社會，各莊自建圍牆與砲台，造成行政管理困難。",
                "resolution": "官府往往採取『分而治之』或事後調解，但也導致族群居住空間的高度偏好與隔離。"
            },
            "summary": "族群械鬥是台灣開發史中「地緣政治」的縮影，直接影響了聚落的分佈與防禦建築設計。"
        },
        {
            "type": "Frontier_Conflict (理番衝突)",
            "subject": "理番政策與土地 encroachement",
            "logic": {
                "triggers": ["漢人越界開墾", "樟腦採伐爭利", "原住民出草習俗"],
                "models": [
                    {"name": "以石為界", "logic": "物理隔絕與封禁政策"},
                    {"name": "以路帶墾", "logic": "沈葆楨、劉銘傳時期的開山撫番，以武力推進"},
                    {"name": "化番為民", "logic": "透過設立官制與學校縮小文化差異"}
                ],
                "outcome": "原住民族群的持續向內山退縮或同化。"
            },
            "summary": "理番衝突的核心在於生存空間的爭奪，軍事與教育是清廷雙管齊下的治理手段。"
        },
        {
            "type": "Foreign_Invasion (外侮防衛)",
            "subject": "海防轉型與門戶保衛戰",
            "logic": {
                "triggers": ["列強東顧 (英法美日)", "通商口岸爭利", "船難賠償賠命事件 (如牡丹社)"],
                "strategic_points": ["基隆煤礦", "淡水門戶", "澎湖要塞", "枋寮/琅嶠登陸點"],
                "defense_evolution": [
                    {"stage": "清初", "logic": "偏重防內，認為台灣不需重兵，僅靠水師巡邏"},
                    {"stage": "清末", "logic": "劉銘傳強化砲台、水雷、機器局，轉向現代化海防系統"}
                ]
            },
            "summary": "19世紀後半葉，台灣的防禦邏輯從「防內亂」轉向「禦外侮」，徹底改變了台灣的行政層級與預算配置。"
        }
    ]
    
    return conflict_patterns

def ingest():
    patterns = parse_conflict_logic()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Store the integrated logic
    cursor.execute("""
        INSERT INTO ai_knowledge_atlas (category, subject, scope_vol_id, data_payload, semantic_summary, version_tag)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        'Conflict_Logic',
        '臺灣歷史衝突因果與邏輯模型',
        None, # Cross-volume analysis (軍備, 撫墾, 經營)
        json.dumps(patterns, ensure_ascii=False),
        "從《軍備志》、《撫墾志》等多卷次中綜合建模，涵蓋民變、械鬥、理番衝突與外侮防禦四大邏輯範式。",
        '2026-02-22-v1'
    ))
    
    conn.commit()
    conn.close()
    print("✅ 臺灣歷史衝突與因果事件鏈模型已成功入庫。")

if __name__ == "__main__":
    ingest()
