'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Sparkles, AlertCircle, Check, Loader2 } from 'lucide-react';
import { GenerationSettings, ToneOption, ModelOption, ModeOption } from './generation-settings';
import { apiClient } from '@/lib/api-client';
import ReactMarkdown from 'react-markdown';

interface ReadmeGenerationProps {
  repoUrl: string;
}

export function ReadmeGeneration({ repoUrl }: ReadmeGenerationProps) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [readmeContent, setReadmeContent] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [settings, setSettings] = useState({
    tone: 'professional' as ToneOption,
    model: 'gpt-4' as ModelOption,
    mode: 'standard' as ModeOption
  });

  const handleSettingsChange = (newSettings: any) => {
    setSettings(newSettings);
  };

  const generateReadme = async () => {
    setIsGenerating(true);
    setError(null);
    setReadmeContent('');
    
    try {
      const response = await apiClient.post('/generate', {
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
    } catch (err: any) {
      setError(err.message || 'Error generating README');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5" />
            README Generation
          </CardTitle>
          <CardDescription>
            Generate a README for your GitHub repository
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
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

      {readmeContent && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Check className="h-5 w-5" />
              Generated README
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="bg-muted rounded-md p-4 overflow-auto max-h-[500px]">
              <ReactMarkdown className="prose dark:prose-invert max-w-none">
                {readmeContent}
              </ReactMarkdown>
            </div>
          </CardContent>
          <CardFooter>
            <Button 
              variant="outline" 
              onClick={() => navigator.clipboard.writeText(readmeContent)}
            >
              Copy to Clipboard
            </Button>
          </CardFooter>
        </Card>
      )}
    </div>
  );
} 