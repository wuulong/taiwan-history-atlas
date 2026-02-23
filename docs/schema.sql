-- HGIS Tiered Architecture Master Schema (v2.0)
-- This file defines the structures for both Regional/Source DBs (L1) and the Central Knowledge Atlas (L2).

-- ==========================================
-- LAYER 1: Regional/Source Database Structure
-- ==========================================

-- 1.0 Document Level (Metadata for the source text)
CREATE TABLE documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT UNIQUE,    -- e.g., '新竹縣採訪冊'
    author TEXT,
    dynasty TEXT,
    published_year TEXT,
    category TEXT,        -- e.g., 'Gazetteer'
    description TEXT,
    meta_data TEXT        -- JSON
);

-- 1.1 Volume Level (Structural headings)
CREATE TABLE volumes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_id INTEGER,
    vol_num_str TEXT,     -- e.g., '卷一'
    title TEXT,           -- e.g., '山川'
    category TEXT,
    summary TEXT,
    meta_data TEXT,
    FOREIGN KEY(doc_id) REFERENCES documents(id)
);

-- 1.2 Content Level (Raw text segments)
CREATE TABLE contents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vol_id INTEGER,
    line_num INTEGER,
    raw_text TEXT,
    sub_title TEXT,
    meta_data TEXT,
    FOREIGN KEY(vol_id) REFERENCES volumes(id)
);

-- 1.3 Entity Level (Extracted historical objects)
CREATE TABLE entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    type TEXT,            -- Person, Location, etc.
    description TEXT,
    meta_data TEXT
);

-- 1.4 Mention Level (Linkage between text and entities)
CREATE TABLE mentions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id INTEGER,
    content_id INTEGER,
    snippet TEXT,
    confidence REAL,
    meta_data TEXT,
    FOREIGN KEY(entity_id) REFERENCES entities(id),
    FOREIGN KEY(content_id) REFERENCES contents(id)
);

-- 1.5 Spatial Level (Geocoding)
CREATE TABLE spatial_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id INTEGER,
    longitude REAL,
    latitude REAL,
    accuracy TEXT,
    dtm_elevation REAL,
    meta_data TEXT,
    FOREIGN KEY(entity_id) REFERENCES entities(id)
);

-- ==========================================
-- LAYER 2: Central Knowledge Atlas Structure
-- ==========================================
-- (Lives in history_atlas.db)

CREATE TABLE knowledge_atlas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_origin TEXT,    -- e.g., 'Global', 'Hsinchu', 'Zengwen'
    category TEXT,         -- e.g., 'Eco_System', 'Gov_Org'
    subject TEXT,          -- e.g., '全台重要歷史陂圳清單'
    data_payload TEXT,     -- Core data (JSON)
    semantic_summary TEXT, -- Human-readable summary
    source_db_path TEXT,   -- Lineage: path to original L1 DB
    original_id INTEGER,   -- Lineage: ID in original L1 table
    version_tag TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
