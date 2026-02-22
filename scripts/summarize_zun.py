import sqlite3
import json
import re

DB_PATH = "data/history_texts/taiwan_history.db"

def clean_snippet(text):
    if not text:
        return ""
    # 移除重複的段落 (有時候 group_concat 會把相同的 snippet 重複合併)
    snippets = list(set(text.split(' | ')))
    # 取最長或最具代表性的段落（通常第一段就有定義）
    # 這裡我們把它們合併，但限制長度以作為摘要
    combined = " / ".join(snippets)
    # 移除多餘的換行和空白
    combined = re.sub(r'\s+', ' ', combined).strip()
    return combined[:200] + ("..." if len(combined) > 200 else "")

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 取出所有包含「圳」的基礎設施及其所有的提及段落
    cursor.execute("""
        SELECT e.id, e.name, e.meta_data, GROUP_CONCAT(m.snippet, ' | ') as all_snippets
        FROM entities e
        JOIN mentions m ON e.id = m.entity_id
        WHERE e.type = 'Infrastructure' AND e.name LIKE '%圳%'
        GROUP BY e.id
    """)
    
    rows = cursor.fetchall()
    updated_count = 0
    summaries_for_report = []
    
    for row in rows:
        entity_id, name, meta_data_str, all_snippets = row
        
        # 產生摘要
        summary = clean_snippet(all_snippets)
        
        # 解析現有的 meta_data
        meta_data = {}
        if meta_data_str:
            try:
                meta_data = json.loads(meta_data_str)
            except json.JSONDecodeError:
                pass
                
        # 更新 meta_data 加入 summary
        meta_data['summary'] = summary
        
        # 寫回資料庫
        cursor.execute("UPDATE entities SET meta_data = ? WHERE id = ?", (json.dumps(meta_data, ensure_ascii=False), entity_id))
        updated_count += 1
        
        # 收集幾個著名的用來印出報告
        if any(x in name for x in ['隆恩', '曹公', '八堡', '瑠公', '大安', '霄裏', '虎尾', '清水']):
            summaries_for_report.append(f"**{name}**: {summary}")

    conn.commit()
    conn.close()
    
    print(f"✅ 成功為 {updated_count} 條圳路生成摘要並更新至資料庫 `meta_data` 欄位。")
    print("\n--- 經典圳路摘要預覽 ---")
    for s in summaries_for_report[:10]:
        print(s)

if __name__ == "__main__":
    main()
