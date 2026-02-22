# Taiwan History Atlas (臺灣歷史知識地圖)

本專案將連橫所著之《臺灣通史》數位化，並透過 AI 進行實體萃取與知識建模，建立具備多層結構的歷史地理知識庫 (HGIS)。

## 📁 目錄結構

- `data/`: 包含核心 SQLite 資料庫 `taiwan_history.db`。
- `scripts/`: 用於建立資料庫、萃取實體及入庫知識模型的腳本。
- `docs/`: 專案文件與分析報告。

## 🏛️ 資料庫架構 (Three-Layer Architecture)

1. **Layer 0 (Raw Text)**: 全書原文與卷次索引。
2. **Layer 1 (Entities)**: 自動萃取的 3,000+ 歷史實體（人名、地名、職官等）。
3. **Layer 2 (Knowledge Atlas)**: 由 AI 合成的結構化知識模型，涵蓋：
   - 水利系統 (Eco_System)
   - 經濟貿易 (Economy)
   - 官職權力 (Gov_Structure)
   - 衝突邏輯 (Conflict_Logic)
   - 地名演進 (Toponym_Ref)

## 🚀 快速開始

### 資料庫查詢範例
使用 SQLite 即可探索歷史脈絡：
```sql
-- 查詢特定作者相關的所有段落
SELECT m.snippet FROM mentions m JOIN entities e ON m.entity_id = e.id WHERE e.name = '王世傑';

-- 獲取 AI 指引
SELECT data_payload FROM ai_knowledge_atlas WHERE category = 'AI_Guidance';
```

## 📜 授權
本數位化專案遵循 MIT 授權。原始文本屬公有領域。
