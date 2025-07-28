-- Add file fields to jobs table
ALTER TABLE jobs ADD COLUMN quote_file TEXT;
ALTER TABLE jobs ADD COLUMN job_file TEXT; 