-- Run this in Supabase SQL Editor
CREATE TABLE IF NOT EXISTS budgets (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE,
  amount REAL NOT NULL DEFAULT 5000,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE budgets ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users manage own budget" ON budgets
  FOR ALL USING (auth.uid() = user_id);
