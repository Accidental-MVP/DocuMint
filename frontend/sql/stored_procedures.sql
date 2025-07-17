-- Stored procedures for DocuMint

-- Create a function to record token usage (atomic transaction)
CREATE OR REPLACE FUNCTION public.record_token_usage(
  p_user_id UUID,
  p_tokens_used INTEGER,
  p_source TEXT DEFAULT 'web',
  p_endpoint TEXT DEFAULT 'generate'
)
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  -- Update the user's token usage
  UPDATE public.users
  SET tokens_used = tokens_used + p_tokens_used,
      updated_at = now()
  WHERE id = p_user_id;
  
  -- Record the token usage entry
  INSERT INTO public.token_usage (
    user_id,
    date,
    tokens_used,
    source,
    endpoint
  ) VALUES (
    p_user_id,
    CURRENT_DATE,
    p_tokens_used,
    p_source,
    p_endpoint
  );
END;
$$;

-- Create a function to create a user if they don't exist
CREATE OR REPLACE FUNCTION public.create_user_if_not_exists(
  user_id UUID,
  user_email TEXT
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER -- This is important as it runs with the privileges of the function creator
AS $$
DECLARE
  v_result JSONB;
BEGIN
  -- Check if the user already exists
  IF EXISTS (SELECT 1 FROM public.users WHERE id = user_id) THEN
    -- Update the existing user
    UPDATE public.users
    SET 
      email = user_email,
      updated_at = NOW()
    WHERE id = user_id
    RETURNING jsonb_build_object('id', id, 'email', email) INTO v_result;
  ELSE
    -- Insert a new user
    INSERT INTO public.users (
      id,
      email,
      auth_provider,
      created_at,
      updated_at
    ) VALUES (
      user_id,
      user_email,
      'email',
      NOW(),
      NOW()
    )
    RETURNING jsonb_build_object('id', id, 'email', email) INTO v_result;
  END IF;
  
  RETURN v_result;
END;
$$;

-- Create a function to increment a value (used for counters)
CREATE OR REPLACE FUNCTION public.increment(inc INTEGER)
RETURNS INTEGER
LANGUAGE sql
IMMUTABLE
AS $$
  SELECT $1;
$$;

-- Create a function to reset token usage on quota reset date
CREATE OR REPLACE FUNCTION public.reset_token_quota()
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  UPDATE public.users
  SET tokens_used = 0,
      quota_reset_date = (now() + INTERVAL '1 month'),
      updated_at = now()
  WHERE quota_reset_date <= now();
END;
$$;

-- Create a function to create an API key
CREATE OR REPLACE FUNCTION public.create_api_key(
  p_user_id UUID,
  p_name TEXT
)
RETURNS TEXT
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_key TEXT;
BEGIN
  -- Generate a random API key
  v_key := encode(gen_random_bytes(32), 'hex');
  
  -- Insert the API key
  INSERT INTO public.api_keys (
    user_id,
    key,
    name
  ) VALUES (
    p_user_id,
    v_key,
    p_name
  );
  
  RETURN v_key;
END;
$$;

-- Create a function to validate an API key
CREATE OR REPLACE FUNCTION public.validate_api_key(
  p_key TEXT
)
RETURNS UUID
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_user_id UUID;
BEGIN
  -- Get the user ID for the API key
  SELECT user_id INTO v_user_id
  FROM public.api_keys
  WHERE key = p_key
  AND is_active = TRUE;
  
  -- Update last_used timestamp
  IF v_user_id IS NOT NULL THEN
    UPDATE public.api_keys
    SET last_used = now()
    WHERE key = p_key;
  END IF;
  
  RETURN v_user_id;
END;
$$; 