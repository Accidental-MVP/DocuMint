'use client';

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Download, Copy, FileText, Code, Eye } from 'lucide-react'

interface ReadmePreviewProps {
  markdown: string
  repoName?: string
}

export function ReadmePreview({ markdown, repoName = 'Repository' }: ReadmePreviewProps) {
  // Use null as initial state to prevent hydration mismatch
  const [activeTab, setActiveTab] = useState<string | null>(null)
  const [isMounted, setIsMounted] = useState(false)

  // Set initial state after component mounts to avoid hydration mismatch
  useEffect(() => {
    setActiveTab('preview')
    setIsMounted(true)
  }, [])

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(markdown)
      alert('README copied to clipboard!')
    } catch (err) {
      console.error('Failed to copy text: ', err)
    }
  }

  const downloadMarkdown = () => {
    const element = document.createElement('a')
    const file = new Blob([markdown], { type: 'text/markdown' })
    element.href = URL.createObjectURL(file)
    element.download = 'README.md'
    document.body.appendChild(element)
    element.click()
    document.body.removeChild(element)
  }

  // This is a placeholder. In a real app, you would use a proper markdown renderer
  // like react-markdown or remark/rehype
  const renderMarkdown = () => {
    return (
      <div className="prose prose-sm dark:prose-invert max-w-none">
        <div dangerouslySetInnerHTML={{ __html: `<pre>${markdown}</pre>` }} />
      </div>
    )
  }

  // Only render when component is mounted (client-side)
  if (!isMounted || activeTab === null) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            README Preview for {repoName}
          </CardTitle>
          <CardDescription>
            Preview and download your generated README
          </CardDescription>
        </CardHeader>
        <CardContent className="h-[500px] flex items-center justify-center">
          <p>Loading preview...</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="h-5 w-5" />
          README Preview for {repoName}
        </CardTitle>
        <CardDescription>
          Preview and download your generated README
        </CardDescription>
      </CardHeader>
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <div className="px-6">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="preview" className="flex items-center gap-1">
              <Eye className="h-4 w-4" />
              Preview
            </TabsTrigger>
            <TabsTrigger value="markdown" className="flex items-center gap-1">
              <Code className="h-4 w-4" />
              Markdown
            </TabsTrigger>
          </TabsList>
        </div>
        <TabsContent value="preview" className="p-0">
          <CardContent className="max-h-[500px] overflow-y-auto border-t pt-6">
            {renderMarkdown()}
          </CardContent>
        </TabsContent>
        <TabsContent value="markdown" className="p-0">
          <CardContent className="max-h-[500px] overflow-y-auto border-t pt-6">
            <pre className="bg-muted p-4 rounded-md overflow-x-auto text-sm">
              <code>{markdown}</code>
            </pre>
          </CardContent>
        </TabsContent>
      </Tabs>
      <CardFooter className="flex justify-between border-t bg-muted/50 p-4">
        <div className="text-sm text-muted-foreground">
          {markdown.length} characters
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={copyToClipboard}>
            <Copy className="h-4 w-4 mr-1" />
            Copy
          </Button>
          <Button variant="default" size="sm" onClick={downloadMarkdown}>
            <Download className="h-4 w-4 mr-1" />
            Download
          </Button>
        </div>
      </CardFooter>
    </Card>
  )
} 