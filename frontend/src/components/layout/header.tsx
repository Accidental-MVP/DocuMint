import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { FileText, Github, Settings, Menu, X } from 'lucide-react'
import { useState } from 'react'

export function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

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
            <Button variant="ghost" size="icon" className="text-foreground/70 hover:text-primary hover:bg-primary-50">
              <Settings className="h-5 w-5" />
            </Button>
            <Button variant="default" className="bg-primary hover:bg-primary-600 transition-colors">
              Sign In
            </Button>
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
              <Button variant="ghost" size="icon" className="text-foreground/70">
                <Settings className="h-5 w-5" />
              </Button>
              <Button variant="default" className="w-full bg-primary hover:bg-primary-600 transition-colors">
                Sign In
              </Button>
            </div>
          </nav>
        </div>
      )}
    </header>
  )
} 