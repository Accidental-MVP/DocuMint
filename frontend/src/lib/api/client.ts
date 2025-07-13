/**
 * API client for interacting with the DocuMint backend
 */

// API base URL - will be different in development vs production
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

// Types
export type ReadmeTone = 'professional' | 'startup' | 'meme';
export type GenerationMode = 'standard' | 'detailed' | 'concise' | 'creative';

export interface GenerateRequest {
  repo_url: string;
  tone: ReadmeTone;
  model: string;
  mode: GenerationMode;
  max_files?: number;
}

export interface FilePreview {
  path: string;
  preview: string;
}

export interface ProcessingMetadata {
  total_prompt_tokens: number;
  total_completion_tokens: number;
  total_tokens: number;
  chunk_errors: number;
  error_details?: Array<Record<string, any>>;
}

export interface GenerateResponse {
  success: boolean;
  readme: string;
  metadata?: Record<string, any>;
  error?: string;
  file_preview?: FilePreview[];
  processing_metadata?: ProcessingMetadata;
}

export interface ModelInfo {
  id: string;
  name: string;
  description: string;
  max_tokens: number;
}

export interface ModeInfo {
  id: string;
  name: string;
  description: string;
  temperature: number;
}

export interface ModelsResponse {
  models: ModelInfo[];
}

export interface ModesResponse {
  modes: ModeInfo[];
}

/**
 * Generate a README for a GitHub repository
 */
export async function generateReadme(request: GenerateRequest): Promise<GenerateResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to generate README');
    }

    return await response.json();
  } catch (error) {
    console.error('Error generating README:', error);
    return {
      success: false,
      readme: '',
      error: error instanceof Error ? error.message : 'An unknown error occurred',
    };
  }
}

/**
 * Get available models for README generation
 */
export async function getAvailableModels(): Promise<ModelInfo[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/models`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch models');
    }

    const data: ModelsResponse = await response.json();
    return data.models;
  } catch (error) {
    console.error('Error fetching models:', error);
    return [];
  }
}

/**
 * Get available generation modes
 */
export async function getGenerationModes(): Promise<ModeInfo[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/modes`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch modes');
    }

    const data: ModesResponse = await response.json();
    return data.modes;
  } catch (error) {
    console.error('Error fetching modes:', error);
    return [];
  }
}

/**
 * Check if the API is healthy
 */
export async function checkApiHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.ok;
  } catch (error) {
    console.error('API health check failed:', error);
    return false;
  }
} 