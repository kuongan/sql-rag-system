// API Response Types
export interface ApiResponse<T = any> {
  success: boolean
  message?: string
  data?: T
  error?: string
}

// Agent Types
export interface AgentAction {
  tool_name: string
  args: Record<string, any>
  success?: boolean
  iteration?: number
  result?: any
}

export interface AgentResult {
  success: boolean
  sql_query?: string | null
  data?: any[]
  answer?: string
  error?: string | null
  agent_type?: string
  plot_type?: string
  figure_json?: any
  analysis?: string
  chart_config?: any
  image_base64?: string
}

// Orchestrator Response
export interface OrchestratorResponse {
  success: boolean
  query: string
  intent?: string | null
  response: {
    final_answer: string
    thought?: string
    actions_taken: AgentAction[]
    agents_used: string[]
    data?: any
    visualization?: {
      type: string
      image_base64?: string
      config?: any
    }
  }
  conversation_history?: ConversationMessage[]
  conversation_id: string
  user_id: string
}

// Conversation Types
export interface ConversationMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  actions?: AgentAction[]
  thought?: string
  error?: boolean
}

// Query Request
export interface QueryRequest {
  query: string
  conversation_id?: string
  user_id?: string
  context?: any
}

// Chart/Visualization Types
export interface ChartData {
  labels: string[]
  datasets: {
    label: string
    data: number[]
    backgroundColor?: string[]
    borderColor?: string[]
  }[]
}

export interface ChartConfig {
  type: 'bar' | 'line' | 'pie' | 'scatter' | 'histogram'
  x_column?: string
  y_column?: string
  title?: string
  responsive?: boolean
}