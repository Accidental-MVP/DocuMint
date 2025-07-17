-- Production-grade SaaS schema for DocuMint
-- This creates a robust database structure for user management, API keys, token usage, and more

-- 🧱 1. `users` Table – The Soul of Your SaaS
CREATE TABLE public.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    username TEXT UNIQUE, -- optional handle
    avatar_url TEXT,

    -- Auth Info
    auth_provider TEXT NOT NULL DEFAULT 'email', -- 'email', 'google', etc.
    hashed_password TEXT, -- NULL if OAuth
    email_verified BOOLEAN DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now(),
    last_login TIMESTAMP,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_banned BOOLEAN DEFAULT FALSE,
    ban_reason TEXT,

    -- Plan & Limits
    plan TEXT DEFAULT 'free', -- 'free', 'pro', 'enterprise'
    tokens_used INTEGER DEFAULT 0,
    tokens_quota INTEGER DEFAULT 10000,
    quota_reset_date TIMESTAMP,
    
    -- Billing
    stripe_customer_id TEXT,
    stripe_subscription_id TEXT,
    billing_cycle_anchor TIMESTAMP,

    -- Metadata
    locale TEXT DEFAULT 'en',
    timezone TEXT DEFAULT 'UTC',
    referral_code TEXT,
    referred_by UUID REFERENCES public.users(id),

    metadata JSONB
);

-- 🔑 2. `api_keys` Table – Programmatic Access
CREATE TABLE public.api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    key TEXT UNIQUE NOT NULL,
    name TEXT, -- user can name their key
    created_at TIMESTAMP DEFAULT now(),
    last_used TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- 📊 3. `token_usage` Table – Metered Billing, Usage Tracking
CREATE TABLE public.token_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    tokens_used INTEGER NOT NULL,
    source TEXT, -- e.g., 'web', 'api', 'cli'
    endpoint TEXT, -- which API endpoint

    created_at TIMESTAMP DEFAULT now()
);

-- 📜 4. `readme_history` Table – Save Generated Content
CREATE TABLE public.readme_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    repo_url TEXT NOT NULL,
    content TEXT NOT NULL,
    model_used TEXT,
    generation_mode TEXT,
    token_cost INTEGER,

    created_at TIMESTAMP DEFAULT now()
);

-- 🧾 5. `plans` Table – Metadata for Pricing Tiers
CREATE TABLE public.plans (
    id TEXT PRIMARY KEY, -- 'free', 'pro', 'enterprise'
    name TEXT,
    monthly_price INTEGER,
    yearly_price INTEGER,
    token_quota INTEGER,
    features JSONB,
    stripe_price_id_monthly TEXT,
    stripe_price_id_yearly TEXT
);

-- Insert default plans
INSERT INTO public.plans (id, name, monthly_price, yearly_price, token_quota, features)
VALUES 
('free', 'Free', 0, 0, 10000, '{"repositories": 1, "advanced_generation": false}'::jsonb),
('pro', 'Pro', 1000, 10000, 100000, '{"repositories": 10, "advanced_generation": true}'::jsonb),
('enterprise', 'Enterprise', 5000, 50000, 1000000, '{"repositories": -1, "advanced_generation": true, "priority_support": true}'::jsonb);

-- Add foreign key from users to auth.users
ALTER TABLE public.users 
ADD CONSTRAINT users_auth_id_fkey 
FOREIGN KEY (id) REFERENCES auth.users(id) ON DELETE CASCADE;

-- 🔐 Row-Level Security (RLS) Policies

-- Enable RLS on all tables
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.token_usage ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.readme_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.plans ENABLE ROW LEVEL SECURITY;

-- Users table policies
CREATE POLICY "Users can view their own data" 
ON public.users FOR SELECT 
USING (id = auth.uid());

CREATE POLICY "Users can update their own data" 
ON public.users FOR UPDATE 
USING (id = auth.uid());

-- API Keys policies
CREATE POLICY "Users can view their own API keys" 
ON public.api_keys FOR SELECT 
USING (user_id = auth.uid());

CREATE POLICY "Users can create their own API keys" 
ON public.api_keys FOR INSERT 
WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can update their own API keys" 
ON public.api_keys FOR UPDATE 
USING (user_id = auth.uid());

CREATE POLICY "Users can delete their own API keys" 
ON public.api_keys FOR DELETE 
USING (user_id = auth.uid());

-- Token Usage policies
CREATE POLICY "Users can view their own token usage" 
ON public.token_usage FOR SELECT 
USING (user_id = auth.uid());

-- README History policies
CREATE POLICY "Users can view their own README history" 
ON public.readme_history FOR SELECT 
USING (user_id = auth.uid());

CREATE POLICY "Users can create their own README history" 
ON public.readme_history FOR INSERT 
WITH CHECK (user_id = auth.uid());

-- Plans policies (everyone can view plans)
CREATE POLICY "Anyone can view plans" 
ON public.plans FOR SELECT 
USING (true);

-- Create a function to handle new user registration
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.users (id, email, auth_provider, email_verified)
  VALUES (
    NEW.id, 
    NEW.email,
    COALESCE(NEW.raw_app_meta_data->>'provider', 'email'),
    NEW.email_confirmed_at IS NOT NULL
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create a trigger to automatically add new users
CREATE OR REPLACE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Create a function to update user login timestamp
CREATE OR REPLACE FUNCTION public.handle_user_login()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE public.users
  SET last_login = now(), updated_at = now()
  WHERE id = NEW.id;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create a trigger to update last_login on auth sign-in
CREATE OR REPLACE TRIGGER on_auth_user_signed_in
  AFTER UPDATE OF last_sign_in_at ON auth.users
  FOR EACH ROW
  WHEN (OLD.last_sign_in_at IS DISTINCT FROM NEW.last_sign_in_at)
  EXECUTE FUNCTION public.handle_user_login(); 