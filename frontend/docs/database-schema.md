# DocuMint Database Schema

This document explains the database schema used by DocuMint for user management, API keys, token usage tracking, and more.

## Overview

DocuMint uses a production-grade SaaS schema with the following tables:

1. `users` - Core user data and plan information
2. `api_keys` - API keys for programmatic access
3. `token_usage` - Metered billing and usage tracking
4. `readme_history` - History of generated README files
5. `plans` - Pricing tiers and features

## Tables

### 1. `users` Table

The soul of your SaaS - stores all core user data.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key, linked to auth.users |
| email | TEXT | User's email address |
| full_name | TEXT | User's full name |
| username | TEXT | Optional username/handle |
| avatar_url | TEXT | URL to user's avatar |
| auth_provider | TEXT | 'email', 'google', etc. |
| hashed_password | TEXT | NULL if using OAuth |
| email_verified | BOOLEAN | Whether email is verified |
| created_at | TIMESTAMP | When user was created |
| updated_at | TIMESTAMP | When user was last updated |
| last_login | TIMESTAMP | When user last logged in |
| is_active | BOOLEAN | Whether user is active |
| is_banned | BOOLEAN | Whether user is banned |
| ban_reason | TEXT | Reason for ban if applicable |
| plan | TEXT | 'free', 'pro', 'enterprise' |
| tokens_used | INTEGER | Number of tokens used |
| tokens_quota | INTEGER | Token quota for current period |
| quota_reset_date | TIMESTAMP | When token quota resets |
| stripe_customer_id | TEXT | Stripe customer ID |
| stripe_subscription_id | TEXT | Stripe subscription ID |
| billing_cycle_anchor | TIMESTAMP | Billing cycle start date |
| locale | TEXT | User's locale preference |
| timezone | TEXT | User's timezone |
| referral_code | TEXT | User's referral code |
| referred_by | UUID | ID of user who referred this user |
| metadata | JSONB | Additional user metadata |

### 2. `api_keys` Table

Stores API keys for programmatic access.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Foreign key to users.id |
| key | TEXT | The API key |
| name | TEXT | User-provided name for the key |
| created_at | TIMESTAMP | When key was created |
| last_used | TIMESTAMP | When key was last used |
| is_active | BOOLEAN | Whether key is active |

### 3. `token_usage` Table

Tracks token usage for metered billing.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Foreign key to users.id |
| date | DATE | Date of usage |
| tokens_used | INTEGER | Number of tokens used |
| source | TEXT | Source of usage (web, api, etc.) |
| endpoint | TEXT | API endpoint or feature used |
| created_at | TIMESTAMP | When record was created |

### 4. `readme_history` Table

Stores history of generated README files.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Foreign key to users.id |
| repo_url | TEXT | Repository URL |
| content | TEXT | Generated README content |
| model_used | TEXT | AI model used |
| generation_mode | TEXT | Generation mode used |
| token_cost | INTEGER | Token cost of generation |
| created_at | TIMESTAMP | When README was generated |

### 5. `plans` Table

Defines pricing tiers and features.

| Column | Type | Description |
|--------|------|-------------|
| id | TEXT | Primary key (free, pro, enterprise) |
| name | TEXT | Display name |
| monthly_price | INTEGER | Monthly price in cents |
| yearly_price | INTEGER | Yearly price in cents |
| token_quota | INTEGER | Monthly token quota |
| features | JSONB | Plan features |
| stripe_price_id_monthly | TEXT | Stripe price ID for monthly billing |
| stripe_price_id_yearly | TEXT | Stripe price ID for yearly billing |

## Relationships

- `users.id` → `auth.users.id` (Foreign key)
- `users.referred_by` → `users.id` (Self-reference)
- `api_keys.user_id` → `users.id` (Foreign key)
- `token_usage.user_id` → `users.id` (Foreign key)
- `readme_history.user_id` → `users.id` (Foreign key)
- `users.plan` → `plans.id` (Logical relationship)

## Row-Level Security (RLS)

Row-Level Security is enabled on all tables to ensure data isolation:

- Users can only view and update their own data
- Users can only view, create, update, and delete their own API keys
- Users can only view their own token usage
- Users can only view and create their own README history
- Anyone can view plans

## Stored Procedures

The following stored procedures are available:

- `record_token_usage(user_id, tokens_used, source, endpoint)` - Record token usage in a transaction
- `increment(inc)` - Helper function for incrementing values
- `reset_token_quota()` - Reset token quotas when they expire
- `create_api_key(user_id, name)` - Create a new API key
- `validate_api_key(key)` - Validate an API key and return the user ID

## Triggers

Two triggers are set up to automate user management:

1. `on_auth_user_created` - Creates a record in `users` when a new user signs up
2. `on_auth_user_signed_in` - Updates the `last_login` timestamp when a user signs in

## Setup

To set up the database schema:

1. Run the setup script:
   ```
   cd frontend
   npm install dotenv @supabase/supabase-js
   node scripts/setup-database.js
   ```

2. Or manually run the SQL files in the Supabase SQL Editor:
   - `frontend/sql/production_schema.sql`
   - `frontend/sql/stored_procedures.sql`

## Usage

Use the utility functions in `frontend/src/utils/user-management.ts` to interact with the database:

- `ensureUserExists(supabase, authUser)` - Ensure a user exists in the users table
- `getUserProfile(supabase, userId)` - Get a user's profile data
- `updateUserProfile(supabase, userId, userData)` - Update a user's profile data
- `getUserPlan(supabase, userId)` - Get a user's plan details
- `hasEnoughTokens(supabase, userId, tokensNeeded)` - Check if a user has enough tokens
- `recordTokenUsage(supabase, userId, tokensUsed, source, endpoint)` - Record token usage 