"use client";

import { CopilotKit } from "@copilotkit/react-core";
import { CopilotChat } from "@copilotkit/react-ui";
import "@copilotkit/react-ui/styles.css";

export default function Home() {
  return (
    <CopilotKit runtimeUrl="/api/copilotkit">
      <main className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
        <div className="container mx-auto px-4 py-8">
          {/* Header */}
          <header className="text-center mb-8">
            <h1 className="text-4xl font-bold text-white mb-2">
              🔍 Web Research Agent
            </h1>
            <p className="text-purple-200">
              Autonomous AI research powered by AG-UI Protocol
            </p>
          </header>

          {/* Chat Interface */}
          <div className="max-w-4xl mx-auto">
            <div className="bg-white/10 backdrop-blur-lg rounded-2xl shadow-2xl overflow-hidden border border-white/20">
              <CopilotChat
                className="h-[600px]"
                labels={{
                  title: "Research Assistant",
                  initial: "Hello! I'm your research assistant. Ask me anything and I'll search the web to find accurate, up-to-date information.",
                  placeholder: "What would you like me to research?",
                }}
                instructions={`You are a web research agent. When users ask questions:
1. Use the research tool to search the web
2. Synthesize information from multiple sources
3. Provide accurate, well-structured responses with sources
4. Always cite your sources`}
              />
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
              icon="⚡"
              title="AG-UI Protocol"
              description="Seamless streaming with the AG-UI standard"
            />
          </div>
        </div>
      </main>
    </CopilotKit>
  );
}

function FeatureCard({ icon, title, description }: { icon: string; title: string; description: string }) {
  return (
    <div className="bg-white/5 backdrop-blur rounded-xl p-4 border border-white/10">
      <div className="text-3xl mb-2">{icon}</div>
      <h3 className="text-white font-semibold mb-1">{title}</h3>
      <p className="text-purple-200 text-sm">{description}</p>
    </div>
  );
}
