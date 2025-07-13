import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { RepositoryForm } from '@/components/repository/repository-form';
import { ReadmeGeneration } from '@/components/repository/readme-generation';
import { AdvancedGeneration } from '@/components/repository/advanced-generation';
import { Sparkles, FileText } from 'lucide-react';

export default function Home() {
  return (
    <main className="container max-w-5xl mx-auto py-8 px-4">
      <div className="space-y-8">
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold tracking-tight">
            <span className="bg-gradient-to-r from-purple-500 to-blue-500 bg-clip-text text-transparent">
              DocuMint
            </span>
          </h1>
          <p className="text-lg text-muted-foreground">
            Generate beautiful README files for your GitHub repositories
          </p>
        </div>

        <RepositoryForm />

        <Tabs defaultValue="standard" className="w-full">
          <TabsList className="grid w-full max-w-md mx-auto grid-cols-2">
            <TabsTrigger value="standard" className="flex items-center gap-2">
              <FileText className="h-4 w-4" />
              Standard
            </TabsTrigger>
            <TabsTrigger value="advanced" className="flex items-center gap-2">
              <Sparkles className="h-4 w-4" />
              Advanced
            </TabsTrigger>
          </TabsList>
          <TabsContent value="standard" className="pt-6">
            <ReadmeGeneration repoUrl="https://github.com/fastapi-users/fastapi-users" />
          </TabsContent>
          <TabsContent value="advanced" className="pt-6">
            <AdvancedGeneration repoUrl="https://github.com/fastapi-users/fastapi-users" />
          </TabsContent>
        </Tabs>
      </div>
    </main>
  );
}
