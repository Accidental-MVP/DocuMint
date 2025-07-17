/**
 * API client for interacting with the DocuMint backend
 */
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs';

// API base URL - will be different in development vs production
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

// Debug mode
const DEBUG = true;

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
 * Debug log function
 */
function debugLog(...args: any[]) {
  if (DEBUG) {
    console.log('[API Client]', ...args);
  }
}

/**
 * Get authentication token from Supabase
 */
async function getAuthToken(): Promise<string | null> {
  try {
    debugLog('Getting auth token from Supabase...');
    const supabase = createClientComponentClient();
    const { data } = await supabase.auth.getSession();
    
    if (!data.session) {
      debugLog('No session found');
      return null;
    }
    
    debugLog('Session found, user:', data.session.user.email);
    
    // First try to get the session token (this is what Supabase uses internally)
    if (data.session?.access_token) {
      debugLog('Using access token');
      
      // Log token details for debugging (safely)
      try {
        const tokenParts = data.session.access_token.split('.');
        if (tokenParts.length === 3) {
          const payload = JSON.parse(atob(tokenParts[1]));
          debugLog('Token payload:', {
            exp: payload.exp ? new Date(payload.exp * 1000).toISOString() : 'none',
            iat: payload.iat ? new Date(payload.iat * 1000).toISOString() : 'none',
            sub: payload.sub ? payload.sub.substring(0, 8) + '...' : 'none',
            email: payload.email ? payload.email : 'none',
            hasAud: !!payload.aud,
            hasRole: !!payload.role
          });
          
          // Check if token is expired
          if (payload.exp && payload.exp < Date.now() / 1000) {
            debugLog('Token is expired! Refreshing session...');
            const { data: refreshData } = await supabase.auth.refreshSession();
            if (refreshData.session?.access_token) {
              debugLog('Session refreshed successfully');
              return refreshData.session.access_token;
            } else {
              debugLog('Failed to refresh session');
              return null;
            }
          }
        }
      } catch (e) {
        debugLog('Error parsing token:', e);
      }
      
      return data.session.access_token;
    }
    
    debugLog('No token available');
    return null;
  } catch (error) {
    console.error('Error getting auth token:', error);
    return null;
  }
}

/**
 * Generate a README for a GitHub repository
 */
export async function generateReadme(request: GenerateRequest): Promise<GenerateResponse> {
  try {
    debugLog('Generating README for repo:', request.repo_url);
    
    // Get authentication token
    const token = await getAuthToken();
    
    if (!token) {
      debugLog('No authentication token available');
      throw new Error('Not authenticated. Please sign in to use this feature.');
    }
    
    debugLog('Using token:', token.substring(0, 10) + '...');
    
    // Get user info for debug headers
    let userId = null;
    try {
      const tokenParts = token.split('.');
      if (tokenParts.length === 3) {
        const payload = JSON.parse(atob(tokenParts[1]));
        userId = payload.sub;
      }
    } catch (e) {
      debugLog('Error extracting user ID from token:', e);
    }
    
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    };
    
    // Add debug headers in development
    if (process.env.NODE_ENV === 'development' && userId) {
      debugLog('Adding debug user ID header');
      headers['X-Debug-User-ID'] = userId;
    }
    
    debugLog('Request headers:', headers);
    debugLog('Request body:', request);
    
    const response = await fetch(`${API_BASE_URL}/generate`, {
      method: 'POST',
      headers,
      body: JSON.stringify(request),
    });

    debugLog('Response status:', response.status);
    
    if (!response.ok) {
      if (response.status === 401) {
        debugLog('Authentication failed (401)');
        
        // Try to refresh the session
        debugLog('Attempting to refresh session...');
        const supabase = createClientComponentClient();
        const { data: refreshData, error: refreshError } = await supabase.auth.refreshSession();
        
        if (refreshError) {
          debugLog('Session refresh failed:', refreshError.message);
          throw new Error('Authentication expired. Please sign in again.');
        }
        
        if (refreshData.session) {
          debugLog('Session refreshed, retrying request');
          // Retry the request with the new token
          const newToken = refreshData.session.access_token;
          const newHeaders = {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${newToken}`
          };
          
          const retryResponse = await fetch(`${API_BASE_URL}/generate`, {
            method: 'POST',
            headers: newHeaders,
            body: JSON.stringify(request),
          });
          
          if (retryResponse.ok) {
            const responseData = await retryResponse.json();
            debugLog('Retry successful, response data:', responseData);
            return responseData;
          } else {
            debugLog('Retry failed with status:', retryResponse.status);
            throw new Error('Not authenticated. Please sign in again.');
          }
        } else {
          throw new Error('Not authenticated. Please sign in again.');
        }
      }
      
      const errorText = await response.text();
      debugLog('Error response:', errorText);
      
      let errorData;
      try {
        errorData = JSON.parse(errorText);
      } catch (e) {
        debugLog('Failed to parse error response as JSON');
        errorData = { detail: errorText };
      }
      
      throw new Error(errorData.detail || 'Failed to generate README');
    }

    const responseData = await response.json();
    debugLog('Response data:', responseData);
    
    return responseData;
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
    debugLog('Fetching available models');
    const response = await fetch(`${API_BASE_URL}/models`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch models');
    }

    const data: ModelsResponse = await response.json();
    debugLog('Models:', data.models);
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
    debugLog('Fetching generation modes');
    const response = await fetch(`${API_BASE_URL}/modes`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch modes');
    }

    const data: ModesResponse = await response.json();
    debugLog('Modes:', data.modes);
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
    debugLog('Checking API health');
    const response = await fetch(`${API_BASE_URL}/health`);
    const isHealthy = response.ok;
    debugLog('API health:', isHealthy ? 'Healthy' : 'Unhealthy');
    return isHealthy;
  } catch (error) {
    console.error('API health check failed:', error);
    return false;
  }
} 