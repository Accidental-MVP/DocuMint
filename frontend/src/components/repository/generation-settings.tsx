'use client';

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Button } from '@/components/ui/button'
import { Sparkles, FileText, Settings2, Code, Zap } from 'lucide-react'

export type ToneOption = 'professional' | 'startup' | 'meme'
export type ModelOption = 'gpt-4' | 'gpt-3.5-turbo'
export type ModeOption = 'standard' | 'detailed' | 'concise' | 'creative'

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
  
  useEffect(() => {
    setIsMounted(true)
  }, [])

  const updateSettings = (key: keyof typeof settings, value: string) => {
    const newSettings = {
      ...settings,
      [key]: value
    }
    setSettings(newSettings)
    onSettingsChange(newSettings as any)
  }

  // Simple placeholder during SSR
  if (!isMounted) {
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
          <p>Loading settings...</p>
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
              <TabsTrigger value="gpt-4" className="flex items-center gap-1">
                <Sparkles className="h-4 w-4" />
                GPT-4
              </TabsTrigger>
              <TabsTrigger value="gpt-3.5-turbo" className="flex items-center gap-1">
                <Code className="h-4 w-4" />
                GPT-3.5 Turbo
              </TabsTrigger>
            </TabsList>
          </Tabs>
          <p className="text-xs text-muted-foreground mt-1">
            {settings.model === 'gpt-4' 
              ? 'Most powerful model, best for complex README generation' 
              : 'Faster and more cost-effective model'}
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
              <TabsTrigger value="standard">Standard</TabsTrigger>
              <TabsTrigger value="detailed">Detailed</TabsTrigger>
              <TabsTrigger value="concise">Concise</TabsTrigger>
              <TabsTrigger value="creative">Creative</TabsTrigger>
            </TabsList>
          </Tabs>
        </div>
      </CardContent>
    </Card>
  )
} 