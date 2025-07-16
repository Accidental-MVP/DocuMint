import { SupabaseClient } from '@supabase/supabase-js';

/**
 * Ensures a user exists in the custom users table
 * @param supabase - Supabase client instance
 * @param authUser - User object from Supabase Auth
 * @returns Promise<boolean> - True if the user exists or was created successfully
 */
export async function ensureUserExists(
  supabase: SupabaseClient,
  authUser: any
): Promise<boolean> {
  try {
    if (!authUser || !authUser.id || !authUser.email) {
      console.error('Invalid user object provided to ensureUserExists');
      return false;
    }
    
    // First check if the user already exists
    const { data: existingUser, error: fetchError } = await supabase
      .from('users')
      .select('id')
      .eq('id', authUser.id)
      .single();
    
    // If user exists, just update the last_sign_in
    if (existingUser) {
      const { error: updateError } = await supabase
        .from('users')
        .update({ 
          last_sign_in: new Date().toISOString(),
          updated_at: new Date().toISOString()
        })
        .eq('id', authUser.id);
      
      if (updateError) {
        console.error('Error updating user last_sign_in:', updateError);
      }
      
      return true;
    }
    
    // If user doesn't exist, create them
    if (fetchError && fetchError.code === 'PGRST116') { // No rows returned
      const { error: insertError } = await supabase
        .from('users')
        .insert({
          id: authUser.id,
          email: authUser.email,
          username: authUser.user_metadata?.username || authUser.email?.split('@')[0] || null,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          last_sign_in: new Date().toISOString(),
        });
      
      if (insertError) {
        console.error('Error inserting user:', insertError);
        return false;
      }
      
      return true;
    }
    
    // If there was another error checking if user exists
    if (fetchError) {
      console.error('Error checking if user exists:', fetchError);
      return false;
    }
    
    return true;
  } catch (error) {
    console.error('Unexpected error in ensureUserExists:', error);
    return false;
  }
} 