'use client';

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Button } from '@/components/ui/button'
import { Sparkles, FileText, Settings2, Code, Zap, Loader2 } from 'lucide-react'
import { getAvailableModels, getGenerationModes, ModelInfo, ModeInfo } from '@/lib/api/client'
import { ReadmeTone, GenerationMode } from '@/lib/api/client'

export type ToneOption = ReadmeTone
export type ModelOption = string
export type ModeOption = GenerationMode

interface GenerationSettingsProps {
  onSettingsChange: (settings: {
    tone: ToneOption
    model: ModelOption
    mode: ModeOption
  }) => void
  defaultSettings?: {
    tone: ToneOption
    model: ModelOption
    mode: ModeOption
  }
}

export function GenerationSettings({
  onSettingsChange,
  defaultSettings = {
    tone: 'professional',
    model: 'gpt-4',
    mode: 'standard'
  }
}: GenerationSettingsProps) {
  const [settings, setSettings] = useState(defaultSettings)
  const [isMounted, setIsMounted] = useState(false)
  const [models, setModels] = useState<ModelInfo[]>([])
  const [modes, setModes] = useState<ModeInfo[]>([])
  const [isLoading, setIsLoading] = useState(false)
  
  useEffect(() => {
    setIsMounted(true)
    
    // Fetch models and modes from API
    const fetchData = async () => {
      setIsLoading(true)
      try {
        const [modelsData, modesData] = await Promise.all([
          getAvailableModels(),
          getGenerationModes()
        ])
        
        if (modelsData.length > 0) {
          setModels(modelsData)
        }
        
        if (modesData.length > 0) {
          setModes(modesData)
        }
      } catch (error) {
        console.error('Error fetching models or modes:', error)
      } finally {
        setIsLoading(false)
      }
    }
    
    fetchData()
  }, [])

  const updateSettings = (key: keyof typeof settings, value: string) => {
    const newSettings = {
      ...settings,
      [key]: value
    }
    setSettings(newSettings)
    onSettingsChange(newSettings as any)
  }

  // Simple placeholder during SSR or loading
  if (!isMounted || isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings2 className="h-5 w-5" />
            Generation Settings
          </CardTitle>
          <CardDescription>
            Customize how your README is generated
          </CardDescription>
        </CardHeader>
        <CardContent className="h-[300px] flex items-center justify-center">
          <div className="flex flex-col items-center gap-2">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <p>Loading settings...</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Settings2 className="h-5 w-5" />
          Generation Settings
        </CardTitle>
        <CardDescription>
          Customize how your README is generated
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Tone Selection */}
        <div className="space-y-2">
          <h3 className="text-sm font-medium">Tone</h3>
          <Tabs
            defaultValue={settings.tone}
            onValueChange={(value) => updateSettings('tone', value as ToneOption)}
            className="w-full"
          >
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="professional" className="flex items-center gap-1">
                <FileText className="h-4 w-4" />
                Professional
              </TabsTrigger>
              <TabsTrigger value="startup" className="flex items-center gap-1">
                <Zap className="h-4 w-4" />
                Startup
              </TabsTrigger>
              <TabsTrigger value="meme" className="flex items-center gap-1">
                <Sparkles className="h-4 w-4" />
                Meme
              </TabsTrigger>
            </TabsList>
          </Tabs>
        </div>

        {/* Model Selection */}
        <div className="space-y-2">
          <h3 className="text-sm font-medium">Model</h3>
          <Tabs
            defaultValue={settings.model}
            onValueChange={(value) => updateSettings('model', value as ModelOption)}
            className="w-full"
          >
            <TabsList className="grid w-full grid-cols-2">
              {models.length > 0 ? (
                models.map(model => (
                  <TabsTrigger 
                    key={model.id} 
                    value={model.id} 
                    className="flex items-center gap-1"
                  >
                    <Sparkles className="h-4 w-4" />
                    {model.name}
                  </TabsTrigger>
                ))
              ) : (
                <>
                  <TabsTrigger value="gpt-4" className="flex items-center gap-1">
                    <Sparkles className="h-4 w-4" />
                    GPT-4
                  </TabsTrigger>
                  <TabsTrigger value="gpt-3.5-turbo" className="flex items-center gap-1">
                    <Code className="h-4 w-4" />
                    GPT-3.5 Turbo
                  </TabsTrigger>
                </>
              )}
            </TabsList>
          </Tabs>
          <p className="text-xs text-muted-foreground mt-1">
            {models.find(m => m.id === settings.model)?.description || 
              (settings.model === 'gpt-4' 
                ? 'Most powerful model, best for complex README generation' 
                : 'Faster and more cost-effective model')}
          </p>
        </div>

        {/* Mode Selection */}
        <div className="space-y-2">
          <h3 className="text-sm font-medium">Detail Level</h3>
          <Tabs
            defaultValue={settings.mode}
            onValueChange={(value) => updateSettings('mode', value as ModeOption)}
            className="w-full"
          >
            <TabsList className="grid w-full grid-cols-4">
              {modes.length > 0 ? (
                modes.map(mode => (
                  <TabsTrigger key={mode.id} value={mode.id}>
                    {mode.name}
                  </TabsTrigger>
                ))
              ) : (
                <>
                  <TabsTrigger value="standard">Standard</TabsTrigger>
                  <TabsTrigger value="detailed">Detailed</TabsTrigger>
                  <TabsTrigger value="concise">Concise</TabsTrigger>
                  <TabsTrigger value="creative">Creative</TabsTrigger>
                </>
              )}
            </TabsList>
          </Tabs>
          <p className="text-xs text-muted-foreground mt-1">
            {modes.find(m => m.id === settings.mode)?.description || ''}
          </p>
        </div>
      </CardContent>
    </Card>
  )
} 