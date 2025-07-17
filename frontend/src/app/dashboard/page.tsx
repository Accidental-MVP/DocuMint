'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs';
import Image from 'next/image';
import Link from 'next/link';
import { ensureUserExists, getUserProfile, getUserPlan } from '@/utils/user-management';

export default function Dashboard() {
  const router = useRouter();
  const supabase = createClientComponentClient();
  const [user, setUser] = useState<any>(null);
  const [profile, setProfile] = useState<any>(null);
  const [plan, setPlan] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function getUser() {
      try {
        console.log('Checking auth session...');
        const { data: { session }, error: sessionError } = await supabase.auth.getSession();
        
        if (sessionError) {
          console.error('Error getting session:', sessionError);
          setError('Error with authentication. Please try logging in again.');
          setLoading(false);
          return;
        }
        
        if (!session) {
          console.log('No session found, redirecting to login');
          router.push('/login');
          return;
        }
        
        console.log('Session found:', session.user.id);
        setUser(session.user);
        
        // Ensure the user exists in our custom users table
        // The database trigger should handle this automatically, but we'll check just in case
        const userExists = await ensureUserExists(supabase, session.user);
        console.log('User exists in database:', userExists);
        
        if (!userExists) {
          console.warn('Failed to ensure user exists in database');
          setError('There was an issue with your account. Some features may be limited.');
        }
        
        // Get user profile
        console.log('Fetching user profile...');
        const userProfile = await getUserProfile(supabase, session.user.id);
        
        if (userProfile) {
          console.log('User profile found:', userProfile.id);
          setProfile(userProfile);
          
          // Get user plan
          console.log('Fetching user plan...');
          const userPlan = await getUserPlan(supabase, session.user.id);
          
          if (userPlan) {
            console.log('User plan found:', userPlan.id);
            setPlan(userPlan);
          } else {
            console.warn('No plan found for user');
            setError('Could not retrieve your subscription plan. Using free plan.');
          }
        } else {
          console.warn('No profile found for user');
          setError('Could not retrieve your profile. Please try refreshing the page.');
        }
      } catch (error) {
        console.error('Error in dashboard initialization:', error);
        setError('An unexpected error occurred. Please try refreshing the page.');
      } finally {
        setLoading(false);
      }
    }
    
    getUser();
  }, [router, supabase]);

  const handleSignOut = async () => {
    try {
      const { error } = await supabase.auth.signOut();
      if (error) {
        console.error('Error signing out:', error);
        setError('Error signing out. Please try again.');
        return;
      }
      router.push('/login');
    } catch (error) {
      console.error('Unexpected error during sign out:', error);
      setError('An unexpected error occurred. Please try again.');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div className="flex items-center">
            <Image 
              src="/globe.svg" 
              alt="DocuMint Logo" 
              width={32} 
              height={32} 
              className="h-8 w-8 mr-2"
            />
            <h1 className="text-xl font-bold text-gray-900">DocuMint</h1>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-700">
              {profile?.full_name || profile?.email || user?.email}
            </span>
            <button 
              onClick={handleSignOut}
              className="px-3 py-1 text-sm bg-gray-200 hover:bg-gray-300 rounded-md"
            >
              Sign out
            </button>
          </div>
        </div>
      </header>
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 text-yellow-800 rounded-md">
            {error}
          </div>
        )}
        
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-2xl font-bold mb-6">
            Welcome{profile?.full_name ? `, ${profile.full_name}` : ''}!
          </h2>
          
          {plan && (
            <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="font-medium text-blue-800">
                    {plan.name} Plan
                  </h3>
                  <p className="text-sm text-blue-600">
                    {profile?.tokens_used || 0} / {plan.token_quota} tokens used
                  </p>
                </div>
                {plan.id !== 'enterprise' && (
                  <Link href="/pricing" className="px-3 py-1 text-sm bg-blue-500 text-white rounded-md hover:bg-blue-600">
                    Upgrade
                  </Link>
                )}
              </div>
            </div>
          )}
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Link href="/generate" className="block p-6 border rounded-lg hover:shadow-md transition-shadow">
              <h3 className="text-lg font-medium mb-2">Generate README</h3>
              <p className="text-gray-600">Create beautiful documentation for your repositories</p>
            </Link>
            
            <Link href="/api-keys" className="block p-6 border rounded-lg hover:shadow-md transition-shadow">
              <h3 className="text-lg font-medium mb-2">API Keys</h3>
              <p className="text-gray-600">Manage your API keys for integration</p>
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
} 