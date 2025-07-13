import { Metadata } from "next";

// Metadata needs to be in a separate file since layout.tsx is a Client Component
export const metadata: Metadata = {
  title: "DocuMint - AI-Powered README Generator",
  description: "Generate professional README files for your GitHub repositories with AI",
  icons: {
    icon: "/favicon.ico",
  },
}; 