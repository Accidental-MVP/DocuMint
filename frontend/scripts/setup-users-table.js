#!/usr/bin/env node

const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');
const path = require('path');
const readline = require('readline');
require('dotenv').config();

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

async function main() {
  console.log('🔧 DocuMint User Management Setup 🔧');
  console.log('====================================');
  console.log('This script will help you set up the users table in your Supabase project.');
  console.log('');

  // Get Supabase URL and key from environment or prompt
  let supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
  let supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

  if (!supabaseUrl) {
    supabaseUrl = await promptQuestion('Enter your Supabase URL: ');
  }

  if (!supabaseKey) {
    supabaseKey = await promptQuestion('Enter your Supabase service role key: ');
    console.log('⚠️ Warning: Using the service role key in this script. Never expose this in client-side code!');
  }

  try {
    // Initialize Supabase client with service role key
    const supabase = createClient(supabaseUrl, supabaseKey);
    
    console.log('🔄 Connecting to Supabase...');
    
    // Read the SQL file
    const sqlFilePath = path.join(__dirname, '..', 'sql', 'create_users_table.sql');
    const sqlContent = fs.readFileSync(sqlFilePath, 'utf8');
    
    console.log('📄 SQL file loaded successfully.');
    console.log('🔄 Executing SQL to create users table and triggers...');
    
    // Execute the SQL
    const { error } = await supabase.rpc('exec_sql', { sql: sqlContent });
    
    if (error) {
      console.error('❌ Error executing SQL:', error);
      console.log('');
      console.log('You may need to run the SQL manually in the Supabase SQL Editor.');
      console.log(`The SQL file is located at: ${sqlFilePath}`);
    } else {
      console.log('✅ Users table and triggers created successfully!');
      
      // Test the setup by checking if the users table exists
      const { data, error: testError } = await supabase
        .from('users')
        .select('id')
        .limit(1);
      
      if (testError) {
        console.error('❌ Error testing users table:', testError);
      } else {
        console.log('✅ Users table is accessible.');
        console.log(`Found ${data.length} existing users.`);
      }
    }
    
    console.log('');
    console.log('🎉 Setup complete!');
    console.log('');
    console.log('Next steps:');
    console.log('1. Make sure your .env file contains the Supabase URL and anon key:');
    console.log('   NEXT_PUBLIC_SUPABASE_URL=your_supabase_url');
    console.log('   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key');
    console.log('2. Restart your Next.js development server');
    console.log('3. Test user registration and login');
    
  } catch (err) {
    console.error('❌ Unexpected error:', err);
  }
  
  rl.close();
}

function promptQuestion(question) {
  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      resolve(answer);
    });
  });
}

main(); 