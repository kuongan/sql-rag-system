import { QueryRequest, OrchestratorResponse, ApiResponse } from '~/types/api'

// Use direct backend calls in development, Next.js API routes in production
const BASE_URL = process.env.NODE_ENV === 'development' 
  ? (process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000')
  : ''

class ApiError extends Error {
  constructor(
    message: string,
    public status?: number,
    public response?: any
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

/**
 * Get the correct endpoint based on environment
 */
function getApiEndpoint(endpoint: string): string {
  if (process.env.NODE_ENV === 'development') {
    // Direct to FastAPI in development
    return `${BASE_URL}${endpoint}`
  } else {
    // Use Next.js API routes in production
    return endpoint
  }
}

/**
 * Base API client with error handling
 */
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = getApiEndpoint(endpoint)
  
  const defaultOptions: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  }

  try {
    const response = await fetch(url, defaultOptions)
    const data = await response.json()
    
    if (!response.ok) {
      throw new ApiError(
        data.message || `HTTP error! status: ${response.status}`,
        response.status,
        data
      )
    }
    
    return data
  } catch (error) {
    if (error instanceof ApiError) {
      throw error
    }
    
    // Network or other errors
    throw new ApiError(
      error instanceof Error ? error.message : 'Unknown error occurred'
    )
  }
}

/**
 * Orchestrator Agent API
 */
export class OrchestratorService {
  /**
   * Send query to orchestrator agent via Next.js API route
   */
  static async query(request: QueryRequest): Promise<OrchestratorResponse> {
    return apiRequest<OrchestratorResponse>('/api/agents/query', {
      method: 'POST',
      body: JSON.stringify({
        query: request.query,
        conversation_id: request.conversation_id || 'default',
        user_id: request.user_id || 'anonymous',
        ...request.context && { context: request.context }
      }),
    })
  }

  /**
   * Get conversation history
   */
  static async getHistory(conversationId: string, userId: string = 'anonymous') {
    return apiRequest<{ history: any[] }>(`/api/conversations/${conversationId}`, {
      method: 'GET',
      headers: {
        'X-User-ID': userId,
      },
    })
  }
}

/**
 * Individual Agent Services (via Next.js API routes)
 */
export class SQLService {
  static async query(question: string, conversationId?: string) {
    return apiRequest<any>('/api/agents/sql/query', {
      method: 'POST',
      body: JSON.stringify({
        question,
        conversation_id: conversationId || 'default'
      }),
    })
  }
}

export class RAGService {
  static async query(question: string, conversationId?: string) {
    return apiRequest<any>('/api/agents/rag/query', {
      method: 'POST',
      body: JSON.stringify({
        question,
        conversation_id: conversationId || 'default'
      }),
    })
  }
}

export class PlottingService {
  static async create(data: any[], plotRequest: string, conversationId?: string) {
    return apiRequest<any>('/api/agents/plotting/create', {
      method: 'POST',
      body: JSON.stringify({
        data,
        plot_request: plotRequest,
        conversation_id: conversationId || 'default'
      }),
    })
  }
}

/**
 * Health check service
 */
export class HealthService {
  static async check() {
    return apiRequest<{ status: string; timestamp: string }>('/api/health')
  }
  
  static async agentStatus() {
    return apiRequest<{ agents: Record<string, any> }>('/api/agents/status')
  }
}

// Export the ApiError for error handling in components
export { ApiError }