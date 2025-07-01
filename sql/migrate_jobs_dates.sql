-- Migration to add date_started and date_finished columns to jobs table
-- This will replace the single 'date' column with separate start and finish dates

-- Add new columns
ALTER TABLE jobs ADD COLUMN date_started TEXT;
ALTER TABLE jobs ADD COLUMN date_finished TEXT;

-- Copy existing date data to date_finished (assuming the single date was the completion date)
UPDATE jobs SET date_finished = date WHERE date IS NOT NULL;

-- Drop the old date column
-- Note: SQLite doesn't support DROP COLUMN directly, so we'll need to recreate the table
-- For now, we'll keep the old column and use the new ones going forward 