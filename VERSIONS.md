# Taiwan History Atlas 版本紀錄 (VERSIONS.md)

本文件紀錄 `taiwan-history-atlas` 儲存庫的重大更新路徑，包含資料庫版本、AI 知識圖譜釋出以及技能組更新。

---

## [v260223.4] - 2026-02-23
### 🗺️ 新竹五書入庫與空間對合框架 (Hsinchu Regional Multi-book Integration)
- **多書結構化 (L0)**：運用 v2.0 架構，一次性匯入《新竹縣採訪冊》、《淡水廳志》、《樹杞林志》、《新竹縣志初稿》、《新竹縣制度考》五書，總計擴充 9,000+ 段史料片段。
- **三重空間清洗 (L1)**：針對 Location (聚落), Irrigation (水利), Infrastructure (交通與城防) 發展特定名稱清洗與語義去尾算法。
- **雙軌對合引擎 (Spatial Linkage)**：整合 1920 堡圖大字（Oaza）中心點與內政部古地名，自動為 821 個歷史實體打上精確的 WGS84 座標。
- **知識圖譜提煉 (L2)**：匯出「竹塹歷史聚落空間分佈」、「竹塹歷史水利開發網」、「竹塹歷史交通與防禦網」三大 Layer 2 JSON 模型，送入 `history_atlas.db` 中樞。
- **WalkGIS 對接**：成功轉化釋出「竹塹五書歷史知識地圖」POI。

---

## [v260223.3] - 2026-02-23 (Latest)
### 🏛️ L0-L1-L2 三層階梯式架構升級 (Tiered Architecture v2.0)
- **架構重塑**：實現「分區溯源 (L1) -> 集中中樞 (L2)」的工業級 HGIS 架構。
- **資料庫更新**：
    - `history_atlas.db` (L2 Atlas): 全新知識中樞，整合 21 筆全台級合成知識。
    - `taiwan_history.db` (L1 v2.0): 引入 `Documents -> Volumes -> Contents` 三級文本管理，支援單庫多文獻。
- **工具釋出**：
    - `scripts/atlas_migrator.py`: 支援跨資料庫的知識實體遷移與來源標註。
    - `docs/v2_tiered_schema.sql`: 發布新一代 HGIS 數據交換標準。

---

## [v260223.2] - 2026-02-23
### 🚀 專業化 AI 技能封裝 (Skill-First Release)
- **新增**：`skill/SKILL.md` 外掛式 AI 指令集，支援代理程式自動化 HGIS 分析。
- **優化**：全腳本 `scripts/` 去耦合化，建立 `config.py` 標準路徑配置與 AI 適配機制。
- **新增**：`scripts/config.py` 統一管理資料庫、文本與 SHP 路徑。

---

## [v260223.1] - 2026-02-23
### 🌊 流域 HGIS 知識厚化 (River Basins Enrichment)
- **資料庫更新 (`ai_knowledge_atlas` 表)**：
    - `v260223.1-Zengwen`: 曾文溪流域 696 個厚數據 POI、五塊厝/蘇厝考證邏輯入庫。
    - `v260223.1-Erren`: 二仁溪流域 463 個厚數據 POI、界河糧倉中洲社倉邏輯入庫。
- **功能**：確立「15 分鐘極速對合」SOP，整合內政部古地名庫與《臺灣通史》文本。

---

## [v260222.1] - 2026-02-22
### 🏛️ 三層架構基礎版本 (Layer 0-1-2 Foundation)
- **核心釋出**：建立 `taiwan_history.db` 初期結構。
- **Layer 0**：全量匯入《臺灣通史》37 卷原文，支援 FTS5 全文檢索。
- **Layer 1**：初步萃取 3,000+ 個地名、人名與水利實體。
- **Layer 2**：發布首批「地名演進矩陣」與「水利開發邏輯模型」。
- **工具**：發布 `build_history_db.py`, `geo_coding.py` 等基礎腳本。

---

## 未來規劃 (Roadmap)
- [ ] 整合 1920s 全台大字中心點座標至 `moi_settlements` 擴展表。
- [ ] 支援更多方志文本（如《重修臺灣府志》）的 Layer 0 載入。
- [ ] 強化 AI 對「宗族遷徙」與「林爽文事件」的專題建模。
