-- Add new fields to tasks table for Phase 2
-- All fields nullable or have defaults for backward compatibility

-- Add category field (optional categorization)
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS category VARCHAR(50);

-- Add priority field (low, medium, high) with default
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS priority VARCHAR(20) DEFAULT 'medium';

-- Add due_date field (optional deadline)
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS due_date TIMESTAMP;

-- Add order field (for custom drag-drop ordering)
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS "order" INTEGER DEFAULT 0;

-- Add indexes for filtering performance
CREATE INDEX IF NOT EXISTS idx_tasks_category ON tasks(category);
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);
CREATE INDEX IF NOT EXISTS idx_tasks_order ON tasks("order");
