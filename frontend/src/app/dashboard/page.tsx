'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs';
import Image from 'next/image';
import Link from 'next/link';

export default function Dashboard() {
  const router = useRouter();
  const supabase = createClientComponentClient();
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function getUser() {
      try {
        const { data: { session } } = await supabase.auth.getSession();
        
        if (!session) {
          router.push('/login');
          return;
        }
        
        setUser(session.user);
      } catch (error) {
        console.error('Error getting user:', error);
      } finally {
        setLoading(false);
      }
    }
    
    getUser();
  }, [router, supabase]);

  const handleSignOut = async () => {
    await supabase.auth.signOut();
    router.push('/login');
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
              {user?.email}
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
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-2xl font-bold mb-6">Welcome to your Dashboard</h2>
          
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