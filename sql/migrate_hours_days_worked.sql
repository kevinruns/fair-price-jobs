-- Migration to add hours_worked and days_worked columns to jobs table

-- Add hours_worked column
ALTER TABLE jobs ADD COLUMN hours_worked REAL NULL;

-- Add days_worked column
ALTER TABLE jobs ADD COLUMN days_worked REAL NULL; 