-- Migration 001: Drop extractions table, add user_id and modified to configs
-- This migration is for existing SQLite databases that have the old schema

-- Drop the extractions table (no longer needed)
DROP TABLE IF EXISTS texthunter_extractions;

-- Recreate configs table with new schema
-- First, rename the old table
ALTER TABLE texthunter_configs RENAME TO texthunter_configs_old;

-- Create new table with user_id and modified columns
CREATE TABLE texthunter_configs (
    id                    TEXT PRIMARY KEY,
    user_id               TEXT,
    name                  TEXT NOT NULL,
    keyword_regex         TEXT NOT NULL,
    file_identifier_regex TEXT,
    created_at            TEXT NOT NULL DEFAULT (datetime('now')),
    modified              TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(user_id, name)
);

-- Migrate existing data (user_id will be NULL for desktop users)
INSERT INTO texthunter_configs (id, name, keyword_regex, file_identifier_regex, created_at, modified)
    SELECT id, name, keyword_regex, file_identifier_regex, created_at, datetime('now')
    FROM texthunter_configs_old;

-- Clean up old table
DROP TABLE texthunter_configs_old;
