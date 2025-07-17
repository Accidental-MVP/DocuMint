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
  console.log('🔧 DocuMint Database Setup 🔧');
  console.log('============================');
  console.log('This script will set up the database for DocuMint.');
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
    
    // Step 1: Set up the database schema
    console.log('\n📦 Step 1: Setting up database schema...');
    const schemaPath = path.join(__dirname, '..', 'sql', 'production_schema.sql');
    const schemaSql = fs.readFileSync(schemaPath, 'utf8');
    
    try {
      // Execute the SQL directly using the REST API
      const { error: schemaError } = await supabase.from('_sql').select('*').execute(schemaSql);
      
      if (schemaError) {
        console.error('❌ Error setting up database schema:', schemaError);
        console.log('You may need to run the SQL manually in the Supabase SQL Editor.');
        console.log(`The SQL file is located at: ${schemaPath}`);
      } else {
        console.log('✅ Database schema set up successfully!');
      }
    } catch (err) {
      console.error('❌ Error executing SQL for database schema:', err);
      console.log('You may need to run the SQL manually in the Supabase SQL Editor.');
      console.log(`The SQL file is located at: ${schemaPath}`);
    }
    
    // Step 2: Set up stored procedures
    console.log('\n🔧 Step 2: Setting up stored procedures...');
    const proceduresPath = path.join(__dirname, '..', 'sql', 'stored_procedures.sql');
    const proceduresSql = fs.readFileSync(proceduresPath, 'utf8');
    
    try {
      // Execute the SQL directly using the REST API
      const { error: proceduresError } = await supabase.from('_sql').select('*').execute(proceduresSql);
      
      if (proceduresError) {
        console.error('❌ Error setting up stored procedures:', proceduresError);
        console.log('You may need to run the SQL manually in the Supabase SQL Editor.');
        console.log(`The SQL file is located at: ${proceduresPath}`);
      } else {
        console.log('✅ Stored procedures set up successfully!');
      }
    } catch (err) {
      console.error('❌ Error executing SQL for stored procedures:', err);
      console.log('You may need to run the SQL manually in the Supabase SQL Editor.');
      console.log(`The SQL file is located at: ${proceduresPath}`);
    }
    
    // Test the setup
    console.log('\n🧪 Testing the setup...');
    try {
      // Test if the users table exists
      const { data: tableData, error: tableError } = await supabase
        .from('users')
        .select('id')
        .limit(1);
      
      if (tableError) {
        console.error('❌ Error accessing users table:', tableError);
      } else {
        console.log('✅ Users table is accessible.');
        console.log(`Found ${tableData.length} existing users.`);
      }
      
      // Test if the plans table exists and has data
      const { data: plansData, error: plansError } = await supabase
        .from('plans')
        .select('id, name')
        .limit(10);
      
      if (plansError) {
        console.error('❌ Error accessing plans table:', plansError);
      } else {
        console.log('✅ Plans table is accessible.');
        console.log(`Found ${plansData.length} plans: ${plansData.map(p => p.name).join(', ')}`);
      }
    } catch (err) {
      console.error('❌ Error testing setup:', err);
    }
    
    console.log('\n🎉 Setup complete!');
    console.log('\nNext steps:');
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