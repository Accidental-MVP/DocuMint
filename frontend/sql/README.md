# Setting Up User Management in Supabase

This directory contains SQL scripts to set up user management in your Supabase project.

## Important Note About Triggers

We initially tried to use database triggers on the `auth.users` table to automatically create records in our custom users table. However, this approach causes a known issue in Supabase:

> **"Database error saving new user"**

This error occurs because Supabase's internal authentication system conflicts with custom triggers on the `auth.users` table. To avoid this issue, we've removed the triggers and instead handle user creation entirely through our application code.

## Option 1: Using the Setup Script (Recommended)

We've created a setup script to help you easily set up the users table in Supabase:

1. Make sure you have the required environment variables:
   ```
   NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
   SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
   ```
   
   You can add these to your `.env.local` file or set them in your environment.

2. Run the setup script:
   ```bash
   node scripts/setup-users-table.js
   ```

3. The script will:
   - Connect to your Supabase project
   - Create the users table
   - Set up Row Level Security policies
   - Verify the setup was successful

## Option 2: Manual Setup

If you prefer to set up the users table manually:

1. Log in to your Supabase dashboard
2. Navigate to the SQL Editor
3. Create a new query
4. Copy and paste the contents of `create_users_table.sql` into the query editor
5. Run the query

## What This Sets Up

The SQL script creates:

1. A `users` table that extends the built-in `auth.users` table with additional fields:
   - `username`: A display name for the user
   - `created_at`: When the user record was created
   - `updated_at`: When the user record was last updated
   - `last_sign_in`: When the user last signed in
   - `avatar_url`: URL to the user's profile picture
   - `display_name`: Full name of the user
   - `bio`: User's biography or description
   - `website`: User's website URL
   - `role`: User's role in the system (defaults to 'user')

2. Row Level Security (RLS) policies:
   - All users can view all other users
   - Users can only update their own data
   - Users can only insert their own data
   - Service role can do everything (important for the setup script)

## How User Creation Works

Since we can't use database triggers on the `auth.users` table, we handle user creation in our application code:

1. When a user signs in or registers, we check if they already exist in our custom users table
2. If they don't exist, we create a new record for them
3. If they do exist, we update their last_sign_in timestamp

This approach is implemented in the `ensureUserExists` utility function in `src/utils/user-management.ts`.

## Troubleshooting

If you encounter issues with user creation:

1. Check the browser console for any error messages
2. Verify that your Supabase URL and keys are correct
3. Make sure the users table was created correctly
4. Check that the Row Level Security policies are set up properly
5. Ensure your application has the necessary permissions to insert/update records in the users table

## Testing

After setting up the table, you can test by:

1. Creating a new user through the registration page
2. Going to the Supabase dashboard
3. Opening the Table Editor
4. Selecting the "users" table
5. Checking that a record was created for your new user 