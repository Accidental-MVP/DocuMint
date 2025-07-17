'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs';
import { RepositoryInput } from '@/components/repository/repository-input';
import { GenerationSettings, ToneOption, ModelOption, ModeOption } from '@/components/repository/generation-settings';
import { ReadmePreview } from '@/components/repository/readme-preview';
import { TokenUsage } from '@/components/repository/token-usage';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { FileText, Settings2, BarChart, AlertCircle, LogIn, Loader2 } from 'lucide-react';
import { generateReadme, getAvailableModels, getGenerationModes, checkApiHealth } from '@/lib/api/client';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';

export default function GeneratePage() {
  const router = useRouter();
  const supabase = createClientComponentClient();
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
  const [error, setError] = useState<string | null>(null);
  const [apiHealthy, setApiHealthy] = useState<boolean | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);
  
  // Set initial state after component mounts to avoid hydration mismatch
  useEffect(() => {
    setActiveTab('input');
    
    // Check API health on component mount
    const checkHealth = async () => {
      const isHealthy = await checkApiHealth();
      setApiHealthy(isHealthy);
    };
    
    // Check authentication status
    const checkAuth = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      setIsAuthenticated(!!session);
    };
    
    checkHealth();
    checkAuth();
  }, [supabase]);

  const handleRefreshSession = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const { data, error } = await supabase.auth.refreshSession();
      
      if (error) {
        setError(`Failed to refresh session: ${error.message}`);
        setIsAuthenticated(false);
      } else if (data.session) {
        setIsAuthenticated(true);
        setError(null);
      } else {
        setError('No session available. Please sign in again.');
        setIsAuthenticated(false);
      }
    } catch (error) {
      console.error('Error refreshing session:', error);
      setError('An unexpected error occurred while refreshing the session.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (url: string) => {
    if (!isAuthenticated) {
      setError('You must be signed in to generate a README. Please sign in and try again.');
      return;
    }
    
    setIsLoading(true);
    setRepoUrl(url);
    setError(null);
    
    try {
      const response = await generateReadme({
        repo_url: url,
        tone: settings.tone,
        model: settings.model,
        mode: settings.mode,
        max_files: 50 // Optional limit
      });
      
      if (response.success) {
        setReadmeContent(response.readme);
        
        // Extract token usage data from response
        if (response.processing_metadata) {
          const metadata = response.processing_metadata;
          const maxTokens = settings.model === 'gpt-4' ? 8192 : 4096;
          
          setTokenUsage({
            promptTokens: metadata.total_prompt_tokens,
            completionTokens: metadata.total_completion_tokens,
            totalTokens: metadata.total_tokens,
            maxTokens: maxTokens,
            usagePercentage: (metadata.total_tokens / maxTokens) * 100,
            filesIncluded: response.metadata?.files_included || 0,
            filesSkipped: response.metadata?.files_skipped || 0,
            filesTruncated: response.metadata?.files_truncated || 0
          });
        }
        
        setActiveTab('preview');
      } else {
        setError(response.error || 'Failed to generate README');
        
        // If authentication error, prompt to sign in again
        if (response.error?.includes('Not authenticated')) {
          setIsAuthenticated(false);
        }
      }
    } catch (error) {
      console.error('Error generating README:', error);
      setError('An unexpected error occurred. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSignIn = () => {
    router.push('/login');
  };

  // Only render when activeTab is set (client-side)
  if (activeTab === null) {
    return null; // Return null during SSR to prevent hydration mismatch
  }

  return (
    <div className="container mx-auto py-8 px-4">
      <h1 className="text-3xl font-bold mb-8 text-center">Generate README</h1>
      
      {apiHealthy === false && (
        <Alert variant="destructive" className="mb-6">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>API Connection Error</AlertTitle>
          <AlertDescription>
            Cannot connect to the API server. Please check that the backend is running and try again.
          </AlertDescription>
        </Alert>
      )}
      
      {isAuthenticated === false && (
        <Alert className="mb-6 bg-amber-50 border-amber-200">
          <LogIn className="h-4 w-4" />
          <AlertTitle>Authentication Required</AlertTitle>
          <AlertDescription className="flex items-center justify-between">
            <span>You need to be signed in to generate README files.</span>
            <div className="flex gap-2">
              <Button onClick={handleRefreshSession} variant="outline" disabled={isLoading}>
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Refreshing
                  </>
                ) : (
                  'Refresh Session'
                )}
              </Button>
              <Button onClick={handleSignIn}>Sign In</Button>
            </div>
          </AlertDescription>
        </Alert>
      )}
      
      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
      
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
          <RepositoryInput onSubmit={handleSubmit} isLoading={isLoading} disabled={isAuthenticated === false} />
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