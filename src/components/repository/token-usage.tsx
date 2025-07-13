'use client';

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { BarChart, Gauge, FileText } from 'lucide-react'

interface TokenUsageProps {
  tokenUsage: {
    promptTokens: number
    completionTokens: number
    totalTokens: number
    maxTokens: number
    usagePercentage: number
    filesIncluded: number
    filesSkipped: number
    filesTruncated: number
  }
}

export function TokenUsage({ tokenUsage }: TokenUsageProps) {
  const [isMounted, setIsMounted] = useState(false)
  
  useEffect(() => {
    setIsMounted(true)
  }, [])

  const {
    promptTokens,
    completionTokens,
    totalTokens,
    maxTokens,
    usagePercentage,
    filesIncluded,
    filesSkipped,
    filesTruncated
  } = tokenUsage

  // Calculate percentages for the progress bars
  const promptPercentage = (promptTokens / maxTokens) * 100
  const completionPercentage = (completionTokens / maxTokens) * 100

  // Render a simple placeholder during SSR
  if (!isMounted) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart className="h-5 w-5" />
            Token Usage
          </CardTitle>
          <CardDescription>
            Analysis of token consumption and file processing
          </CardDescription>
        </CardHeader>
        <CardContent className="h-[400px] flex items-center justify-center">
          <p>Loading token usage data...</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BarChart className="h-5 w-5" />
          Token Usage
        </CardTitle>
        <CardDescription>
          Analysis of token consumption and file processing
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Token Usage Gauge */}
        <div className="flex flex-col items-center justify-center">
          <div className="relative w-32 h-32">
            <svg className="w-full h-full" viewBox="0 0 100 100">
              {/* Background circle */}
              <circle 
                cx="50" 
                cy="50" 
                r="45" 
                fill="none" 
                stroke="hsl(var(--muted))" 
                strokeWidth="10" 
              />
              {/* Progress arc - we're drawing an arc from 0 to the percentage */}
              <circle 
                cx="50" 
                cy="50" 
                r="45" 
                fill="none" 
                stroke="hsl(var(--primary))" 
                strokeWidth="10" 
                strokeDasharray={`${usagePercentage * 2.83} 283`} 
                strokeDashoffset="0" 
                strokeLinecap="round" 
                transform="rotate(-90 50 50)" 
              />
              <text 
                x="50" 
                y="50" 
                dominantBaseline="middle" 
                textAnchor="middle" 
                fontSize="16" 
                fontWeight="bold"
                fill="currentColor"
              >
                {Math.round(usagePercentage)}%
              </text>
              <text 
                x="50" 
                y="65" 
                dominantBaseline="middle" 
                textAnchor="middle" 
                fontSize="8"
                fill="currentColor"
              >
                Token Usage
              </text>
            </svg>
          </div>
        </div>

        {/* Token Breakdown */}
        <div className="space-y-3">
          <h3 className="text-sm font-medium">Token Breakdown</h3>
          
          <div className="space-y-1">
            <div className="flex justify-between text-xs">
              <span>Prompt Tokens</span>
              <span>{promptTokens.toLocaleString()} / {maxTokens.toLocaleString()}</span>
            </div>
            <div className="w-full bg-muted rounded-full h-2">
              <div 
                className="bg-primary rounded-full h-2" 
                style={{ width: `${promptPercentage}%` }}
              />
            </div>
          </div>
          
          <div className="space-y-1">
            <div className="flex justify-between text-xs">
              <span>Completion Tokens</span>
              <span>{completionTokens.toLocaleString()} / {maxTokens.toLocaleString()}</span>
            </div>
            <div className="w-full bg-muted rounded-full h-2">
              <div 
                className="bg-primary rounded-full h-2" 
                style={{ width: `${completionPercentage}%` }}
              />
            </div>
          </div>
          
          <div className="flex justify-between text-xs font-medium pt-1">
            <span>Total Tokens</span>
            <span>{totalTokens.toLocaleString()}</span>
          </div>
        </div>

        {/* File Processing Stats */}
        <div className="space-y-3">
          <h3 className="text-sm font-medium flex items-center gap-1">
            <FileText className="h-4 w-4" />
            File Processing
          </h3>
          
          <div className="grid grid-cols-3 gap-2">
            <div className="bg-muted/50 p-2 rounded-md text-center">
              <div className="text-2xl font-bold">{filesIncluded}</div>
              <div className="text-xs text-muted-foreground">Included</div>
            </div>
            <div className="bg-muted/50 p-2 rounded-md text-center">
              <div className="text-2xl font-bold">{filesTruncated}</div>
              <div className="text-xs text-muted-foreground">Truncated</div>
            </div>
            <div className="bg-muted/50 p-2 rounded-md text-center">
              <div className="text-2xl font-bold">{filesSkipped}</div>
              <div className="text-xs text-muted-foreground">Skipped</div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
} 