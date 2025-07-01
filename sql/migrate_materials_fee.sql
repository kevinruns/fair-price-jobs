-- Migration to add materials_fee column to jobs table

-- Add materials_fee column
ALTER TABLE jobs ADD COLUMN materials_fee INTEGER NULL; 