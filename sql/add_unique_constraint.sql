-- Migration script to add unique constraint to user_groups table
-- This prevents duplicate join requests from the same user to the same group

-- First, remove any duplicate entries (keep the first one for each user-group combination)
DELETE FROM user_groups 
WHERE id NOT IN (
    SELECT MIN(id) 
    FROM user_groups 
    GROUP BY user_id, group_id
);

-- Add the unique constraint
CREATE UNIQUE INDEX IF NOT EXISTS idx_user_groups_unique 
ON user_groups (user_id, group_id); 