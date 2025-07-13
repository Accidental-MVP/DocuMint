import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { FileText, Code, Settings, BarChart, ArrowRight, Check, Star } from "lucide-react";
import Link from "next/link";

export default function Home() {
  return (
    <>
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        {/* Background gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-primary-50 via-background to-background -z-10" />
        
        {/* Hero content */}
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-16 md:py-24 lg:py-32">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="heading-1 mb-6">
              Generate <span className="gradient-text">Professional READMEs</span> with AI
            </h1>
            <p className="text-xl text-muted-700 mb-10 max-w-2xl mx-auto">
              DocuMint uses advanced AI to analyze your GitHub repositories and create
              compelling, detailed README files in seconds.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" className="bg-primary hover:bg-primary-600 transition-colors text-base h-12 px-6" asChild>
                <Link href="/generate">
                  Get Started
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
              <Button size="lg" variant="outline" className="border-primary text-primary hover:bg-primary-50 transition-colors text-base h-12 px-6" asChild>
                <Link href="/docs">
                  Learn More
                </Link>
              </Button>
            </div>
            
            {/* Trusted by */}
            <div className="mt-16">
              <p className="text-sm text-muted-500 mb-6">TRUSTED BY DEVELOPERS FROM</p>
              <div className="flex flex-wrap justify-center gap-8 md:gap-12 opacity-70">
                <div className="h-8 text-muted-700">Microsoft</div>
                <div className="h-8 text-muted-700">Google</div>
                <div className="h-8 text-muted-700">Amazon</div>
                <div className="h-8 text-muted-700">Meta</div>
                <div className="h-8 text-muted-700">Stripe</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 md:py-24 bg-muted-50">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl mx-auto text-center mb-16">
            <h2 className="heading-2 mb-4">Powerful Features</h2>
            <p className="text-lg text-muted-600">
              Everything you need to create perfect documentation for your projects
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            <Card className="card-hover border-border/40">
              <CardHeader className="pb-2">
                <div className="w-12 h-12 rounded-lg bg-primary-100 flex items-center justify-center mb-4">
                  <FileText className="h-6 w-6 text-primary-600" />
                </div>
                <CardTitle className="text-xl">Smart Analysis</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-600">
                  Analyzes your codebase to understand structure, dependencies, and functionality.
                </p>
              </CardContent>
            </Card>

            <Card className="card-hover border-border/40">
              <CardHeader className="pb-2">
                <div className="w-12 h-12 rounded-lg bg-secondary-100 flex items-center justify-center mb-4">
                  <Settings className="h-6 w-6 text-secondary-600" />
                </div>
                <CardTitle className="text-xl">Customizable</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-600">
                  Choose from multiple tones, detail levels, and formatting options.
                </p>
              </CardContent>
            </Card>

            <Card className="card-hover border-border/40">
              <CardHeader className="pb-2">
                <div className="w-12 h-12 rounded-lg bg-accent-100 flex items-center justify-center mb-4">
                  <BarChart className="h-6 w-6 text-accent-600" />
                </div>
                <CardTitle className="text-xl">Token Optimization</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-600">
                  Advanced token management ensures the most important information is included.
                </p>
              </CardContent>
            </Card>

            <Card className="card-hover border-border/40">
              <CardHeader className="pb-2">
                <div className="w-12 h-12 rounded-lg bg-muted-200 flex items-center justify-center mb-4">
                  <Code className="h-6 w-6 text-muted-700" />
                </div>
                <CardTitle className="text-xl">Code Aware</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-600">
                  Understands your code context to highlight key features and usage examples.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-16 md:py-24">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl mx-auto text-center mb-16">
            <h2 className="heading-2 mb-4">How It Works</h2>
            <p className="text-lg text-muted-600">
              Generate professional READMEs in three simple steps
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
            <div className="flex flex-col items-center text-center">
              <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-6 relative">
                <span className="text-2xl font-bold text-primary">1</span>
                <div className="absolute -right-8 top-1/2 h-0.5 w-16 bg-muted-200 hidden md:block"></div>
              </div>
              <h3 className="text-xl font-semibold mb-3">Enter Repository URL</h3>
              <p className="text-muted-600">
                Provide the URL to your GitHub repository and select your preferences for tone and detail level.
              </p>
            </div>

            <div className="flex flex-col items-center text-center">
              <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-6 relative">
                <span className="text-2xl font-bold text-primary">2</span>
                <div className="absolute -right-8 top-1/2 h-0.5 w-16 bg-muted-200 hidden md:block"></div>
              </div>
              <h3 className="text-xl font-semibold mb-3">AI Analysis</h3>
              <p className="text-muted-600">
                Our AI analyzes your code, structure, and documentation to understand your project's purpose and features.
              </p>
            </div>

            <div className="flex flex-col items-center text-center">
              <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-6">
                <span className="text-2xl font-bold text-primary">3</span>
              </div>
              <h3 className="text-xl font-semibold mb-3">Generate README</h3>
              <p className="text-muted-600">
                Receive a professionally formatted README tailored to your project's needs, ready to use or customize further.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="py-16 md:py-24 bg-muted-50">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl mx-auto text-center mb-16">
            <h2 className="heading-2 mb-4">Loved by Developers</h2>
            <p className="text-lg text-muted-600">
              See what others are saying about DocuMint
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <Card className="border-border/40">
              <CardHeader>
                <div className="flex items-center gap-1 text-amber-400 mb-4">
                  <Star className="h-5 w-5 fill-current" />
                  <Star className="h-5 w-5 fill-current" />
                  <Star className="h-5 w-5 fill-current" />
                  <Star className="h-5 w-5 fill-current" />
                  <Star className="h-5 w-5 fill-current" />
                </div>
                <CardTitle className="text-lg">"Saved me hours of documentation work"</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-600">
                  DocuMint generated a README that perfectly captured my project's functionality and purpose. I was amazed at how accurate it was!
                </p>
              </CardContent>
              <CardFooter>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-muted-200"></div>
                  <div>
                    <p className="font-medium">Alex Chen</p>
                    <p className="text-sm text-muted-500">Senior Developer @ Acme Inc.</p>
                  </div>
                </div>
              </CardFooter>
            </Card>
            
            <Card className="border-border/40">
              <CardHeader>
                <div className="flex items-center gap-1 text-amber-400 mb-4">
                  <Star className="h-5 w-5 fill-current" />
                  <Star className="h-5 w-5 fill-current" />
                  <Star className="h-5 w-5 fill-current" />
                  <Star className="h-5 w-5 fill-current" />
                  <Star className="h-5 w-5 fill-current" />
                </div>
                <CardTitle className="text-lg">"Professional documentation in seconds"</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-600">
                  I used to dread writing documentation. With DocuMint, I can focus on coding and let the AI handle the README. Game changer!
                </p>
              </CardContent>
              <CardFooter>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-muted-200"></div>
                  <div>
                    <p className="font-medium">Sarah Johnson</p>
                    <p className="text-sm text-muted-500">Frontend Developer @ TechCorp</p>
                  </div>
                </div>
              </CardFooter>
            </Card>
            
            <Card className="border-border/40">
              <CardHeader>
                <div className="flex items-center gap-1 text-amber-400 mb-4">
                  <Star className="h-5 w-5 fill-current" />
                  <Star className="h-5 w-5 fill-current" />
                  <Star className="h-5 w-5 fill-current" />
                  <Star className="h-5 w-5 fill-current" />
                  <Star className="h-5 w-5 fill-current" />
                </div>
                <CardTitle className="text-lg">"Impressive attention to detail"</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-600">
                  The AI picked up on subtle aspects of my codebase that I wouldn't have thought to document. My project looks much more professional now.
                </p>
              </CardContent>
              <CardFooter>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-muted-200"></div>
                  <div>
                    <p className="font-medium">Michael Rodriguez</p>
                    <p className="text-sm text-muted-500">Lead Engineer @ DevStudio</p>
                  </div>
                </div>
              </CardFooter>
            </Card>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="py-16 md:py-24">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl mx-auto text-center mb-16">
            <h2 className="heading-2 mb-4">Simple, Transparent Pricing</h2>
            <p className="text-lg text-muted-600">
              Choose the plan that's right for you
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <Card className="border-border/40">
              <CardHeader>
                <CardTitle>Free</CardTitle>
                <CardDescription className="text-3xl font-bold">$0<span className="text-sm font-normal text-muted-500">/month</span></CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <ul className="space-y-2">
                  <li className="flex items-center gap-2">
                    <Check className="h-5 w-5 text-accent-500" />
                    <span>5 READMEs per month</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <Check className="h-5 w-5 text-accent-500" />
                    <span>Basic customization</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <Check className="h-5 w-5 text-accent-500" />
                    <span>Standard templates</span>
                  </li>
                </ul>
              </CardContent>
              <CardFooter>
                <Button variant="outline" className="w-full">Get Started</Button>
              </CardFooter>
            </Card>
            
            <Card className="border-primary/20 shadow-lg relative">
              <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 bg-primary text-white text-sm font-medium py-1 px-3 rounded-full">
                Most Popular
              </div>
              <CardHeader>
                <CardTitle>Pro</CardTitle>
                <CardDescription className="text-3xl font-bold">$12<span className="text-sm font-normal text-muted-500">/month</span></CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <ul className="space-y-2">
                  <li className="flex items-center gap-2">
                    <Check className="h-5 w-5 text-accent-500" />
                    <span>Unlimited READMEs</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <Check className="h-5 w-5 text-accent-500" />
                    <span>Advanced customization</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <Check className="h-5 w-5 text-accent-500" />
                    <span>Premium templates</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <Check className="h-5 w-5 text-accent-500" />
                    <span>Priority support</span>
                  </li>
                </ul>
              </CardContent>
              <CardFooter>
                <Button className="w-full">Subscribe Now</Button>
              </CardFooter>
            </Card>
            
            <Card className="border-border/40">
              <CardHeader>
                <CardTitle>Enterprise</CardTitle>
                <CardDescription className="text-3xl font-bold">Custom<span className="text-sm font-normal text-muted-500"> pricing</span></CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <ul className="space-y-2">
                  <li className="flex items-center gap-2">
                    <Check className="h-5 w-5 text-accent-500" />
                    <span>Everything in Pro</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <Check className="h-5 w-5 text-accent-500" />
                    <span>Custom integrations</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <Check className="h-5 w-5 text-accent-500" />
                    <span>Dedicated support</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <Check className="h-5 w-5 text-accent-500" />
                    <span>SLA guarantees</span>
                  </li>
                </ul>
              </CardContent>
              <CardFooter>
                <Button variant="outline" className="w-full">Contact Sales</Button>
              </CardFooter>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 md:py-24 bg-primary-50">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="heading-2 mb-6">Ready to create the perfect README?</h2>
            <p className="text-xl text-muted-700 mb-8 max-w-2xl mx-auto">
              Join thousands of developers who use DocuMint to showcase their projects with professional documentation.
            </p>
            <Button size="lg" className="bg-primary hover:bg-primary-600 transition-colors text-base h-12 px-8" asChild>
              <Link href="/generate">
                Generate Your README
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </div>
        </div>
      </section>
    </>
  );
}
