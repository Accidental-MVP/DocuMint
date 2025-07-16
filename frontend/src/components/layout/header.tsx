'use client';

import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { FileText, Github, Settings, Menu, X, User } from 'lucide-react'
import { useState, useEffect } from 'react'
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs'
import { useRouter } from 'next/navigation'

export function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const supabase = createClientComponentClient();
  const router = useRouter();

  useEffect(() => {
    async function getUser() {
      try {
        const { data: { session } } = await supabase.auth.getSession();
        setUser(session?.user || null);
      } catch (error) {
        console.error('Error getting user:', error);
      } finally {
        setLoading(false);
      }
    }
    
    getUser();
    
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user || null);
    });
    
    return () => {
      subscription.unsubscribe();
    };
  }, [supabase]);

  const handleSignIn = () => {
    router.push('/login');
  };

  const handleSignOut = async () => {
    await supabase.auth.signOut();
    router.push('/');
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/80 backdrop-blur-lg">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center gap-2">
            <Link href="/" className="flex items-center gap-2">
              <div className="flex items-center justify-center w-8 h-8 rounded-md bg-primary text-white">
                <FileText className="h-5 w-5" />
              </div>
              <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-primary-700">
                DocuMint
              </span>
            </Link>
          </div>
          
          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-8">
            <Link href="/dashboard" className="text-sm font-medium text-foreground/80 hover:text-primary transition-colors">
              Dashboard
            </Link>
            <Link href="/templates" className="text-sm font-medium text-foreground/80 hover:text-primary transition-colors">
              Templates
            </Link>
            <Link href="/pricing" className="text-sm font-medium text-foreground/80 hover:text-primary transition-colors">
              Pricing
            </Link>
            <Link href="/docs" className="text-sm font-medium text-foreground/80 hover:text-primary transition-colors">
              Docs
            </Link>
          </nav>
          
          {/* Desktop Actions */}
          <div className="hidden md:flex items-center gap-3">
            <Button variant="ghost" size="icon" className="text-foreground/70 hover:text-primary hover:bg-primary-50">
              <Github className="h-5 w-5" />
            </Button>
            {user && (
              <Button 
                variant="ghost" 
                size="icon" 
                className="text-foreground/70 hover:text-primary hover:bg-primary-50"
                onClick={() => router.push('/api-keys')}
              >
                <Settings className="h-5 w-5" />
              </Button>
            )}
            {!loading && (
              user ? (
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-2">
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-primary">
                      <User className="h-4 w-4" />
                    </div>
                    <span className="text-sm font-medium hidden lg:inline-block">
                      {user.email?.split('@')[0]}
                    </span>
                  </div>
                  <Button 
                    variant="outline" 
                    onClick={handleSignOut}
                    className="border-primary text-primary hover:bg-primary/10"
                  >
                    Sign Out
                  </Button>
                </div>
              ) : (
                <Button 
                  variant="default" 
                  className="bg-primary hover:bg-primary-600 transition-colors"
                  onClick={handleSignIn}
                >
                  Sign In
                </Button>
              )
            )}
          </div>
          
          {/* Mobile Menu Button */}
          <div className="flex md:hidden">
            <Button variant="ghost" size="icon" onClick={() => setIsMenuOpen(!isMenuOpen)}>
              {isMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </Button>
          </div>
        </div>
      </div>
      
      {/* Mobile Menu */}
      {isMenuOpen && (
        <div className="md:hidden border-t border-border/40 py-4 px-4 bg-background/95 animate-slide-down">
          <nav className="flex flex-col space-y-4">
            <Link 
              href="/dashboard" 
              className="text-sm font-medium text-foreground/80 hover:text-primary transition-colors px-2 py-1.5 rounded-md hover:bg-muted/50"
              onClick={() => setIsMenuOpen(false)}
            >
              Dashboard
            </Link>
            <Link 
              href="/templates" 
              className="text-sm font-medium text-foreground/80 hover:text-primary transition-colors px-2 py-1.5 rounded-md hover:bg-muted/50"
              onClick={() => setIsMenuOpen(false)}
            >
              Templates
            </Link>
            <Link 
              href="/pricing" 
              className="text-sm font-medium text-foreground/80 hover:text-primary transition-colors px-2 py-1.5 rounded-md hover:bg-muted/50"
              onClick={() => setIsMenuOpen(false)}
            >
              Pricing
            </Link>
            <Link 
              href="/docs" 
              className="text-sm font-medium text-foreground/80 hover:text-primary transition-colors px-2 py-1.5 rounded-md hover:bg-muted/50"
              onClick={() => setIsMenuOpen(false)}
            >
              Docs
            </Link>
            <div className="flex items-center gap-3 pt-2 border-t border-border/40">
              <Button variant="ghost" size="icon" className="text-foreground/70">
                <Github className="h-5 w-5" />
              </Button>
              {user && (
                <Button 
                  variant="ghost" 
                  size="icon" 
                  className="text-foreground/70"
                  onClick={() => {
                    router.push('/api-keys');
                    setIsMenuOpen(false);
                  }}
                >
                  <Settings className="h-5 w-5" />
                </Button>
              )}
              {!loading && (
                user ? (
                  <Button 
                    variant="default" 
                    className="w-full bg-primary hover:bg-primary-600 transition-colors"
                    onClick={() => {
                      handleSignOut();
                      setIsMenuOpen(false);
                    }}
                  >
                    Sign Out
                  </Button>
                ) : (
                  <Button 
                    variant="default" 
                    className="w-full bg-primary hover:bg-primary-600 transition-colors"
                    onClick={() => {
                      handleSignIn();
                      setIsMenuOpen(false);
                    }}
                  >
                    Sign In
                  </Button>
                )
              )}
            </div>
          </nav>
        </div>
      )}
    </header>
  )
} 