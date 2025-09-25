import { Button } from '~/components/ui/button';
import { ScrollArea } from '~/components/ui/scroll-area';
import { Conversation, Agent, SystemStatus } from '~/lib/types';
import { cn } from '~/lib/utils';
import { formatDate } from '~/lib/utils';
import { useEffect, useState } from 'react';

interface SidebarProps {
  conversations: Record<string, Conversation>;
  currentConversationId: string | null;
  onSelectConversation: (id: string) => void;
  onNewConversation: () => void;
  selectedAgent: Agent;
  onSelectAgent: (agent: Agent) => void;
  systemStatus?: SystemStatus | null;
}

export default function Sidebar({
  conversations,
  currentConversationId,
  onSelectConversation,
  onNewConversation,
  selectedAgent,
  onSelectAgent,
  systemStatus,
}: SidebarProps) {
  // State để đảm bảo client-side rendering
  const [isClient, setIsClient] = useState(false);
  
  // Đánh dấu là đã render ở client
  useEffect(() => {
    setIsClient(true);
  }, []);
  
  // Group conversations by date - using consistent date format to avoid hydration errors
  const conversationsByDate: Record<string, Conversation[]> = {};
  
  // Sắp xếp tất cả các cuộc hội thoại theo thời gian mới nhất (giảm dần)
  const sortedConversations = Object.values(conversations).sort(
    (a, b) => new Date(b.lastUpdated).getTime() - new Date(a.lastUpdated).getTime()
  );
  
  // Nhóm các cuộc hội thoại đã sắp xếp theo ngày
  sortedConversations.forEach((conversation) => {
    // Use ISO date format to avoid locale differences between server and client
    const date = new Date(conversation.lastUpdated).toISOString().split('T')[0];
    if (!conversationsByDate[date]) {
      conversationsByDate[date] = [];
    }
    conversationsByDate[date].push(conversation);
  });
  
  // Sort dates in descending order (newest first)
  const sortedDates = Object.keys(conversationsByDate).sort(
    (a, b) => new Date(b).getTime() - new Date(a).getTime()
  );

  return (
    <div className="w-64 border-r border-border h-screen flex flex-col bg-card text-card-foreground fixed left-0 top-0 z-10">
      <div className="p-4 border-b border-border">
        <Button
          onClick={onNewConversation}
          variant="secondary"
          className="w-full justify-start"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="mr-2"
          >
            <path d="M12 5v14" />
            <path d="M5 12h14" />
          </svg>
          New Chat
        </Button>
      </div>

      <ScrollArea className="flex-1 h-[calc(100vh-120px)]">
        <div className="p-4">
          <h3 className="mb-2 text-sm font-medium">Conversations</h3>
          
          {/* Chỉ hiển thị khi đã render ở client để tránh lỗi hydration */}
          {isClient ? (
            sortedDates.length > 0 ? (
              sortedDates.map((date) => (
                <div key={date} className="mb-4">
                  <h4 className="text-xs text-muted-foreground mb-2">
                    {date.split('-').reverse().join('/')}
                  </h4>
                  
                  <div className="space-y-1">
                    {conversationsByDate[date].map((conversation, index) => (
                      <Button
                        key={`${date}-${conversation.id || index}`}
                        variant="ghost"
                        className={cn(
                          "w-full justify-start text-left font-normal",
                          currentConversationId === conversation.id && "bg-accent text-accent-foreground"
                        )}
                        onClick={() => onSelectConversation(conversation.id)}
                      >
                        <div className="truncate">{conversation.title}</div>
                      </Button>
                    ))}
                  </div>
                </div>
              ))
            ) : (
              <div className="text-sm text-muted-foreground mb-4">No conversations yet</div>
            )
          ) : (
            <div className="text-sm text-muted-foreground mb-4">Loading conversations...</div>
          )}
        </div>
      </ScrollArea>

      <div className="p-3 border-t border-border">
        <div className="flex justify-between items-center">
          <Button variant="ghost" size="sm" className="w-1/2 justify-start px-2 text-xs">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-1">
              <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"></path>
              <circle cx="12" cy="12" r="3"></circle>
            </svg>
            Settings
          </Button>
          <Button variant="ghost" size="sm" className="w-1/2 justify-start px-2 text-xs">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-1">
              <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"></path>
              <circle cx="12" cy="7" r="4"></circle>
            </svg>
            Login
          </Button>
        </div>
      </div>
    </div>
  );
}