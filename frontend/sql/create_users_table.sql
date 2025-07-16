-- Create a users table that extends the auth.users table
-- First check if the table exists
CREATE TABLE IF NOT EXISTS public.users (
  id UUID PRIMARY KEY,
  email TEXT NOT NULL,
  username TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  last_sign_in TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  avatar_url TEXT,
  display_name TEXT,
  bio TEXT,
  website TEXT,
  role TEXT DEFAULT 'user'
);

-- Add foreign key if it doesn't exist (separate step to avoid errors)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint 
    WHERE conname = 'users_id_fkey' AND conrelid = 'public.users'::regclass
  ) THEN
    ALTER TABLE public.users 
    ADD CONSTRAINT users_id_fkey 
    FOREIGN KEY (id) REFERENCES auth.users(id) ON DELETE CASCADE;
  END IF;
END
$$;

-- Enable Row Level Security
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

-- Create policies (drop first to avoid errors if they already exist)
DROP POLICY IF EXISTS "Users are viewable by everyone" ON public.users;
CREATE POLICY "Users are viewable by everyone" 
  ON public.users FOR SELECT 
  USING (true);

DROP POLICY IF EXISTS "Users can update their own data" ON public.users;
CREATE POLICY "Users can update their own data" 
  ON public.users FOR UPDATE 
  USING (auth.uid() = id);

DROP POLICY IF EXISTS "Users can insert their own data" ON public.users;
CREATE POLICY "Users can insert their own data" 
  ON public.users FOR INSERT 
  WITH CHECK (auth.uid() = id);

-- Service role can do everything
DROP POLICY IF EXISTS "Service role can do everything" ON public.users;
CREATE POLICY "Service role can do everything"
  ON public.users
  USING (auth.jwt() ->> 'role' = 'service_role');

-- IMPORTANT: We're removing the triggers on auth.users table since they cause the
-- "Database error saving new user" error. Instead, we'll handle user creation
-- entirely from our application code.

-- Drop any existing triggers on auth.users table
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
DROP TRIGGER IF EXISTS on_auth_user_signed_in ON auth.users; 