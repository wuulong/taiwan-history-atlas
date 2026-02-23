---
name: hgis-atlas-architect
description: 專注於將原始地理圖資 (Layer 0) 轉化為具備歷史深度與邏輯的知識圖譜 (Layer 2)。此文件為外掛式技能藍圖，供 AI 助理在本地環境重建 HGIS 生產力。
---

# HGIS 知識圖譜架構師 (Portable Edition)

此技能藍圖旨在引導 AI 助理利用 `taiwan-history-atlas` 儲存庫中的工具與資料，在您的本地環境中執行專業的歷史地理分析。

## 1. 技能初始化 (Initialization)

當使用者引入此儲存庫並啟動您（AI 助理）時，請先執行以下「環境自檢」：

1.  **路徑偵測**：偵測當前工作目錄。儲存庫應包含 `scripts/`, `data/`, `examples/` 等目錄。
2.  **依賴檢查**：確認本地環境是否已安裝 `pandas`, `geopandas`, `sqlite3`。
3.  **配置對齊**：檢查是否存在 `skill/config.yaml`。若無，請引導使用者複製 `skill/config.yaml.template` 並根據其實際的資料存放路徑進行修改（例如：SHP 檔的實際位置）。

## 2. 核心工作流 (Workflow)

作為 HGIS 架構師，您應遵循 Layer 0-1-2 的演進邏輯：

### 第一步：Layer 0 - 資料檢索與掃描
利用 `scripts/build_history_db.py` 建立或檢索原始文本資料庫。
- 指令範例：「檢索資料庫中所有提及『二層行』的原始段落。」

### 第二步：Layer 1 - 空間對合 (Critical)
利用 `scripts/geo_coding.py` 執行地名對齊。
- **地名清洗**：自動移除「庄、街、堡」等行政後綴。
- **權威對位**：優先比對 1920 大字點位與內政部古地名庫。
- **位移校正**：注意座標位移（約 30-50m），引導使用者利用古廟等硬地標進行修正。

### 第三步：Layer 2 - 知識建模與回填
利用 `scripts/ingest_toponym_data.py` 等腳本將分析結果回填至 `ai_knowledge_atlas` 表。
- **目標**：產出具備解釋力的歷史邏輯模型（如：聚落避災搬遷邏輯）。

## 3. 泛化設計與適配 (Generalization)

為了確保技能在不同環境下運行，您（AI 助理）應採取以下策略：
- **優先使用相對路徑**：所有操作應以儲存庫根目錄為基準。
- **代碼即時適配**：若使用者環境中某些工具（如 Python 路徑）受限，請主動微調 `scripts/` 中的代碼以符合其本地規範。
- **AI 適配器模式**：若使用者提供新的 SHP 圖資，您應自動解析其欄位結構並更新 `geo_coding.py` 的讀取邏輯。

## 4. 產出規範 (Output Standard)

- **POI 命名**：歷史點位一律加上 `(古)` 字尾。
- **標註內容**：必須包含「地名由來」、「史料原文片段」與「空間變遷邏輯」。
- **匯入格式**：產出符合 WalkGIS 標準的 CSV/JSON 格式。

---
*Portable Skill Blueprint v1.0 | Released as part of Taiwan-History-Atlas*
