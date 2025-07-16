import { createMiddlewareClient } from '@supabase/auth-helpers-nextjs';
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export async function middleware(request: NextRequest) {
  const response = NextResponse.next();
  const supabase = createMiddlewareClient({ req: request, res: response });

  // Check if we have a session
  const {
    data: { session },
  } = await supabase.auth.getSession();

  // If no session and trying to access a protected route
  const isProtectedRoute = 
    request.nextUrl.pathname.startsWith('/dashboard') ||
    request.nextUrl.pathname.startsWith('/generate') ||
    request.nextUrl.pathname.startsWith('/api-keys') ||
    request.nextUrl.pathname.startsWith('/history');

  // If accessing login/register while logged in, redirect to dashboard
  const isAuthRoute = 
    request.nextUrl.pathname.startsWith('/login') ||
    request.nextUrl.pathname.startsWith('/register');

  if (!session && isProtectedRoute) {
    // Redirect to login page
    const redirectUrl = new URL('/login', request.url);
    redirectUrl.searchParams.set('redirectedFrom', request.nextUrl.pathname);
    return NextResponse.redirect(redirectUrl);
  }

  if (session && isAuthRoute) {
    // Redirect to dashboard if trying to access login/register while logged in
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  return response;
}

// Specify which routes this middleware should run on
export const config = {
  matcher: [
    '/dashboard/:path*',
    '/generate/:path*',
    '/api-keys/:path*',
    '/history/:path*',
    '/login',
    '/register',
  ],
}; 