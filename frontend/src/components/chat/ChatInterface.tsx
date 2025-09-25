import React, { useState, useRef, useEffect } from 'react';
import { Button } from '~/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '~/components/ui/card';
import { Input } from '~/components/ui/input';
import { ScrollArea } from '~/components/ui/scroll-area';
import { Avatar } from '~/components/ui/avatar';
import { Badge } from '~/components/ui/badge';
import { Label } from '~/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '~/components/ui/tabs';
import { ChatMessage, AgentAction } from '~/lib/types';
import { formatDate, decodeBase64Image, extractDataInsights } from '~/lib/utils';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface MessageProps {
  message: ChatMessage;
}

const Message = ({ message }: MessageProps) => {
  const isUser = message.role === 'user';
  const hasResponse = message.response && !isUser;
  
  return (
    <div className={`flex gap-3 mb-6 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <Avatar className="h-8 w-8 flex-shrink-0">
          <div className="flex h-full w-full items-center justify-center bg-primary text-white text-sm font-medium">
            AI
          </div>
        </Avatar>
      )}
      
      <div className={`${isUser ? 'max-w-[80%]' : 'max-w-[85%] flex-1'} ${isUser ? 'bg-primary text-white px-4 py-3 rounded-lg' : ''}`}>
        {isUser ? (
          <div className="whitespace-pre-wrap">
            {message.content}
          </div>
        ) : hasResponse ? (
          <div className="space-y-4">
            {/* Final Answer lên trên */}
            <div className="p-4 bg-background border rounded-md">
              <p className="whitespace-pre-wrap text-sm leading-relaxed">
                {message.response?.response?.final_answer}
              </p>
            </div>

            <Card>
              <CardContent className="pt-6">
                <Tabs defaultValue="result" className="w-full">
                <TabsList className="grid w-full grid-cols-3">
                  <TabsTrigger value="result">Result</TabsTrigger>
                  <TabsTrigger value="actions">Actions</TabsTrigger>
                  <TabsTrigger value="data">Data</TabsTrigger>
                </TabsList>
                
                <TabsContent value="result" className="space-y-4">
                  <div className="space-y-2">
                                          {/* Render data preview */}
                      {(() => {
                        // Check for plotting data (base64 image)
                        const plottingAction = message.response?.response?.actions_taken?.find(
                          (action: AgentAction) => action.tool_name === 'plotting_agent' && action.result?.data
                        )
                        
                        if (plottingAction?.result?.data) {
                          return (
                            <div className="mt-4 pt-4 border-t">
                              <Label className="text-xs font-medium text-muted-foreground mb-2 block">Generated Visualization:</Label>
                              <div className="flex justify-center p-2 bg-muted/30 rounded-md">
                                <img 
                                  src={decodeBase64Image(plottingAction.result.data)}
                                  alt="Generated chart"
                                  className="max-w-full h-auto max-h-64 rounded border"
                                />
                              </div>
                            </div>
                          )
                        }
                        
                        // Check for SQL/RAG data
                        const dataAction = message.response?.response?.actions_taken?.find(
                          (action: AgentAction) => (action.tool_name === 'sql_agent' || action.tool_name === 'rag_agent') && action.result?.data
                        )
                        
                        if (dataAction?.result?.data) {
                          let dataToShow = dataAction.result.data
                          
                          // If data is array, take first 10 items
                          if (Array.isArray(dataToShow) && dataToShow.length > 10) {
                            dataToShow = dataToShow.slice(0, 10)
                          }
                          
                          return (
                            <div className="mt-4 pt-4 border-t">
                              <Label className="text-xs font-medium text-muted-foreground mb-2 block">
                                Data Preview {Array.isArray(dataAction.result.data) && dataAction.result.data.length > 10 && `(showing 10 of ${dataAction.result.data.length})`}:
                              </Label>
                              <ScrollArea className="h-32 w-full rounded border bg-muted/30">
                                <pre className="text-xs p-3 font-mono">
                                  {typeof dataToShow === 'string' ? dataToShow : JSON.stringify(dataToShow, null, 2)}
                                </pre>
                              </ScrollArea>
                            </div>
                          )
                        }
                        
                        return null
                      })()}
                  </div>
                </TabsContent>

                <TabsContent value="actions" className="space-y-4 mt-4">
                  {(() => {
                    // Filter actions that have content (args or result)
                    const actionsWithContent = message.response?.response?.actions_taken?.filter((action: AgentAction) => 
                      action.args || action.result
                    ) || []
                    
                    if (actionsWithContent.length === 0) {
                      return (
                        <div className="text-center text-muted-foreground py-4">
                          <p className="text-sm">No action</p>
                        </div>
                      )
                    }
                    
                    return (
                      <div className="space-y-3">
                        {actionsWithContent.map((action: AgentAction, index: number) => (
                          <Card key={index} className="border-l-4 border-l-blue-500">
                            <CardHeader className="pb-2">
                              <CardTitle className="text-xs">{action.tool_name}</CardTitle>
                            </CardHeader>
                            <CardContent className="pt-0 space-y-3">
                              {action.args && (
                                <div>
                                  <Label className="text-xs text-muted-foreground">Input:</Label>
                                  <ScrollArea className="h-20 w-full mt-1 overflow-x-auto">
                                    <pre className="text-xs p-2 bg-muted/50 rounded">
                                      {JSON.stringify(action.args, null, 2)}
                                    </pre>
                                  </ScrollArea>
                                </div>
                              )}
                              
                              {action.result && (
                                <div>
                                  <Label className="text-xs text-muted-foreground">Output:</Label>
                                  <ScrollArea className="h-20 w-full mt-1 overflow-x-auto">
                                    <pre className="text-xs p-2 bg-muted/50 rounded">
                                      {typeof action.result === 'string' 
                                        ? action.result 
                                        : JSON.stringify(action.result, null, 2)}
                                    </pre>
                                  </ScrollArea>
                                </div>
                              )}
                            </CardContent>
                          </Card>
                        ))}
                      </div>
                    )
                  })()}
                </TabsContent>

                <TabsContent value="data" className="space-y-4 mt-4">
                  {(() => {
                    // Find data from SQL/RAG/Plotting actions
                    const dataActions = message.response?.response?.actions_taken?.filter((action: AgentAction) => 
                      action.result?.data && (
                        action.tool_name === 'sql_agent' || 
                        action.tool_name === 'rag_agent' || 
                        action.tool_name === 'plotting_agent'
                      )
                    ) || []
                    
                    if (dataActions.length === 0) {
                      return (
                        <div className="text-center text-muted-foreground py-4">
                          <p className="text-sm">No data</p>
                        </div>
                      )
                    }
                    
                    return (
                      <div className="space-y-4">
                        {dataActions.map((action: AgentAction, index: number) => {
                          const data = action.result?.data
                          if (action.tool_name === 'plotting_agent' && typeof data === 'string') {
                            return (
                              <div key={index} className="space-y-2">
                                <Label className="text-xs font-medium">{action.tool_name} - Visualization:</Label>
                                <div className="flex justify-center p-2 bg-muted/30 rounded-md">
                                <img 
                                  src={decodeBase64Image(data)}
                                  alt="Generated chart"
                                  className="max-w-full h-auto rounded border"
                                />
                                </div>
                              </div>
                            )
                          }
                          
                          // Handle SQL/RAG data
                          let dataToShow = data

                          
                          return (
                            <div key={index} className="space-y-2">
                              <Label className="text-xs font-medium">
                                {action.tool_name} - Data {Array.isArray(data) && data.length > 10 && `(showing 10 of ${data.length})`}:
                              </Label>
                              
                              {Array.isArray(data) && (
                                <div className="space-y-2">
                                  <div className="space-y-1">
                                    {extractDataInsights(data).map((insight: string, idx: number) => (
                                      <Badge key={idx} variant="secondary" className="mr-2 text-xs">
                                        {insight}
                                      </Badge>
                                    ))}
                                  </div>
                                </div>
                              )}
                              
                              <ScrollArea className="h-60 w-full rounded-md border p-4">
                                <pre className="text-xs">
                                  {typeof dataToShow === 'string' 
                                    ? dataToShow 
                                    : JSON.stringify(dataToShow, null, 2)}
                                </pre>
                              </ScrollArea>
                            </div>
                          )
                        })}
                      </div>
                    )
                  })()}
                </TabsContent>
              </Tabs>
            </CardContent>

          </Card>
          </div>
        ) : (
          // Hiển thị tin nhắn AI đơn giản không có response data
          <div className="bg-muted p-4 rounded-lg">
            <div className="markdown-content prose prose-sm dark:prose-invert max-w-none">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {message.content}
              </ReactMarkdown>
            </div>
          </div>
        )}
        
        <div className="text-xs opacity-70 mt-2">
          {formatDate(message.timestamp)}
        </div>
      </div>
      
      {isUser && (
        <Avatar className="h-8 w-8">
          <div className="flex h-full w-full items-center justify-center bg-secondary text-white text-sm font-medium">
            U
          </div>
        </Avatar>
      )}
    </div>
  );
};

interface ChatMessagesProps {
  messages: ChatMessage[];
  isLoading?: boolean;
}

export const ChatMessages = ({ messages, isLoading }: ChatMessagesProps) => {
  const bottomRef = useRef<HTMLDivElement>(null);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom when messages change or loading state changes
  useEffect(() => {
    // Use setTimeout to ensure DOM has updated
    setTimeout(() => {
      bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  }, [messages, isLoading]);

  return (
    <ScrollArea className="flex-1 px-6 h-full" ref={scrollAreaRef}>
      <div className="py-6 max-w-4xl mx-auto">
        {messages && messages.length > 0 ? (
          <>
            {messages.map((message, index) => (
              <Message key={index} message={message} />
            ))}
            {isLoading && (
              <div className="flex items-start gap-3 mb-6">
                <Avatar className="h-8 w-8 flex-shrink-0">
                  <div className="flex h-full w-full items-center justify-center bg-primary text-white text-sm font-medium">
                    AI
                  </div>
                </Avatar>
                <div className="bg-muted p-4 rounded-lg max-w-[80%] flex items-center space-x-2">
                  <div className="w-2 h-2 rounded-full bg-current animate-bounce [animation-delay:-0.3s]"></div>
                  <div className="w-2 h-2 rounded-full bg-current animate-bounce [animation-delay:-0.15s]"></div>
                  <div className="w-2 h-2 rounded-full bg-current animate-bounce"></div>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </>
        ) : (
          <div className="flex h-full min-h-[60vh] items-center justify-center text-center text-muted-foreground">
            <div className="max-w-md">
              <div className="mb-4">
                <svg 
                  className="h-12 w-12 mx-auto text-muted-foreground/50" 
                  fill="none" 
                  viewBox="0 0 24 24" 
                  stroke="currentColor"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium mb-2">Start a conversation</h3>
              <p className="text-sm">
                Ask about SQL queries, search documents, or create charts from data
              </p>
              <div className="mt-4 space-y-2">
                <div className="text-xs text-muted-foreground/75">Examples:</div>
                <div className="text-xs bg-muted px-3 py-2 rounded-md">
                  "Show me top 10 flight destinations and create a bar chart"
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </ScrollArea>
  );
};

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
}

export const ChatInput = ({ onSendMessage, isLoading }: ChatInputProps) => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !isLoading) {
      onSendMessage(message.trim());
      setMessage('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleSubmit(e as any);
    }
  };

  return (
    <div className="border-t bg-background p-4">
      <div className="max-w-4xl mx-auto">
        <form onSubmit={handleSubmit} className="flex gap-3">
          <Input
            placeholder="Nhập câu hỏi của bạn... (Ctrl+Enter để gửi)"
            value={message}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
            className="flex-1 min-h-[44px]"
          />
          <Button 
            type="submit" 
            disabled={isLoading || !message.trim()} 
            className="min-w-[100px] h-[44px]"
          >
            {isLoading ? (
              <span className="flex items-center gap-2">
                <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Đang gửi...
              </span>
            ) : (
              <span className="flex items-center gap-2">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="22" y1="2" x2="11" y2="13"/>
                  <polygon points="22,2 15,22 11,13 2,9 22,2"/>
                </svg>
                Gửi
              </span>
            )}
          </Button>
        </form>
        <p className="text-xs text-muted-foreground mt-2 text-center">
          • Support SQL queries, Document search, and visualization
        </p>
      </div>
    </div>
  );
};

interface ChatInterfaceProps {
  messages: ChatMessage[];
  onSendMessage: (message: string) => void;
  isLoading: boolean;
}

export default function ChatInterface({ messages, onSendMessage, isLoading }: ChatInterfaceProps) {
  return (
    <div className="flex flex-col h-full overflow-hidden">
      <ChatMessages messages={messages} isLoading={isLoading} />
      <ChatInput onSendMessage={onSendMessage} isLoading={isLoading} />
    </div>
  );
}