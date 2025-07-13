import Link from 'next/link'
import { FileText } from 'lucide-react'

export function Footer() {
  return (
    <footer className="border-t border-border/40 bg-muted-50/50">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-16">
        <div className="grid grid-cols-1 gap-8 md:grid-cols-5">
          <div className="md:col-span-2">
            <Link href="/" className="flex items-center gap-2 mb-4">
              <div className="flex items-center justify-center w-8 h-8 rounded-md bg-primary text-white">
                <FileText className="h-5 w-5" />
              </div>
              <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-primary-700">
                DocuMint
              </span>
            </Link>
            <p className="text-muted-600 max-w-md">
              DocuMint uses advanced AI to analyze your GitHub repositories and create
              compelling, detailed README files in seconds.
            </p>
            <div className="flex gap-4 mt-6">
              <Link href="https://twitter.com" className="text-muted-500 hover:text-primary transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M22 4s-.7 2.1-2 3.4c1.6 10-9.4 17.3-18 11.6 2.2.1 4.4-.6 6-2C3 15.5.5 9.6 3 5c2.2 2.6 5.6 4.1 9 4-.9-4.2 4-6.6 7-3.8 1.1 0 3-1.2 3-1.2z"></path>
                </svg>
              </Link>
              <Link href="https://github.com" className="text-muted-500 hover:text-primary transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"></path>
                  <path d="M9 18c-4.51 2-5-2-7-2"></path>
                </svg>
              </Link>
              <Link href="https://discord.com" className="text-muted-500 hover:text-primary transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M9 12h.01M15 12h.01M8.5 17.5l-1.5.5s0-9 4-9c-2.5-2.5-4 0-4 0C3.5 9 3 4 3 4s4.5 1 6.5 3C11.5 6 17 7 17 7s.5 5-2.5 6c0 0 1.5-2.5-1-5 4 0 4 9 4 9l-1.5-.5"></path>
                  <path d="M9.5 15.5 10 17l1.5-1.5"></path>
                  <path d="m14.5 15.5-2 1.5.5-2"></path>
                </svg>
              </Link>
            </div>
          </div>
          
          <div>
            <h3 className="text-sm font-semibold text-foreground tracking-wider uppercase mb-4">Product</h3>
            <ul className="space-y-3">
              <li>
                <Link href="/features" className="text-muted-600 hover:text-primary transition-colors">
                  Features
                </Link>
              </li>
              <li>
                <Link href="/pricing" className="text-muted-600 hover:text-primary transition-colors">
                  Pricing
                </Link>
              </li>
              <li>
                <Link href="/docs" className="text-muted-600 hover:text-primary transition-colors">
                  Documentation
                </Link>
              </li>
              <li>
                <Link href="/changelog" className="text-muted-600 hover:text-primary transition-colors">
                  Changelog
                </Link>
              </li>
            </ul>
          </div>
          
          <div>
            <h3 className="text-sm font-semibold text-foreground tracking-wider uppercase mb-4">Company</h3>
            <ul className="space-y-3">
              <li>
                <Link href="/about" className="text-muted-600 hover:text-primary transition-colors">
                  About
                </Link>
              </li>
              <li>
                <Link href="/blog" className="text-muted-600 hover:text-primary transition-colors">
                  Blog
                </Link>
              </li>
              <li>
                <Link href="/careers" className="text-muted-600 hover:text-primary transition-colors">
                  Careers
                </Link>
              </li>
              <li>
                <Link href="/contact" className="text-muted-600 hover:text-primary transition-colors">
                  Contact
                </Link>
              </li>
            </ul>
          </div>
          
          <div>
            <h3 className="text-sm font-semibold text-foreground tracking-wider uppercase mb-4">Legal</h3>
            <ul className="space-y-3">
              <li>
                <Link href="/privacy" className="text-muted-600 hover:text-primary transition-colors">
                  Privacy
                </Link>
              </li>
              <li>
                <Link href="/terms" className="text-muted-600 hover:text-primary transition-colors">
                  Terms
                </Link>
              </li>
              <li>
                <Link href="/cookies" className="text-muted-600 hover:text-primary transition-colors">
                  Cookie Policy
                </Link>
              </li>
              <li>
                <Link href="/licenses" className="text-muted-600 hover:text-primary transition-colors">
                  Licenses
                </Link>
              </li>
            </ul>
          </div>
        </div>
        
        <div className="mt-12 pt-8 border-t border-border/40 flex flex-col md:flex-row justify-between items-center">
          <p className="text-sm text-muted-500">
            &copy; {new Date().getFullYear()} DocuMint. All rights reserved.
          </p>
          <div className="flex gap-6 mt-4 md:mt-0">
            <Link href="/status" className="text-sm text-muted-500 hover:text-primary transition-colors">
              Status
            </Link>
            <Link href="/sitemap" className="text-sm text-muted-500 hover:text-primary transition-colors">
              Sitemap
            </Link>
            <Link href="/accessibility" className="text-sm text-muted-500 hover:text-primary transition-colors">
              Accessibility
            </Link>
          </div>
        </div>
      </div>
    </footer>
  )
} 