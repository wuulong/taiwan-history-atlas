# Taiwan History Atlas (臺灣歷史知識地圖)

本專案將連橫所著之《臺灣通史》數位化，並透過 AI 進行跨維度實體萃取與知識建模，建構出具備「原始史料、結構實體、合成洞察」三層架構的歷史地理知識庫 (HGIS)。

---

## 📁 目錄結構

- `data/`: 包含核心 SQLite 資料庫 `taiwan_history.db`。
- `scripts/`: 用於建立資料庫、萃取實體及入庫知識模型的腳本集。
- `skill/`: **[NEW]** AI 助理技能藍圖，包含 `SKILL.md` 指令集與配置範本。
- `examples/`: 提供 AI 分析實例與專修摘要（如：王世傑列傳摘要）。
- `docs/`: 專案文件、分析報告與資料庫 Schema。

---

## 🤖 AI Agentic Skill (HGIS Architect)

本專案不僅提供資料，更提供一套 **「AI 協作技能藍圖」**。您可以將此儲存庫引入您的 AI 助理環境（如 Claude, ChatGPT, Gemini 等代理介面），讓它具備專業的 HGIS 分析能力。

### 啟動方式
1. 將此 Repo 交給您的 AI 助理。
2. 讓 AI 助理閱讀 `skill/SKILL.md`。
3. 它是「外掛式知識引擎」，能引導 AI 自動處理史料數據、執行空間對合，並產出具備深度歷史感的流域導覽資訊。

> **小技巧**：若您的環境路徑不固定，請引導 AI 讀取 `skill/config.yaml.template` 進行自動適配。

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

## � AI 助理 / Antigravity 使用指南

如果您在使用具備 Agentic 能力的 AI 助理（如 Antigravity, Claude Engineer 等），可以按照以下步驟快速讓助理掌握這些史料：

### 1. 建立連結 (Setup)
將本 Repo 載入到您的助理可存取的工作目錄中，並告知助理資料庫的路徑：
> **Prompt**: 「我現在要開始研究台灣歷史。請使用 `data/taiwan_history.db` 作為知識庫。你可以先查看其 `ai_knowledge_atlas` 表來了解目前的建模成果。」

### 2. 資料庫導航 (Self-Discovery)
讓 AI 助理自我探索資料庫結構，獲取「導航指引」：
> **Prompt**: 「請查詢 `ai_knowledge_atlas` 表中 `category='AI_Guidance'` 的內容，這包含了我為你準備的資料庫操作最佳實踐與常用的 SQL 指令。」

### 3. 研究實戰 (Sample Prompts)
您可以直接使用以下指令進行深度研究：
- **深度挖掘**：「請從《農業志》中分析清代新竹地區的水利開發歷史，並列出所有相關的埤圳與開鑿者。」
- **區域發展研究**：「比較清代『南糖北茶』的地理分佈特徵，並從經濟資源分配的角度分析為何省會最終移往臺北。」
- **空間考證**：「找出《臺灣通史》中提到『王世傑』的所有地點，並嘗試將這些點名對齊現代座標（可調用 `geo_coding.py` 邏輯），最後匯出一個 KML 檔案給我。」

### 4. 三層分析心法
建議引導助理遵循本專案設計的 **「三層分析模式」**：
1. **先查 Atlas (L2)**：獲取系統性的專題摘要。
2. **再下鑽 Entities (L1)**：取得具體人名、地名與座標。
3. **最後對照文本 (L0)**：讀取 `mentions` 中的原文片段 (snippet) 以確保史實精確。

---

## �📖 技術內容
- **資料庫 Schema**: 詳見 `docs/schema.sql`。
- **研究紀錄**: 詳見 `docs/RESEARCH_LOG_260222.md`。
## 📜 授權
本數位化專案採用 **CC0 1.0 通用 (CC0 1.0) 公眾領域貢獻宣告** 釋出。原始文本屬公有領域。
