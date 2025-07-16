'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Image from 'next/image';
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs';
import { Auth } from '@supabase/auth-ui-react';
import { ThemeSupa } from '@supabase/auth-ui-shared';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';

export default function Register() {
  const router = useRouter();
  const supabase = createClientComponentClient();
  const [redirectUrl, setRedirectUrl] = useState<string>('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Set the redirect URL only on the client side
    setRedirectUrl(`${window.location.origin}/auth/callback`);
    
    // Check if user is already authenticated
    const checkUser = async () => {
      try {
        const { data: { session } } = await supabase.auth.getSession();
        if (session) {
          // User is authenticated, redirect to dashboard
          router.push('/dashboard');
        }
      } catch (error) {
        console.error('Error checking authentication:', error);
      } finally {
        setLoading(false);
      }
    };
    
    checkUser();
    
    // Subscribe to auth state changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
      if (event === 'SIGNED_IN' && session) {
        // User has signed in, redirect to dashboard
        router.push('/dashboard');
      }
    });
    
    // Cleanup subscription on unmount
    return () => {
      subscription.unsubscribe();
    };
  }, [router, supabase]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4 sm:p-6 lg:p-8">
      {/* Background pattern */}
      <div className="absolute inset-0 z-0 opacity-10">
        <Image 
          src="/hero-pattern.svg" 
          alt="Background Pattern" 
          fill 
          className="object-cover"
          priority
        />
      </div>

      <div className="relative z-10 w-full max-w-md">
        {/* Logo and branding */}
        <div className="flex justify-center mb-8">
          <div className="bg-white rounded-full p-3 shadow-lg">
            <Image 
              src="/globe.svg" 
              alt="DocuMint Logo" 
              width={48} 
              height={48} 
              className="h-12 w-12"
            />
          </div>
        </div>

        <Card className="backdrop-blur-sm bg-white/90 border-0 shadow-xl">
          <CardHeader className="space-y-1">
            <CardTitle className="text-2xl font-bold text-center">Create account</CardTitle>
            <CardDescription className="text-center">
              Join DocuMint to get started
            </CardDescription>
          </CardHeader>
          
          <CardContent className="space-y-4">
            {/* Supabase Auth UI */}
            <div className="space-y-2">
              {redirectUrl && (
                <Auth
                  supabaseClient={supabase}
                  appearance={{ 
                    theme: ThemeSupa,
                    style: {
                      button: {
                        borderRadius: '0.375rem',
                        fontSize: '0.875rem',
                        lineHeight: '1.25rem',
                        fontWeight: '500',
                        padding: '0.625rem 1rem',
                      },
                      container: {
                        width: '100%',
                      },
                      input: {
                        borderRadius: '0.375rem',
                        fontSize: '0.875rem',
                        padding: '0.625rem 1rem',
                      },
                      label: {
                        fontSize: '0.875rem',
                        marginBottom: '0.5rem',
                      },
                      anchor: {
                        fontSize: '0.875rem',
                        color: '#2563eb',
                      },
                      message: {
                        fontSize: '0.875rem',
                        padding: '0.5rem',
                        marginBottom: '1rem',
                        borderRadius: '0.375rem',
                      }
                    }
                  }}
                  theme="light"
                  providers={['google', 'github']}
                  redirectTo={redirectUrl}
                  view="sign_up"
                  onlyThirdPartyProviders={false}
                />
              )}
            </div>
          </CardContent>
          
          <CardFooter className="flex flex-col space-y-2 text-center">
            <div className="text-sm text-gray-600">
              Already have an account?{' '}
              <Link href="/login" className="font-medium text-blue-600 hover:text-blue-800 hover:underline">
                Sign in
              </Link>
            </div>
            <p className="text-xs text-gray-500">
              By creating an account, you agree to our Terms of Service and Privacy Policy
            </p>
          </CardFooter>
        </Card>
      </div>
    </div>
  );
} 