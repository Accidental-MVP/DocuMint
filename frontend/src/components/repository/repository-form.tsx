'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Github, ArrowRight } from 'lucide-react';

export function RepositoryForm() {
  const [repoUrl, setRepoUrl] = useState('https://github.com/fastapi-users/fastapi-users');
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    
    // In a real app, we would validate the URL and navigate to a generation page
    // For now, we'll just simulate a loading state
    setTimeout(() => {
      setIsLoading(false);
    }, 1000);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Github className="h-5 w-5" />
          Repository URL
        </CardTitle>
        <CardDescription>
          Enter the URL of a GitHub repository to generate a README
        </CardDescription>
      </CardHeader>
      <form onSubmit={handleSubmit}>
        <CardContent>
          <div className="flex flex-col sm:flex-row gap-3">
            <Input
              placeholder="https://github.com/username/repository"
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
              className="flex-1"
            />
            <Button type="submit" disabled={isLoading} className="whitespace-nowrap">
              {isLoading ? (
                <span className="flex items-center gap-2">
                  <span className="animate-spin">⏳</span> Loading...
                </span>
              ) : (
                <span className="flex items-center gap-2">
                  Analyze <ArrowRight className="h-4 w-4" />
                </span>
              )}
            </Button>
          </div>
        </CardContent>
      </form>
    </Card>
  );
} 