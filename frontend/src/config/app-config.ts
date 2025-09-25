// Application configuration

export const config = {
  // API endpoint
  apiBaseUrl: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',
  
  // Feature flags
  features: {
    enablePersistence: true,
    enableAgentSelection: true,
    enableCharts: true,
    enableSqlResults: true,
  },
  
  // UI Configuration
  ui: {
    theme: {
      primary: '#4f46e5',
      secondary: '#9333ea',
      background: '#f9fafb',
      card: '#ffffff',
      border: '#e5e7eb',
      text: '#111827',
    },
    sidebar: {
      width: '260px',
    },
    chat: {
      maxMessageWidth: '80%',
    }
  },
  
  // Default system message
  defaultSystemMessage: 'This is an AI assistant that can query databases, retrieve information, and generate visualizations.',
};