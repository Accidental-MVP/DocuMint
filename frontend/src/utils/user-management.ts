import { SupabaseClient, PostgrestError } from '@supabase/supabase-js';

/**
 * Ensures a user exists in the custom users table
 * This is a fallback in case the database trigger fails
 * 
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
      console.error('Invalid user object provided to ensureUserExists', authUser);
      return false;
    }
    
    console.log('Checking if user exists in database:', authUser.id);
    
    // First check if the user already exists
    const { data: existingUser, error: fetchError } = await supabase
      .from('users')
      .select('id, email')
      .eq('id', authUser.id)
      .single();
    
    // If user exists, we're done
    if (existingUser) {
      console.log('User exists in database:', existingUser);
      return true;
    }
    
    // If there was an error checking if user exists
    if (fetchError) {
      console.log('Error checking if user exists:', fetchError);
      
      // If the error is that no rows were returned, the user doesn't exist
      if ((fetchError as PostgrestError).code === 'PGRST116') {
        console.log('User does not exist, attempting to create');
        
        // Check if we're authenticated
        const { data: { session } } = await supabase.auth.getSession();
        console.log('Current session:', session ? 'Authenticated' : 'Not authenticated');
        
        // Try to insert the user with ON CONFLICT DO UPDATE
        const { data: insertedUser, error: insertError } = await supabase
          .from('users')
          .upsert({
            id: authUser.id,
            email: authUser.email,
            auth_provider: authUser.app_metadata?.provider || 'email',
            email_verified: !!authUser.email_confirmed_at,
            updated_at: new Date().toISOString()
          })
          .select('id, email')
          .single();
        
        if (insertError) {
          console.error('Error inserting user:', insertError);
          console.log('Insert error details:', JSON.stringify(insertError, null, 2));
          
          // Try a different approach - direct RPC call
          console.log('Trying RPC approach');
          const { data: rpcData, error: rpcError } = await supabase.rpc('create_user_if_not_exists', {
            user_id: authUser.id,
            user_email: authUser.email
          });
          
          if (rpcError) {
            console.error('RPC error:', rpcError);
            console.log('RPC error details:', JSON.stringify(rpcError, null, 2));
            return false;
          }
          
          console.log('User created via RPC');
          return true;
        }
        
        console.log('User created or updated:', insertedUser);
        return true;
      } else {
        // Some other error occurred
        console.error('Error checking if user exists:', fetchError);
        console.log('Fetch error details:', JSON.stringify(fetchError, null, 2));
        return false;
      }
    }
    
    // If we get here, something unexpected happened
    console.warn('Unexpected state in ensureUserExists - no user and no error');
    return false;
  } catch (error) {
    console.error('Unexpected error in ensureUserExists:', error);
    console.log('Error details:', error instanceof Error ? error.message : JSON.stringify(error, null, 2));
    return false;
  }
}

/**
 * Get user profile data
 * @param supabase - Supabase client instance
 * @param userId - User ID
 * @returns Promise<any> - User profile data
 */
export async function getUserProfile(
  supabase: SupabaseClient,
  userId: string
): Promise<any> {
  try {
    console.log('Getting user profile for:', userId);
    
    // Check if we're authenticated
    const { data: { session } } = await supabase.auth.getSession();
    console.log('Current session:', session ? 'Authenticated' : 'Not authenticated');
    
    const { data, error } = await supabase
      .from('users')
      .select('*')
      .eq('id', userId)
      .throwOnError()
      .single();
    
    if (error) {
      console.error('Error fetching user profile:', error);
      console.log('Error details:', JSON.stringify(error, null, 2));
      return null;
    }
    
    console.log('User profile retrieved:', data);
    return data;
  } catch (error) {
    console.error('Unexpected error in getUserProfile:', error);
    console.log('Error details:', error instanceof Error ? error.message : JSON.stringify(error, null, 2));
    return null;
  }
}

/**
 * Update user profile data
 * @param supabase - Supabase client instance
 * @param userId - User ID
 * @param userData - User data to update
 * @returns Promise<boolean> - True if update was successful
 */
export async function updateUserProfile(
  supabase: SupabaseClient,
  userId: string,
  userData: any
): Promise<boolean> {
  try {
    console.log('Updating user profile for:', userId);
    
    // Add updated_at timestamp
    const dataToUpdate = {
      ...userData,
      updated_at: new Date().toISOString()
    };
    
    const { data, error } = await supabase
      .from('users')
      .update(dataToUpdate)
      .eq('id', userId)
      .select()
      .throwOnError()
      .single();
    
    if (error) {
      console.error('Error updating user profile:', error);
      console.log('Error details:', JSON.stringify(error, null, 2));
      return false;
    }
    
    console.log('User profile updated:', data);
    return true;
  } catch (error) {
    console.error('Unexpected error in updateUserProfile:', error);
    console.log('Error details:', error instanceof Error ? error.message : JSON.stringify(error, null, 2));
    return false;
  }
}

/**
 * Get user's current plan
 * @param supabase - Supabase client instance
 * @param userId - User ID
 * @returns Promise<any> - Plan data
 */
export async function getUserPlan(
  supabase: SupabaseClient,
  userId: string
): Promise<any> {
  try {
    console.log('Getting user plan for:', userId);
    
    // First get the user's plan ID
    const { data: user, error: userError } = await supabase
      .from('users')
      .select('plan')
      .eq('id', userId)
      .throwOnError()
      .single();
    
    if (userError || !user) {
      console.error('Error fetching user plan:', userError);
      console.log('Error details:', JSON.stringify(userError, null, 2));
      
      // Return the default free plan if we can't get the user's plan
      const { data: defaultPlan } = await supabase
        .from('plans')
        .select('*')
        .eq('id', 'free')
        .single();
      
      console.log('Using default free plan');
      return defaultPlan;
    }
    
    // Then get the plan details
    const { data: plan, error: planError } = await supabase
      .from('plans')
      .select('*')
      .eq('id', user.plan || 'free')
      .throwOnError()
      .single();
    
    if (planError) {
      console.error('Error fetching plan details:', planError);
      console.log('Error details:', JSON.stringify(planError, null, 2));
      return null;
    }
    
    console.log('User plan retrieved:', plan);
    return plan;
  } catch (error) {
    console.error('Unexpected error in getUserPlan:', error);
    console.log('Error details:', error instanceof Error ? error.message : JSON.stringify(error, null, 2));
    return null;
  }
}

/**
 * Check if user has enough tokens for an operation
 * @param supabase - Supabase client instance
 * @param userId - User ID
 * @param tokensNeeded - Number of tokens needed
 * @returns Promise<boolean> - True if user has enough tokens
 */
export async function hasEnoughTokens(
  supabase: SupabaseClient,
  userId: string,
  tokensNeeded: number
): Promise<boolean> {
  try {
    console.log('Checking token quota for:', userId);
    
    const { data: user, error } = await supabase
      .from('users')
      .select('tokens_used, tokens_quota')
      .eq('id', userId)
      .throwOnError()
      .single();
    
    if (error || !user) {
      console.error('Error checking token quota:', error);
      console.log('Error details:', JSON.stringify(error, null, 2));
      return false;
    }
    
    const remaining = (user.tokens_quota || 10000) - (user.tokens_used || 0);
    console.log(`Token quota: ${user.tokens_used || 0} used of ${user.tokens_quota || 10000}, ${remaining} remaining, ${tokensNeeded} needed`);
    
    return remaining >= tokensNeeded;
  } catch (error) {
    console.error('Unexpected error in hasEnoughTokens:', error);
    console.log('Error details:', error instanceof Error ? error.message : JSON.stringify(error, null, 2));
    return false;
  }
}

/**
 * Record token usage
 * @param supabase - Supabase client instance
 * @param userId - User ID
 * @param tokensUsed - Number of tokens used
 * @param source - Source of token usage (e.g., 'web', 'api')
 * @param endpoint - API endpoint or feature used
 * @returns Promise<boolean> - True if recording was successful
 */
export async function recordTokenUsage(
  supabase: SupabaseClient,
  userId: string,
  tokensUsed: number,
  source: string = 'web',
  endpoint: string = 'generate'
): Promise<boolean> {
  try {
    console.log(`Recording ${tokensUsed} tokens used for ${userId}`);
    
    // Start a transaction
    const { data: rpcData, error: tokenError } = await supabase.rpc('record_token_usage', {
      p_user_id: userId,
      p_tokens_used: tokensUsed,
      p_source: source,
      p_endpoint: endpoint
    });
    
    if (tokenError) {
      console.error('Error recording token usage via RPC:', tokenError);
      console.log('Error details:', JSON.stringify(tokenError, null, 2));
      
      console.log('Falling back to manual token usage recording');
      
      // Start a Supabase transaction
      // 1. Update the user's token usage
      const { data: updateData, error: updateError } = await supabase
        .from('users')
        .update({ 
          tokens_used: supabase.rpc('increment', { inc: tokensUsed }),
          updated_at: new Date().toISOString()
        })
        .eq('id', userId)
        .select('tokens_used')
        .single();
      
      if (updateError) {
        console.error('Error updating user token usage:', updateError);
        console.log('Error details:', JSON.stringify(updateError, null, 2));
        return false;
      }
      
      console.log('Updated user token usage:', updateData);
      
      // 2. Record the token usage entry
      const { data: insertData, error: insertError } = await supabase
        .from('token_usage')
        .insert({
          user_id: userId,
          date: new Date().toISOString().split('T')[0],
          tokens_used: tokensUsed,
          source,
          endpoint
        })
        .select()
        .single();
      
      if (insertError) {
        console.error('Error inserting token usage record:', insertError);
        console.log('Error details:', JSON.stringify(insertError, null, 2));
        return false;
      }
      
      console.log('Token usage record inserted:', insertData);
    } else {
      console.log('Token usage recorded via RPC');
    }
    
    return true;
  } catch (error) {
    console.error('Unexpected error in recordTokenUsage:', error);
    console.log('Error details:', error instanceof Error ? error.message : JSON.stringify(error, null, 2));
    return false;
  }
} 