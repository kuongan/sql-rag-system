'use client'

import { useState } from 'react'
import { Button } from '~/components/ui/button'
import { Textarea } from '~/components/ui/textarea'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '~/components/ui/card'
import { Label } from '~/components/ui/label'
import { Badge } from '~/components/ui/badge'

interface BackendResponse {
  success: boolean
  final_answer: string
  thought?: string
  data?: any
  actions_taken: any[]
  agents_used: string[]
  conversation_id: string
  user_id: string
}

export default function ChatTest() {
  const [query, setQuery] = useState('')
  const [response, setResponse] = useState<BackendResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async () => {
    if (!query.trim()) return

    setLoading(true)
    setError(null)
    setResponse(null)

    try {
      // Test với orchestrator agent endpoint
      const res = await fetch('http://localhost:8000/api/agents/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query,
          conversation_id: 'test_frontend',
          user_id: 'frontend_user'
        }),
      })

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`)
      }

      const data: BackendResponse = await res.json()
      setResponse(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred')
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
          <CardTitle>SQL RAG System - Backend Test</CardTitle>
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
            {response.agents_used?.length > 0 && (
              <div className="flex gap-2">
                <span className="text-sm text-muted-foreground">Agents đã sử dụng:</span>
                {response.agents_used.map((agent, index) => (
                  <Badge key={index} variant="outline">
                    {agent}
                  </Badge>
                ))}
              </div>
            )}
          </CardHeader>
          <CardContent className="space-y-4">
            {response.thought && (
              <div className="space-y-2">
                <Label>Thought Process:</Label>
                <div className="p-3 bg-muted rounded-md">
                  <p className="text-sm">{response.thought}</p>
                </div>
              </div>
            )}

            <div className="space-y-2">
              <Label>Final Answer:</Label>
              <div className="p-3 bg-muted rounded-md">
                <p className="whitespace-pre-wrap">{response.final_answer}</p>
              </div>
            </div>

            {response.data && (
              <div className="space-y-2">
                <Label>Data:</Label>
                <div className="p-3 bg-muted rounded-md max-h-60 overflow-auto">
                  <pre className="text-xs">{JSON.stringify(response.data, null, 2)}</pre>
                </div>
              </div>
            )}

            {response.actions_taken?.length > 0 && (
              <div className="space-y-2">
                <Label>Actions Taken:</Label>
                <div className="p-3 bg-muted rounded-md max-h-40 overflow-auto">
                  <pre className="text-xs">{JSON.stringify(response.actions_taken, null, 2)}</pre>
                </div>
              </div>
            )}
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