'use client'

import { useState, useCallback } from 'react'
import ChatInterface from '~/components/chat/ChatInterface'
import Sidebar from '~/components/layout/Sidebar'
import { ChatMessage, Conversation, Agent } from '~/lib/types'
import { OrchestratorService, ApiError } from '~/services/api'
import { generateConversationId, parseErrorMessage } from '~/lib/utils'

export default function MainChat() {
  // Chat state
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [currentConversationId, setCurrentConversationId] = useState(() => generateConversationId())
  
  // Sidebar state
  const [conversations, setConversations] = useState<Record<string, Conversation>>({})
  const [selectedAgent] = useState<Agent>('orchestrator')
  const [sidebarOpen, setSidebarOpen] = useState(true)

  const handleSendMessage = async (messageContent: string) => {
    // Add user message
    const userMessage: ChatMessage = {
      id: `user_${Date.now()}`,
      role: 'user',
      content: messageContent,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)

    try {
      // Call orchestrator service
      const response = await OrchestratorService.query({
        query: messageContent,
        conversation_id: currentConversationId,
        user_id: 'frontend_user'
      })

      // Create assistant message with response data
      const assistantMessage: ChatMessage = {
        id: `assistant_${Date.now()}`,
        role: 'assistant',
        content: response.response?.final_answer || 'Tôi gặp sự cố khi xử lý yêu cầu của bạn.',
        timestamp: new Date(),
        response: response
      }

      const updatedMessages = [...messages, userMessage, assistantMessage]
      setMessages(updatedMessages)

      // Update conversation
      const conversationTitle = messageContent.length > 50 
        ? messageContent.substring(0, 50) + '...'
        : messageContent

      setConversations(prev => ({
        ...prev,
        [currentConversationId]: {
          id: currentConversationId,
          title: conversationTitle,
          messages: updatedMessages,
          lastUpdated: new Date().toISOString(),
          agent: selectedAgent
        }
      }))

    } catch (error) {
      // Create error message
      const errorMessage: ChatMessage = {
        id: `error_${Date.now()}`,
        role: 'assistant',
        content: error instanceof ApiError 
          ? parseErrorMessage(error.message)
          : 'Đã xảy ra lỗi không xác định. Vui lòng thử lại.',
        timestamp: new Date()
      }

      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleNewConversation = useCallback(() => {
    const newId = generateConversationId()
    setCurrentConversationId(newId)
    setMessages([])
  }, [])

  const handleSelectConversation = useCallback((id: string) => {
    const conversation = conversations[id]
    if (conversation) {
      setCurrentConversationId(id)
      setMessages(conversation.messages)
    }
  }, [conversations])

  const handleSelectAgent = useCallback((agent: Agent) => {
    // For now, we only support orchestrator
    console.log('Selected agent:', agent)
  }, [])

  return (
    <div className="h-screen flex bg-background">
      {/* Sidebar */}
      {sidebarOpen && (
        <Sidebar
          conversations={conversations}
          currentConversationId={currentConversationId}
          onSelectConversation={handleSelectConversation}
          onNewConversation={handleNewConversation}
          selectedAgent={selectedAgent}
          onSelectAgent={handleSelectAgent}
        />
      )}
      
      {/* Main Chat Area */}
      <div className={`flex-1 flex flex-col ${sidebarOpen ? 'ml-64' : ''}`}>
        {/* Header */}
        <header className="border-b bg-card px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-1 hover:bg-accent rounded-md transition-colors"
            >
              <svg 
                width="16" 
                height="16" 
                viewBox="0 0 24 24" 
                fill="none" 
                stroke="currentColor" 
                strokeWidth="2"
              >
                <line x1="3" y1="6" x2="21" y2="6"/>
                <line x1="3" y1="12" x2="21" y2="12"/>
                <line x1="3" y1="18" x2="21" y2="18"/>
              </svg>
            </button>
            <div>
              <h1 className="text-lg font-semibold">SQL RAG System</h1>
              <p className="text-xs text-muted-foreground">
                Multi-Agent System with SQL, RAG, and Visualization
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span>Connected</span>
            </div>
          </div>
        </header>

        {/* Chat Interface */}
        <div className="flex-1">
          <ChatInterface 
            messages={messages}
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
          />
        </div>
      </div>
    </div>
  )
}