import { createRouteHandlerClient } from '@supabase/auth-helpers-nextjs';
import { cookies } from 'next/headers';
import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  const requestUrl = new URL(request.url);
  const code = requestUrl.searchParams.get('code');
  const error = requestUrl.searchParams.get('error');
  const errorDescription = requestUrl.searchParams.get('error_description');
  
  // If there's an error in the request, redirect to login with the error
  if (error) {
    console.error(`Auth error: ${error} - ${errorDescription}`);
    return NextResponse.redirect(
      new URL(`/login?error=${encodeURIComponent(error)}&error_description=${encodeURIComponent(errorDescription || '')}`, 
      request.url)
    );
  }

  if (code) {
    // Create a Supabase client with properly awaited cookies
    const cookieStore = cookies();
    const supabase = createRouteHandlerClient({ cookies: () => cookieStore });
    
    try {
      console.log('Exchanging code for session...');
      // Exchange the code for a session
      const { data, error } = await supabase.auth.exchangeCodeForSession(code);
      
      if (error) {
        console.error('Error exchanging code for session:', error);
        return NextResponse.redirect(
          new URL(`/login?error=${encodeURIComponent('auth_error')}&error_description=${encodeURIComponent(error.message)}`, 
          request.url)
        );
      }
      
      console.log('Session created successfully for user:', data.session?.user.id);
      
      // The database trigger should handle creating the user in the public.users table
      // We'll verify this in the dashboard page
      
      // URL to redirect to after sign in process completes
      return NextResponse.redirect(new URL('/dashboard', request.url));
    } catch (unexpectedError) {
      console.error('Unexpected error during authentication:', unexpectedError);
      return NextResponse.redirect(
        new URL(`/login?error=${encodeURIComponent('unexpected_error')}&error_description=${encodeURIComponent('An unexpected error occurred')}`, 
        request.url)
      );
    }
  }

  // If no code is present, redirect to login
  return NextResponse.redirect(new URL('/login', request.url));
} 