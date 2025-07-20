'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { apiClient } from '@/lib/api-client';

interface EnhancedGenerationProps {
  repoUrl: string;
}

type ToneOption = 'professional' | 'startup' | 'meme' | 'technical' | 'friendly';
type ModelOption = 'gpt-4' | 'gpt-4-1106-preview' | 'gpt-4o' | 'gpt-4o-mini';
type GenerationMethod = 'enhanced' | 'streaming-enhanced';

export function EnhancedGeneration({ repoUrl }: EnhancedGenerationProps) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [readmeContent, setReadmeContent] = useState<string>('');
  const [streamingContent, setStreamingContent] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<any>(null);
  const [generationMethod, setGenerationMethod] = useState<GenerationMethod>('enhanced');
  const [settings, setSettings] = useState({
    tone: 'professional' as ToneOption,
    model: 'gpt-4-1106-preview' as ModelOption
  });

  const handleSettingsChange = (newSettings: any) => {
    setSettings(newSettings);
  };

  const generateStreamingEnhancedReadme = async () => {
    try {
      const response = await fetch('/api/stream-enhanced-generate', {
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
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body');
      }

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const content = line.slice(6);
            setStreamingContent(prev => prev + content);
          }
        }
      }
    } catch (err: any) {
      setError(err.message || 'Error in streaming generation');
    }
  };

  const generateReadme = async () => {
    setIsGenerating(true);
    setError(null);
    setReadmeContent('');
    setStreamingContent('');
    setAnalysis(null);
    
    try {
      if (generationMethod === 'streaming-enhanced') {
        // Handle streaming enhanced generation
        await generateStreamingEnhancedReadme();
      } else {
        // Handle standard enhanced generation
        const response = await apiClient.post('/api/enhanced-generate', {
          repo_url: repoUrl,
          tone: settings.tone,
          model: settings.model
        });
        
        if (response.data.success) {
          setReadmeContent(response.data.readme);
          setAnalysis(response.data.analysis);
        } else {
          setError(response.data.error || 'Unknown error occurred');
        }
      }
    } catch (err: any) {
      setError(err.message || 'Error generating enhanced README');
    } finally {
      setIsGenerating(false);
    }
  };

  const copyToClipboard = async (content: string) => {
    try {
      await navigator.clipboard.writeText(content);
    } catch (err) {
      console.error('Failed to copy to clipboard:', err);
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            🧠 Oracle-Level README Generation
            <Badge variant="secondary">Enhanced</Badge>
          </CardTitle>
          <CardDescription>
            Uses advanced repository analysis to understand project structure, detect features, 
            and generate intelligent READMEs with deep insights.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Generation Method</label>
              <select
                value={generationMethod}
                onChange={(e) => setGenerationMethod(e.target.value as GenerationMethod)}
                className="w-full p-2 border rounded-md"
              >
                <option value="enhanced">Enhanced Analysis</option>
                <option value="streaming-enhanced">Streaming Enhanced</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Tone</label>
              <select
                value={settings.tone}
                onChange={(e) => handleSettingsChange({ ...settings, tone: e.target.value })}
                className="w-full p-2 border rounded-md"
              >
                <option value="professional">Professional</option>
                <option value="startup">Startup</option>
                <option value="meme">Meme</option>
                <option value="technical">Technical</option>
                <option value="friendly">Friendly</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Model</label>
              <select
                value={settings.model}
                onChange={(e) => handleSettingsChange({ ...settings, model: e.target.value })}
                className="w-full p-2 border rounded-md"
              >
                <option value="gpt-4-1106-preview">GPT-4 Turbo</option>
                <option value="gpt-4">GPT-4</option>
                <option value="gpt-4o">GPT-4o</option>
                <option value="gpt-4o-mini">GPT-4o Mini</option>
              </select>
            </div>
          </div>

          <Button 
            onClick={generateReadme} 
            disabled={isGenerating}
            className="w-full"
          >
            {isGenerating ? 'Generating Enhanced README...' : 'Generate Enhanced README'}
          </Button>

          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-md">
              <p className="text-red-800">{error}</p>
            </div>
          )}
        </CardContent>
      </Card>

      {analysis && (
        <Card>
          <CardHeader>
            <CardTitle>Repository Analysis</CardTitle>
            <CardDescription>Oracle-level insights from the repository analyzer</CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="summary" className="w-full">
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="summary">Summary</TabsTrigger>
                <TabsTrigger value="features">Features</TabsTrigger>
                <TabsTrigger value="tech-stack">Tech Stack</TabsTrigger>
                <TabsTrigger value="insights">Insights</TabsTrigger>
              </TabsList>
              
              <TabsContent value="summary" className="space-y-4">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">
                      {analysis.summary?.project_type || 'Unknown'}
                    </div>
                    <div className="text-sm text-gray-600">Project Type</div>
                  </div>
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">
                      {analysis.summary?.type_confidence?.toFixed(2) || '0.00'}
                    </div>
                    <div className="text-sm text-gray-600">Confidence</div>
                  </div>
                  <div className="text-center p-4 bg-purple-50 rounded-lg">
                    <div className="text-2xl font-bold text-purple-600">
                      {analysis.summary?.feature_count || 0}
                    </div>
                    <div className="text-sm text-gray-600">Features</div>
                  </div>
                  <div className="text-center p-4 bg-orange-50 rounded-lg">
                    <div className="text-2xl font-bold text-orange-600">
                      {analysis.summary?.complexity_score?.toFixed(1) || '0.0'}
                    </div>
                    <div className="text-sm text-gray-600">Complexity</div>
                  </div>
                </div>
                
                <div className="p-4 bg-gray-50 rounded-lg">
                  <h4 className="font-semibold mb-2">Architecture Pattern</h4>
                  <p className="text-gray-700">{analysis.summary?.architecture_pattern || 'Unknown'}</p>
                </div>
              </TabsContent>
              
              <TabsContent value="features" className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {Object.entries(analysis.results?.features?.inferred_features || {}).map(([feature, data]: [string, any]) => (
                    <div key={feature} className="p-4 border rounded-lg">
                      <div className="flex justify-between items-start mb-2">
                        <h4 className="font-semibold capitalize">{feature.replace('_', ' ')}</h4>
                        <Badge variant="outline">{(data.confidence * 100).toFixed(0)}%</Badge>
                      </div>
                      <ul className="text-sm text-gray-600 space-y-1">
                        {data.evidence?.slice(0, 3).map((evidence: string, index: number) => (
                          <li key={index}>• {evidence}</li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </TabsContent>
              
              <TabsContent value="tech-stack" className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {Object.entries(analysis.summary?.tech_stack || {}).map(([category, technologies]: [string, any]) => (
                    <div key={category} className="p-4 border rounded-lg">
                      <h4 className="font-semibold mb-2 capitalize">{category}</h4>
                      <div className="flex flex-wrap gap-2">
                        {technologies.map((tech: string) => (
                          <Badge key={tech} variant="secondary">{tech}</Badge>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </TabsContent>
              
              <TabsContent value="insights" className="space-y-4">
                <div className="space-y-4">
                  {analysis.insights?.key_findings && (
                    <div className="p-4 bg-blue-50 rounded-lg">
                      <h4 className="font-semibold mb-2 text-blue-800">Key Findings</h4>
                      <ul className="space-y-1 text-blue-700">
                        {analysis.insights.key_findings.map((finding: string, index: number) => (
                          <li key={index}>• {finding}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {analysis.insights?.architecture_insights && (
                    <div className="p-4 bg-green-50 rounded-lg">
                      <h4 className="font-semibold mb-2 text-green-800">Architecture Insights</h4>
                      <ul className="space-y-1 text-green-700">
                        {analysis.insights.architecture_insights.map((insight: string, index: number) => (
                          <li key={index}>• {insight}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {analysis.insights?.recommendations && (
                    <div className="p-4 bg-purple-50 rounded-lg">
                      <h4 className="font-semibold mb-2 text-purple-800">Recommendations</h4>
                      <ul className="space-y-1 text-purple-700">
                        {analysis.insights.recommendations.map((rec: string, index: number) => (
                          <li key={index}>• {rec}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      )}

      {(readmeContent || streamingContent) && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              Generated README
              <Button
                variant="outline"
                size="sm"
                onClick={() => copyToClipboard(readmeContent || streamingContent)}
              >
                Copy to Clipboard
              </Button>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="bg-gray-50 p-4 rounded-lg max-h-96 overflow-y-auto">
              <pre className="whitespace-pre-wrap text-sm">
                {readmeContent || streamingContent}
              </pre>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
} 