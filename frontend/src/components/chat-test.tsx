'use client'

import { useState } from 'react'
import { Button } from '~/components/ui/button'
import { Textarea } from '~/components/ui/textarea'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '~/components/ui/card'
import { Label } from '~/components/ui/label'
import { Badge } from '~/components/ui/badge'
import { ScrollArea } from '~/components/ui/scroll-area'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '~/components/ui/tabs'

// Import types and services
import { OrchestratorResponse, AgentAction } from '~/types/api'
import { OrchestratorService, ApiError } from '~/services/api'
import { 
  formatTimestamp, 
  decodeBase64Image, 
  extractDataInsights, 
  parseErrorMessage,
  generateConversationId,
  validateQuery 
} from '~/lib/utils'

export default function ChatTest() {
  const [query, setQuery] = useState('')
  const [response, setResponse] = useState<OrchestratorResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [conversationId] = useState(() => generateConversationId())
  const [useDirectBackend, setUseDirectBackend] = useState(process.env.NODE_ENV === 'development')

  const handleSubmit = async () => {
    // Validate query
    const validation = validateQuery(query)
    if (!validation.valid) {
      setError(validation.message || 'Invalid query')
      return
    }

    setLoading(true)
    setError(null)
    setResponse(null)

    try {
      // Choose between direct backend or Next.js proxy
      let data: OrchestratorResponse
      
      if (useDirectBackend) {
        // Direct call to FastAPI
        const response = await fetch('http://localhost:8000/api/agents/query', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            query: query.trim(),
            conversation_id: conversationId,
            user_id: 'frontend_user'
          }),
        })
        
        if (!response.ok) {
          throw new Error(`Backend error: ${response.status}`)
        }
        
        data = await response.json()
      } else {
        // Use service layer (Next.js proxy)
        data = await OrchestratorService.query({
          query: query.trim(),
          conversation_id: conversationId,
          user_id: 'frontend_user'
        })
      }
      
      setResponse(data)
    } catch (err) {
      if (err instanceof ApiError) {
        setError(parseErrorMessage(err.message))
      } else {
        setError(err instanceof Error ? err.message : 'Unknown error occurred')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            SQL RAG System - Backend Test
            <div className="flex items-center gap-2 text-sm">
              <Label htmlFor="direct-backend">Direct Backend</Label>
              <input
                id="direct-backend"
                type="checkbox"
                checked={useDirectBackend}
                onChange={(e) => setUseDirectBackend(e.target.checked)}
                className="w-4 h-4"
              />
              <Badge variant="outline" className="text-xs">
                {useDirectBackend ? 'Direct (Faster)' : 'Proxied (Secure)'}
              </Badge>
            </div>
          </CardTitle>
          <CardDescription>
            Test kết nối với multi-agent system. Hỗ trợ SQL queries, RAG search, và data visualization.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="query">Query</Label>
            <Textarea
              id="query"
              placeholder="Nhập câu hỏi của bạn... (Ví dụ: 'Show me top 10 flights and create a chart', 'What is the baggage policy?', 'Count total bookings')"
              value={query}
              onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setQuery(e.target.value)}
              onKeyDown={handleKeyPress}
              className="min-h-[100px]"
            />
            <p className="text-sm text-muted-foreground">
              Nhấn Ctrl+Enter hoặc Cmd+Enter để gửi
            </p>
          </div>
          
          <Button 
            onClick={handleSubmit} 
            disabled={loading || !query.trim()}
            className="w-full"
          >
            {loading ? 'Đang xử lý...' : 'Gửi Query'}
          </Button>
        </CardContent>
      </Card>

      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardHeader>
            <CardTitle className="text-red-800">Lỗi kết nối</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-red-600">{error}</p>
            <p className="text-sm text-red-500 mt-2">
              Đảm bảo backend đang chạy trên port 8000
            </p>
          </CardContent>
        </Card>
      )}

      {response && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              Kết quả 
              <Badge variant={response.success ? "default" : "destructive"}>
                {response.success ? 'Thành công' : 'Thất bại'}
              </Badge>
            </CardTitle>
            {response.response?.agents_used?.length > 0 && (
              <div className="flex gap-2">
                <span className="text-sm text-muted-foreground">Agents đã sử dụng:</span>
                {response.response.agents_used.map((agent: string, index: number) => (
                  <Badge key={index} variant="outline">
                    {agent}
                  </Badge>
                ))}
              </div>
            )}
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="result" className="w-full">
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="result">Kết quả</TabsTrigger>
                <TabsTrigger value="data">Dữ liệu</TabsTrigger>
                <TabsTrigger value="actions">Hành động</TabsTrigger>
                <TabsTrigger value="visualization">Biểu đồ</TabsTrigger>
              </TabsList>
              
              <TabsContent value="result" className="space-y-4">
                {response.response?.thought && (
                  <div className="space-y-2">
                    <Label>Thought Process:</Label>
                    <div className="p-3 bg-muted rounded-md">
                      <p className="text-sm">{response.response.thought}</p>
                    </div>
                  </div>
                )}

                <div className="space-y-2">
                  <Label>Final Answer:</Label>
                  <div className="p-3 bg-muted rounded-md">
                    <p className="whitespace-pre-wrap">{response.response?.final_answer}</p>
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="data" className="space-y-4">
                {response.response?.data && (
                  <>
                    <div className="space-y-2">
                      <Label>Insights:</Label>
                      <div className="space-y-1">
                        {extractDataInsights(response.response.data.data || []).map((insight: string, index: number) => (
                          <Badge key={index} variant="secondary" className="mr-2">
                            {insight}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <Label>Raw Data:</Label>
                      <ScrollArea className="h-60 w-full rounded-md border p-4">
                        <pre className="text-xs">{JSON.stringify(response.response.data, null, 2)}</pre>
                      </ScrollArea>
                    </div>
                  </>
                )}
              </TabsContent>

              <TabsContent value="actions" className="space-y-4">
                {response.response?.actions_taken?.length > 0 && (
                  <div className="space-y-4">
                    {response.response.actions_taken.map((action: AgentAction, index: number) => (
                      <Card key={index} className="border-l-4 border-l-blue-500">
                        <CardHeader className="pb-2">
                          <div className="flex items-center justify-between">
                            <CardTitle className="text-sm">{action.tool_name}</CardTitle>
                            <Badge variant={action.success ? "default" : "destructive"}>
                              {action.success ? 'Thành công' : 'Thất bại'}
                            </Badge>
                          </div>
                        </CardHeader>
                        <CardContent className="pt-0">
                          <ScrollArea className="h-32 w-full">
                            <pre className="text-xs">{JSON.stringify(action, null, 2)}</pre>
                          </ScrollArea>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </TabsContent>

              <TabsContent value="visualization" className="space-y-4">
                {(() => {
                  // Find plotting agent result with image
                  const plottingAction = response.response?.actions_taken?.find((action: AgentAction) => 
                    action.tool_name === 'plotting_agent' && action.result?.data
                  )
                  
                  if (plottingAction?.result?.data) {
                    return (
                      <div className="space-y-4">
                        <Label>Generated Chart:</Label>
                        <div className="flex justify-center p-4 bg-muted rounded-md">
                          <img 
                            src={decodeBase64Image(plottingAction.result.data)}
                            alt="Generated visualization"
                            className="max-w-full h-auto rounded-md shadow-lg"
                          />
                        </div>
                        {plottingAction.result.chart_config && (
                          <div>
                            <Label>Chart Configuration:</Label>
                            <ScrollArea className="h-32 w-full rounded-md border p-4">
                              <pre className="text-xs">{JSON.stringify(plottingAction.result.chart_config, null, 2)}</pre>
                            </ScrollArea>
                          </div>
                        )}
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <strong>Chart Type:</strong> {plottingAction.result.plot_type || 'Unknown'}
                          </div>
                          <div>
                            <strong>Status:</strong> 
                            <Badge variant={plottingAction.success ? "default" : "destructive"} className="ml-2">
                              {plottingAction.success ? 'Success' : 'Failed'}
                            </Badge>
                          </div>
                        </div>
                      </div>
                    )
                  }
                  
                  return (
                    <div className="text-center text-muted-foreground py-8">
                      <p>Không có biểu đồ nào được tạo</p>
                      <p className="text-sm">Thử yêu cầu tạo biểu đồ trong query của bạn</p>
                      <div className="mt-4">
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => setQuery("Show me top 10 flight destinations and create a bar chart")}
                        >
                          Thử ví dụ visualization
                        </Button>
                      </div>
                    </div>
                  )
                })()}
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Ví dụ Queries</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => setQuery("Show me the top 10 flight destinations and create a bar chart")}
              >
                SQL + Visualization
              </Button>
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => setQuery("What is the checked baggage policy?")}
              >
                RAG Search
              </Button>
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => setQuery("Count total flights")}
              >
                Simple SQL
              </Button>
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => setQuery("Hello")}
              >
                Greeting Test
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}