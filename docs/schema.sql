CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE volumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vol_num_str TEXT,     -- 卷一, 卷二
        title TEXT,           -- 開闢紀, 貨殖列傳
        category TEXT,        -- 紀/志/傳/序
        summary TEXT
    , meta_data TEXT);
CREATE TABLE contents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vol_id INTEGER,
        line_num INTEGER,
        raw_text TEXT, meta_data TEXT, sub_title TEXT,
        FOREIGN KEY(vol_id) REFERENCES volumes(id)
    );
CREATE VIRTUAL TABLE contents_fts USING fts5(
        raw_text, 
        content='contents', 
        content_rowid='id'
    )
/* contents_fts(raw_text) */;
CREATE TABLE IF NOT EXISTS 'contents_fts_data'(id INTEGER PRIMARY KEY, block BLOB);
CREATE TABLE IF NOT EXISTS 'contents_fts_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID;
CREATE TABLE IF NOT EXISTS 'contents_fts_docsize'(id INTEGER PRIMARY KEY, sz BLOB);
CREATE TABLE IF NOT EXISTS 'contents_fts_config'(k PRIMARY KEY, v) WITHOUT ROWID;
CREATE TABLE entities (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, type TEXT, description TEXT, meta_data TEXT);
CREATE TABLE mentions (id INTEGER PRIMARY KEY AUTOINCREMENT, entity_id INTEGER, content_id INTEGER, snippet TEXT, confidence REAL, meta_data TEXT, FOREIGN KEY(entity_id) REFERENCES entities(id), FOREIGN KEY(content_id) REFERENCES contents(id));
CREATE TABLE spatial_links (id INTEGER PRIMARY KEY AUTOINCREMENT, entity_id INTEGER, longitude REAL, latitude REAL, accuracy TEXT, dtm_elevation REAL, meta_data TEXT, FOREIGN KEY(entity_id) REFERENCES entities(id));
CREATE TABLE chronology (id INTEGER PRIMARY KEY AUTOINCREMENT, content_id INTEGER, year_ad INTEGER, year_era TEXT, event_summary TEXT, meta_data TEXT, FOREIGN KEY(content_id) REFERENCES contents(id));
CREATE TABLE moi_settlements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT,
        place_name TEXT,
        chinese_phonetic TEXT,
        common_phonetic TEXT,
        another_name TEXT,
        county TEXT,
        county_code TEXT,
        town TEXT,
        town_code TEXT,
        village TEXT,
        place_mean TEXT,      -- 歷史淵源/地名意義
        longitude REAL,
        latitude REAL,
        meta_data TEXT        -- 保留擴充性
    );
CREATE INDEX idx_moi_placename ON moi_settlements(place_name);
CREATE INDEX idx_moi_county ON moi_settlements(county);
CREATE INDEX idx_moi_town ON moi_settlements(town);
CREATE TABLE ai_knowledge_atlas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT,        -- 分類：'Taxonomy', 'Gov_Org', 'Eco_System', 'Chronology'
    subject TEXT,         -- 主題：'原住民生活樣態矩陣', '撫墾局管轄體系'
    scope_vol_id INTEGER, -- 關聯的卷次 (若為跨卷分析則為 NULL)
    data_payload TEXT,    -- 核心數據結構 (JSON)
    semantic_summary TEXT, -- 語義摘要
    version_tag TEXT,     -- 分析版本
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
