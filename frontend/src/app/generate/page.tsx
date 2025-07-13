'use client';

import { useState, useEffect } from 'react';
import { RepositoryInput } from '@/components/repository/repository-input';
import { GenerationSettings, ToneOption, ModelOption, ModeOption } from '@/components/repository/generation-settings';
import { ReadmePreview } from '@/components/repository/readme-preview';
import { TokenUsage } from '@/components/repository/token-usage';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { FileText, Settings2, BarChart } from 'lucide-react';

export default function GeneratePage() {
  // Use null as initial state to prevent hydration mismatch
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<string | null>(null);
  const [repoUrl, setRepoUrl] = useState('');
  const [settings, setSettings] = useState({
    tone: 'professional' as ToneOption,
    model: 'gpt-4' as ModelOption,
    mode: 'standard' as ModeOption
  });
  const [readmeContent, setReadmeContent] = useState('');
  const [tokenUsage, setTokenUsage] = useState({
    promptTokens: 0,
    completionTokens: 0,
    totalTokens: 0,
    maxTokens: 8192,
    usagePercentage: 0,
    filesIncluded: 0,
    filesSkipped: 0,
    filesTruncated: 0
  });
  
  // Set initial state after component mounts to avoid hydration mismatch
  useEffect(() => {
    setActiveTab('input');
  }, []);

  const handleSubmit = async (url: string) => {
    setIsLoading(true);
    setRepoUrl(url);
    
    try {
      // In a real app, this would be an API call to your backend
      // For now, we'll simulate a response after a delay
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      // Sample README content
      const sampleReadme = `# ${url.split('/').pop()?.replace('.git', '') || 'Repository'}

## Overview
This is an AI-generated README for your project. It provides an overview of your repository structure, features, and usage instructions.

## Features
- Feature 1: Description of feature 1
- Feature 2: Description of feature 2
- Feature 3: Description of feature 3

## Installation
\`\`\`bash
npm install your-package-name
\`\`\`

## Usage
\`\`\`javascript
import { someFunction } from 'your-package-name';

// Example usage
someFunction();
\`\`\`

## Project Structure
- /src - Source code
- /tests - Test files
- /docs - Documentation

## License
MIT
`;
      
      // Sample token usage data
      const sampleTokenUsage = {
        promptTokens: 3245,
        completionTokens: 512,
        totalTokens: 3757,
        maxTokens: 8192,
        usagePercentage: 45.9,
        filesIncluded: 12,
        filesSkipped: 3,
        filesTruncated: 2
      };
      
      setReadmeContent(sampleReadme);
      setTokenUsage(sampleTokenUsage);
      setActiveTab('preview');
    } catch (error) {
      console.error('Error generating README:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Only render when activeTab is set (client-side)
  if (activeTab === null) {
    return null; // Return null during SSR to prevent hydration mismatch
  }

  return (
    <div className="container mx-auto py-8 px-4">
      <h1 className="text-3xl font-bold mb-8 text-center">Generate README</h1>
      
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full mb-8">
        <TabsList className="grid w-full grid-cols-3 mb-8">
          <TabsTrigger value="input" className="flex items-center gap-1">
            <FileText className="h-4 w-4" />
            Repository
          </TabsTrigger>
          <TabsTrigger value="preview" className="flex items-center gap-1" disabled={!readmeContent}>
            <FileText className="h-4 w-4" />
            Preview
          </TabsTrigger>
          <TabsTrigger value="stats" className="flex items-center gap-1" disabled={!readmeContent}>
            <BarChart className="h-4 w-4" />
            Stats
          </TabsTrigger>
        </TabsList>
        
        <TabsContent value="input" className="space-y-8">
          <RepositoryInput onSubmit={handleSubmit} isLoading={isLoading} />
          <GenerationSettings onSettingsChange={setSettings} defaultSettings={settings} />
        </TabsContent>
        
        <TabsContent value="preview">
          {readmeContent && (
            <ReadmePreview 
              markdown={readmeContent} 
              repoName={repoUrl.split('/').pop()?.replace('.git', '') || 'Repository'} 
            />
          )}
        </TabsContent>
        
        <TabsContent value="stats">
          {readmeContent && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <TokenUsage tokenUsage={tokenUsage} />
              <div className="space-y-4">
                <h2 className="text-xl font-bold">Generation Settings</h2>
                <div className="bg-muted p-4 rounded-md">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-muted-foreground">Repository</p>
                      <p className="font-medium truncate">{repoUrl}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Model</p>
                      <p className="font-medium">{settings.model}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Tone</p>
                      <p className="font-medium">{settings.tone}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Detail Level</p>
                      <p className="font-medium">{settings.mode}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
} 