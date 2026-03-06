
import sqlite3
import json
import os
import time
import subprocess

DB_PATH = "/Users/wuulong/github/bmad-pa/data/history_texts/history_atlas.db"
FAB_CMD = "/Users/wuulong/github/bmad-pa/fab"

def generate_historical_context(site_data):
    """Call Gemini via fab ask to generate historical context."""
    
    prompt = f"""
你是一位深諳台灣考古學、地貌學與人類學的專家。請根據以下考古遺址的「特徵標籤」與「精算過的水文距離」，寫出一段約 200 字，引人入勝且具備專業深度的「地理與歷史脈絡 (Historical Context)」。
這將用於 WalkGIS 地圖的展示，目的是讓一般民眾了解古人為何選擇住在這裡、他們的生活型態，以及這群人與水系地貌的互動關係。

## 考古遺址輸入數據：
- 遺址名稱：{site_data['name']}
- 文化年代：{site_data['cultural_period']}
- 多層疊壓 (多時期利用)：{'是 (這是一處被多個時代的人群重複選擇定居的風水寶地)' if site_data['is_multicomponent'] else '否 (時代單一)'}
- 學術等級：Rank {site_data['importance_rank']} (1為最高國定，4為疑似)
- 聚落特徵與功能：{json.dumps(site_data['site_function'], ensure_ascii=False)}

## 精確水文幾何空間特徵 (L4 Topology)：
{json.dumps(site_data['l4_topology'], indent=2, ensure_ascii=False)}

## 撰寫要求（嚴格遵守）：
1. 字數約 200 字，分兩段：第一段寫「地理地貌環境與選址邏輯」，第二段寫「這群人的生存型態或歷史重要性」。
2. 請直接給出文本，不要有任何前言後語（如「好的，為您生成...」）。
3. 必須善用「L4 Topology」中提到的河流名稱與距離，具體說明這是「主流旁」、「支流交會處」還是「遠離現今水系（可能依靠古台江內海或舊河道）」。
4. 使用繁體中文，台灣觀點（禁止中國用語）。
"""

    prompt = prompt.strip()
    try:
        # call ./fab ask --question="{prompt}"
        # using subprocess
        result = subprocess.check_output([FAB_CMD, "ask", f"--question={prompt}"], text=True, stderr=subprocess.STDOUT)
        
        # Clean up ANSI escape codes
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        clean_text = ansi_escape.sub('', result)
        
        lines = clean_text.strip().split('\n')
        final_lines = []
        capture = False
        
        # Fabric task output usually starts dumping Gemini text after "Gemini:" or just straight text.
        for line in lines:
            if "Gemini 指令執行" in line or "Task" in line or "Gemini 正在思考" in line:
                continue
            final_lines.append(line.strip())
            
        final_text = "\n".join(final_lines).strip()
        return final_text if final_text else None
    except subprocess.CalledProcessError as e:
        print(f"❌ Fab Ask 呼叫失敗: {e.output}")
        return None
    except Exception as e:
        print(f"❌ 發生例外錯誤: {e}")
        return None

def run_batch_enrichment(limit=10):
    print("🚀 啟動 L3 大歷史語意批次厚化作業 (斷點續傳機制)...")
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 找尋: 
    # 1. 在曾文溪流域內 (透過 l4_topology 檢查 <= 5000m 或者 最近水系是這幾個)
    # 2. 目前 enrichment_level 還是 2 (表示還沒做 L3)
    cursor.execute("""
        SELECT * FROM archaeological_sites 
        WHERE enrichment_level < 3 
        AND meta_data LIKE '%最近水系%'
    """)
    all_eligible_sites = cursor.fetchall()
    
    # Filter memory for those really close to Zengwen system
    # We will pick sites whose closest river is in our Zengwen subset.
    zengwen_rivers = ['曾文溪', '菜寮溪', '官田溪', '後堀溪', '密枝溪', '後旦溪', '油車溪', '灣丘溪']
    
    target_sites = []
    for row in all_eligible_sites:
        try:
            meta = json.loads(row['meta_data'])
            if 'l4_topology' in meta:
                closest = meta['l4_topology'].get('最近水系', '')
                dist = meta['l4_topology'].get('距離最近水系_公尺', 99999)
                # Only pick sites actually related geographically to the basin (< 5000m to one of the rivers)
                if closest in zengwen_rivers and dist < 5000:
                    target_sites.append((row, meta))
        except:
            continue
            
    print(f"📌 掃描完畢：找到 {len(target_sites)} 筆符合曾文溪流域且等待 L3 厚化的遺址。")
    print(f"🎯 本次預計處理數量: {limit} 筆。")
    print("-" * 60)
    
    processed_count = 0
    
    for row, meta in target_sites:
        if processed_count >= limit:
            break
            
        site_id = row['site_id']
        name = row['name']
        print(f"[{processed_count + 1}/{limit}] 正在處理遺址: {name} ({site_id})...")
        
        # Prepare input data
        site_data = {
            'name': name,
            'cultural_period': row['cultural_period'],
            'is_multicomponent': bool(row['is_multicomponent']),
            'importance_rank': row['importance_rank'],
            'site_function': json.loads(row['site_function'] or '[]'),
            'l4_topology': meta.get('l4_topology', {})
        }
        
        # Call API
        context_text = generate_historical_context(site_data)
        
        if context_text:
            # Update meta
            meta['historical_context'] = context_text
            
            # Save to DB and bump enrichment_level
            try:
                cursor.execute("""
                    UPDATE archaeological_sites 
                    SET meta_data = ?, enrichment_level = 3 
                    WHERE site_id = ?
                """, (json.dumps(meta, ensure_ascii=False), site_id))
                conn.commit()
                print(f"   ✅ 成功生成並寫入 DB！")
                # print(f"   📝 預覽: {context_text[:50]}...")
            except Exception as e:
                print(f"   ❌ 資料庫更新失敗: {e}")
        else:
            print(f"   ⚠️ 跳過 {name}，生成失敗。")
            
        processed_count += 1
        time.sleep(2) # Rate limiting protection
        
    conn.close()
    print("-" * 60)
    print(f"🎉 批次作業結束。成功處理 {processed_count} 筆。")

if __name__ == "__main__":
    run_batch_enrichment(limit=50)
