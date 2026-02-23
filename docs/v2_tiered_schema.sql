-- HGIS Region History Database Schema Template v2.0 (L0-L1)
-- 採用三層架構：Documents -> Volumes -> Contents

-- 0. 文獻表：存放史料的基本元數據
CREATE TABLE documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT UNIQUE,    -- 書名 (如：新竹縣採訪冊)
    author TEXT,          -- 作者 (如：陳培桂)
    dynasty TEXT,         -- 編纂年代 (如：清、日治)
    published_year TEXT,  -- 出版/完稿年份
    category TEXT,        -- 分類 (如：地方志、私人採錄)
    description TEXT,     -- 文獻價值與內容概述
    meta_data TEXT        -- 原始版本資訊、數位化來源 (JSON)
);

-- 1. 卷次表：記錄文獻的章節結構
CREATE TABLE volumes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_id INTEGER,       -- 關聯之文獻
    vol_num_str TEXT,     -- 卷號 (如：卷一)
    title TEXT,           -- 篇名 (如：山川)
    category TEXT,        -- 分類 (如：志、傳、序)
    summary TEXT,         -- 卷次內容摘要
    meta_data TEXT,       -- 原始卷次標記 (JSON)
    FOREIGN KEY(doc_id) REFERENCES documents(id)
);

-- 2. 內容表：存儲原始文本片段
CREATE TABLE contents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vol_id INTEGER,       -- 關聯之卷次
    line_num INTEGER,     -- 原始行號 (L0 溯源用)
    raw_text TEXT,        -- 原始文本內容
    sub_title TEXT,       -- 小節標題 (如有)
    meta_data TEXT,       -- 語意標籤 (JSON)
    FOREIGN KEY(vol_id) REFERENCES volumes(id)
);

-- 3. 實體表：存放各類歷史物件
CREATE TABLE entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,     -- 實體標準名稱
    type TEXT,            -- 類型 (Person, Location, Infrastructure, Event)
    description TEXT,     -- 基礎描述
    meta_data TEXT        -- 屬性特徵 (JSON)
);

-- 4. 提及表：連結實體與原始文本 (Mentions)
CREATE TABLE mentions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id INTEGER,    -- 關聯之實體
    content_id INTEGER,   -- 出現之文本片段
    snippet TEXT,         -- 上下文片段 (L1 考證用)
    confidence REAL,      -- AI 萃取置信度
    meta_data TEXT,       -- 角色標註 (JSON)
    FOREIGN KEY(entity_id) REFERENCES entities(id),
    FOREIGN KEY(content_id) REFERENCES contents(id)
);

-- 5. 空間對合表：紀錄空間實體的座標 (Geo-coding)
CREATE TABLE spatial_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id INTEGER,    -- 關聯之實體
    longitude REAL,       -- WGS84 經度
    latitude REAL,        -- WGS84 緯度
    accuracy TEXT,        -- 精度級別
    dtm_elevation REAL,   -- DTM 高程
    meta_data TEXT,       -- 錨定邏輯與置信度 (JSON)
    FOREIGN KEY(entity_id) REFERENCES entities(id)
);

-- 6. 編年表：紀錄時間事件
CREATE TABLE chronology (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_id INTEGER,   -- 關連之文本片段
    year_ad INTEGER,      -- 西元年份
    year_era TEXT,        -- 歷史紀年
    event_summary TEXT,   -- 事件摘要
    meta_data TEXT,       -- 分類 (JSON)
    FOREIGN KEY(content_id) REFERENCES contents(id)
);

-- 索引優化
CREATE INDEX idx_docs_title ON documents(title);
CREATE INDEX idx_vols_doc ON volumes(doc_id);
CREATE INDEX idx_contents_vol ON contents(vol_id);
CREATE INDEX idx_entities_name ON entities(name);
CREATE INDEX idx_mentions_entity ON mentions(entity_id);
