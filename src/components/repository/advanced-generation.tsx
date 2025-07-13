'use client';

import { useState, useEffect, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Sparkles, AlertCircle, Check, Loader2, FileText, Zap } from 'lucide-react';
import { GenerationSettings, ToneOption, ModelOption, ModeOption } from './generation-settings';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { apiClient } from '@/lib/api-client';
import ReactMarkdown from 'react-markdown';

interface AdvancedGenerationProps {
  repoUrl: string;
}

export function AdvancedGeneration({ repoUrl }: AdvancedGenerationProps) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [streamingContent, setStreamingContent] = useState<string>('');
  const [readmeContent, setReadmeContent] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [generationMethod, setGenerationMethod] = useState<'standard' | 'advanced' | 'streaming'>('advanced');
  const [settings, setSettings] = useState({
    tone: 'professional' as ToneOption,
    model: 'gpt-4-1106-preview' as ModelOption,
    mode: 'standard' as ModeOption
  });
  
  const streamRef = useRef<ReadableStreamDefaultReader | null>(null);
  const streamDecoder = useRef(new TextDecoder());
  
  // Clean up stream on unmount
  useEffect(() => {
    return () => {
      if (streamRef.current) {
        streamRef.current.cancel();
      }
    };
  }, []);

  const handleSettingsChange = (newSettings: any) => {
    setSettings(newSettings);
  };

  const generateReadme = async () => {
    setIsGenerating(true);
    setError(null);
    setReadmeContent('');
    setStreamingContent('');
    
    try {
      if (generationMethod === 'streaming') {
        // Handle streaming generation
        await generateStreamingReadme();
      } else {
        // Handle standard or advanced generation
        const endpoint = generationMethod === 'standard' ? '/api/generate' : '/api/advanced-generate';
        const response = await apiClient.post(endpoint, {
          repo_url: repoUrl,
          tone: settings.tone,
          model: settings.model,
          mode: settings.mode
        });
        
        if (response.data.success) {
          setReadmeContent(response.data.readme);
        } else {
          setError(response.data.error || 'Unknown error occurred');
        }
      }
    } catch (err: any) {
      setError(err.message || 'Error generating README');
    } finally {
      setIsGenerating(false);
    }
  };
  
  const generateStreamingReadme = async () => {
    try {
      // Use fetch directly for streaming
      const response = await fetch('/api/stream-generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          repo_url: repoUrl,
          tone: settings.tone,
          model: settings.model
        }),
      });
      
      if (!response.ok) {
        throw new Error(`Server responded with ${response.status}`);
      }
      
      if (!response.body) {
        throw new Error('Response body is null');
      }
      
      // Get reader from response body stream
      const reader = response.body.getReader();
      streamRef.current = reader;
      
      // Read stream
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        // Decode and append to streaming content
        const chunk = streamDecoder.current.decode(value, { stream: true });
        setStreamingContent(prev => prev + chunk);
      }
    } catch (err: any) {
      setError(err.message || 'Error in streaming README generation');
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5" />
            Advanced README Generation
          </CardTitle>
          <CardDescription>
            Generate a comprehensive README using advanced AI strategies
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Tabs 
            defaultValue="advanced" 
            value={generationMethod}
            onValueChange={(value) => setGenerationMethod(value as 'standard' | 'advanced' | 'streaming')}
            className="w-full"
          >
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="standard" className="flex items-center gap-1">
                <FileText className="h-4 w-4" />
                Standard
              </TabsTrigger>
              <TabsTrigger value="advanced" className="flex items-center gap-1">
                <Sparkles className="h-4 w-4" />
                Advanced
              </TabsTrigger>
              <TabsTrigger value="streaming" className="flex items-center gap-1">
                <Zap className="h-4 w-4" />
                Streaming
              </TabsTrigger>
            </TabsList>
            <TabsContent value="standard" className="pt-4">
              <p className="text-sm text-muted-foreground">
                Standard generation creates a README in a single step. Fast but less comprehensive.
              </p>
            </TabsContent>
            <TabsContent value="advanced" className="pt-4">
              <p className="text-sm text-muted-foreground">
                Advanced generation uses multiple steps: planning, section-by-section generation, and refinement.
                Creates more comprehensive READMEs but takes longer.
              </p>
            </TabsContent>
            <TabsContent value="streaming" className="pt-4">
              <p className="text-sm text-muted-foreground">
                Streaming generation shows results in real-time as they're being created.
                See the README take shape before your eyes.
              </p>
            </TabsContent>
          </Tabs>

          <GenerationSettings onSettingsChange={handleSettingsChange} defaultSettings={settings} />
          
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>Error</AlertTitle>
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
        </CardContent>
        <CardFooter className="flex justify-between">
          <div className="flex items-center gap-2">
            <Badge variant="outline">{repoUrl.split('/').pop()}</Badge>
          </div>
          <Button 
            onClick={generateReadme} 
            disabled={isGenerating}
            className="flex items-center gap-2"
          >
            {isGenerating ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Sparkles className="h-4 w-4" />
                Generate README
              </>
            )}
          </Button>
        </CardFooter>
      </Card>

      {(readmeContent || streamingContent) && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Check className="h-5 w-5" />
              Generated README
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="bg-muted rounded-md p-4 overflow-auto max-h-[500px]">
              {generationMethod === 'streaming' ? (
                <ReactMarkdown className="prose dark:prose-invert max-w-none">
                  {streamingContent}
                </ReactMarkdown>
              ) : (
                <ReactMarkdown className="prose dark:prose-invert max-w-none">
                  {readmeContent}
                </ReactMarkdown>
              )}
            </div>
          </CardContent>
          <CardFooter>
            <Button 
              variant="outline" 
              onClick={() => {
                const content = generationMethod === 'streaming' ? streamingContent : readmeContent;
                navigator.clipboard.writeText(content);
              }}
            >
              Copy to Clipboard
            </Button>
          </CardFooter>
        </Card>
      )}
    </div>
  );
} 