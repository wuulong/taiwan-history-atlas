# Taiwan History Atlas (臺灣歷史知識地圖)

本專案將連橫所著之《臺灣通史》數位化，並透過 AI 進行跨維度實體萃取與知識建模，建構出具備「原始史料、結構實體、合成洞察」三層架構的歷史地理知識庫 (HGIS)。

---

## 🏛️ 資料庫架構 (Knowledge Layering)

本專案的核心資產為 `data/taiwan_history.db`，其遵循三層知識演進邏輯：

### 1. Layer 0: 原始文本層 (Raw Corpus)
- **Table**: `volumes`, `contents`
- **內容**: 全書 37 卷、88 篇、約 60 萬字原文。包含目錄索引與卷次分類，支援 FTS5 全文檢索。

### 2. Layer 1: 結構實體層 (Atomic Entities)
- **Table**: `entities`, `mentions`
- **內容**: 透過 AI 萃取的 3,000+ 個基礎實體。包含：
  - **人名 (Person)**: 拓墾者、官員、受試者。
  - **地名 (Location)**: 古聚落、社名、行政區。
  - **水利 (Irrigation)**: 埤圳、隧道、水源。
  - **官職 (Official_Post)**: 巡撫、知府、同知。

### 3. Layer 2: 知識中樞層 (AI Synthesized Atlas)
- **Table**: `ai_knowledge_atlas`
- **內容**: 由 AI 針對特定主題進行跨卷次分析後的合成模型。
  - **Eco_System**: 全台水利開發矩陣。
  - **Economy**: 樟腦、糖、茶、鹽經濟鏈。
  - **Gov_Structure**: 歷代政權演變與權力結構。
  - **Conflict_Logic**: 民變、械鬥與外交衝突因果鏈。
  - **Toponym_Ref**: 地名古今對照與演進矩陣。

---

## 🛠️ 腳本說明 (Scripts Toolkit)

本專案提供一系列 Python 工具，支援從資料獲取到空間分析的完整流程：

| 腳本名稱 | 功能描述 |
| :--- | :--- |
| `build_history_db.py` | 初始化資料庫，匯入原始文本並建立檢索索引。 |
| `extract_entities.py` | 執行 AI 實體萃取與分類。 |
| `geo_coding.py` | 將歷史地名與內政部/中研院古地名庫進行座標對齊。 |
| `ingest_*.py` | 專項建模腳本（水利、經濟、衝突、地名等知識資產入庫）。 |
| `export_kml.py` | 將具備座標的歷史實體匯出為 KML，供 Google Earth/QGIS 使用。 |
| `flexible_db_dump.py` | 彈性匯出特定卷次內容，供 AI 做進一步深度研讀。 |

---

## 🔍 資料範例 (Data Examples)

### 知識中樞範例 (ai_knowledge_atlas)
| category | subject | semantic_summary |
| :--- | :--- | :--- |
| **Eco_System** | 全臺歷史埤圳清單 | 結構化 226 筆埤圳數據，包含開鑿者與水源脈絡。 |
| **Economy** | 樟腦產業權力演進鏈 | 紀錄從私熬、英資到劉銘傳官辦改革的經濟轉向。 |

### 空間實體範例 (entities)
| name | type | meta_data (JSON) |
| :--- | :--- | :--- |
| **隆恩圳** | Irrigation | `{"origin": "施世榜", "river": "大肚溪", "area": "彰化"}` |

---

## 🤖 Agentic AI 使用案例

本資料庫專為 Agentic AI 設計，以下為建議的查詢模式：

### 案例 A：跨時空因果分析
> **Query**: "分析清代臺灣中部械鬥後，行政區域劃分的變遷邏輯。"
> **AI Action**: 先從 `Conflict_Logic` 提取械鬥模式，再 Join `Toponym_Ref` 查看後續的設縣 (如雲林縣、苗慄縣) 紀錄。

### 案例 B：流域開發 DNA 追蹤
> **Query**: "找出新竹地區王世傑家族開發的所有水利設施，並產出座標以便實地勘查。"
> **AI Action**: 查詢 `entities` 中 `type='Irrigation'` 且與「王世傑」相關的 `mentions`，最終利用 `geo_coding` 輸出座標。

---

## 📖 如何貢獻
- **資料庫 Schema**: 詳見 `docs/schema.sql`。
- **研究紀錄**: 詳見 `docs/RESEARCH_LOG_260222.md`。

本數位化專案遵循 MIT 授權。原始文本屬公有領域。
