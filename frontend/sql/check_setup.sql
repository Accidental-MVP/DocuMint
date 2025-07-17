-- Check if tables exist
SELECT EXISTS (
  SELECT FROM information_schema.tables 
  WHERE table_schema = 'public' 
  AND table_name = 'users'
) AS users_table_exists;

SELECT EXISTS (
  SELECT FROM information_schema.tables 
  WHERE table_schema = 'public' 
  AND table_name = 'api_keys'
) AS api_keys_table_exists;

SELECT EXISTS (
  SELECT FROM information_schema.tables 
  WHERE table_schema = 'public' 
  AND table_name = 'token_usage'
) AS token_usage_table_exists;

SELECT EXISTS (
  SELECT FROM information_schema.tables 
  WHERE table_schema = 'public' 
  AND table_name = 'readme_history'
) AS readme_history_table_exists;

SELECT EXISTS (
  SELECT FROM information_schema.tables 
  WHERE table_schema = 'public' 
  AND table_name = 'plans'
) AS plans_table_exists;

-- Check if triggers exist
SELECT EXISTS (
  SELECT FROM pg_trigger
  WHERE tgname = 'on_auth_user_created'
) AS user_created_trigger_exists;

SELECT EXISTS (
  SELECT FROM pg_trigger
  WHERE tgname = 'on_auth_user_signed_in'
) AS user_signed_in_trigger_exists;

-- Check if functions exist
SELECT EXISTS (
  SELECT FROM pg_proc
  WHERE proname = 'handle_new_user'
) AS handle_new_user_function_exists;

SELECT EXISTS (
  SELECT FROM pg_proc
  WHERE proname = 'handle_user_login'
) AS handle_user_login_function_exists;

SELECT EXISTS (
  SELECT FROM pg_proc
  WHERE proname = 'create_user_if_not_exists'
) AS create_user_if_not_exists_function_exists;

SELECT EXISTS (
  SELECT FROM pg_proc
  WHERE proname = 'record_token_usage'
) AS record_token_usage_function_exists;

-- Check if RLS is enabled
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('users', 'api_keys', 'token_usage', 'readme_history', 'plans');

-- Check RLS policies
SELECT tablename, policyname, permissive, cmd, qual::text
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;

-- Check if plans exist
SELECT id, name, token_quota
FROM public.plans;

-- Check auth users vs public users
SELECT 
  (SELECT COUNT(*) FROM auth.users) AS auth_users_count,
  (SELECT COUNT(*) FROM public.users) AS public_users_count,
  (SELECT COUNT(*) FROM auth.users u LEFT JOIN public.users p ON u.id = p.id WHERE p.id IS NULL) AS missing_users; 