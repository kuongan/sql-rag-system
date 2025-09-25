import ChatTest from "~/components/chat-test";

export default function Home() {
  return (
    <div className="min-h-screen p-8">
      <div className="max-w-6xl mx-auto">
        <header className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-2">SQL RAG System</h1>
          <p className="text-muted-foreground">
            Multi-Agent System for SQL queries, RAG search, and data visualization
          </p>
        </header>
        <main>
          <ChatTest />
        </main>
      </div>
    </div>
  );
}
