"use client";

import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setIsLoading(true);

    try {
      const response = await fetch("/api/research", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: userMessage }),
      });

      const data = await response.json();

      if (data.success && data.report) {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: data.report },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: data.error || "Sorry, I encountered an error while researching. Please try again.",
          },
        ]);
      }
    } catch (error) {
      console.error("Research error:", error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, I couldn't connect to the research service. Please try again.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            🔍 Web Research Agent
          </h1>
          <p className="text-purple-200">
            Autonomous AI research powered by LangGraph
          </p>
        </header>

        {/* Chat Interface */}
        <div className="max-w-4xl mx-auto">
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl shadow-2xl overflow-hidden border border-white/20">
            {/* Messages */}
            <div className="h-[500px] overflow-y-auto p-6 space-y-4">
              {messages.length === 0 && (
                <div className="text-center text-purple-200 mt-20">
                  <p className="text-lg mb-2">👋 Hello! I&apos;m your research assistant.</p>
                  <p className="text-sm opacity-75">
                    Ask me anything and I&apos;ll search the web to find accurate, up-to-date information.
                  </p>
                </div>
              )}
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                      message.role === "user"
                        ? "bg-purple-600 text-white"
                        : "bg-white/10 text-white"
                    }`}
                  >
                    {message.role === "assistant" ? (
                      <div className="prose prose-invert prose-sm max-w-none">
                        <ReactMarkdown>{message.content}</ReactMarkdown>
                      </div>
                    ) : (
                      <p>{message.content}</p>
                    )}
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-white/10 rounded-2xl px-4 py-3 text-white">
                    <div className="flex items-center space-x-2">
                      <div className="animate-pulse">🔍</div>
                      <span>Researching...</span>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <form onSubmit={handleSubmit} className="p-4 border-t border-white/10">
              <div className="flex space-x-4">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="What would you like me to research?"
                  className="flex-1 bg-white/10 text-white placeholder-purple-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500"
                  disabled={isLoading}
                />
                <button
                  type="submit"
                  disabled={isLoading || !input.trim()}
                  className="bg-purple-600 hover:bg-purple-700 disabled:bg-purple-800 disabled:cursor-not-allowed text-white px-6 py-3 rounded-xl font-medium transition-colors"
                >
                  {isLoading ? "..." : "Send"}
                </button>
              </div>
            </form>
          </div>
        </div>

        {/* Features */}
        <div className="max-w-4xl mx-auto mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
          <FeatureCard
            icon="🌐"
            title="Web Search"
            description="Real-time search using Tavily, SerpAPI, and DuckDuckGo"
          />
          <FeatureCard
            icon="📊"
            title="Structured Reports"
            description="Get organized findings with sources and analysis"
          />
          <FeatureCard
            icon="🤖"
            title="LangGraph Agent"
            description="Powered by LangChain's ReAct agent pattern"
          />
        </div>
      </div>
    </main>
  );
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: string;
  title: string;
  description: string;
}) {
  return (
    <div className="bg-white/5 backdrop-blur rounded-xl p-4 border border-white/10">
      <div className="text-3xl mb-2">{icon}</div>
      <h3 className="text-white font-semibold mb-1">{title}</h3>
      <p className="text-purple-200 text-sm">{description}</p>
    </div>
  );
}
