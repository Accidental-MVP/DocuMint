'use client';

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Github, ArrowRight, Loader2 } from 'lucide-react'

interface RepositoryInputProps {
  onSubmit: (url: string) => void
  isLoading?: boolean
  disabled?: boolean
}

export function RepositoryInput({ onSubmit, isLoading = false, disabled = false }: RepositoryInputProps) {
  const [url, setUrl] = useState('')
  const [error, setError] = useState('')
  const [isMounted, setIsMounted] = useState(false)
  
  useEffect(() => {
    setIsMounted(true)
  }, [])

  const validateUrl = (url: string): boolean => {
    // Simple GitHub URL validation
    const githubRegex = /^https:\/\/github\.com\/[\w-]+\/[\w.-]+\/?$/
    return githubRegex.test(url)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (disabled) {
      return;
    }
    
    if (!url.trim()) {
      setError('Please enter a GitHub repository URL')
      return
    }

    if (!validateUrl(url)) {
      setError('Please enter a valid GitHub repository URL (e.g., https://github.com/username/repo)')
      return
    }

    setError('')
    onSubmit(url)
  }

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="text-2xl">Generate README</CardTitle>
        <CardDescription>
          Enter a GitHub repository URL to generate a professional README file
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="flex items-center space-x-2">
            <Github className="h-5 w-5 text-muted-foreground" />
            <Input
              placeholder="https://github.com/username/repository"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="flex-1"
              disabled={isLoading || disabled}
            />
          </div>
          {error && <p className="text-sm text-destructive">{error}</p>}
        </form>
      </CardContent>
      <CardFooter className="flex justify-between">
        <Button variant="outline" disabled={isLoading || disabled}>
          Examples
        </Button>
        <Button onClick={handleSubmit} disabled={isLoading || disabled || !url.trim()}>
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Generating
            </>
          ) : (
            <>
              Generate README
              <ArrowRight className="ml-2 h-4 w-4" />
            </>
          )}
        </Button>
      </CardFooter>
    </Card>
  )
} 