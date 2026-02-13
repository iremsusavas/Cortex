"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { getResearch } from "@/lib/api";
import { useWebSocket } from "@/hooks/useWebSocket";
import type { ResearchSession, WSMessage } from "@/lib/types";
import { formatCost } from "@/lib/utils";

const AGENTS = ["Planner", "Researcher", "Analyst", "Writer", "Critic"];

export default function ResearchPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.id as string;
  const { messages, connected } = useWebSocket(sessionId);
  const [session, setSession] = useState<ResearchSession | null>(null);
  const [polling, setPolling] = useState(true);

  useEffect(() => {
    if (!sessionId) return;
    const fetchSession = async () => {
      try {
        const data = await getResearch(sessionId);
        setSession(data);
        if (data.phase === "complete" || data.phase === "failed") {
          setPolling(false);
        }
      } catch {
        setPolling(false);
      }
    };
    fetchSession();
    const interval = setInterval(fetchSession, 3000);
    return () => clearInterval(interval);
  }, [sessionId, polling]);

  const activeAgent = messages
    .filter((m) => m.type === "agent.thought" || m.type === "agent.action")
    .slice(-1)[0]?.data?.agent_name as string | undefined;

  return (
    <main className="min-h-screen flex flex-col">
      <header className="border-b border-white/10 px-6 py-4 flex items-center justify-between">
        <h1 className="text-xl font-semibold">Cortex Research</h1>
        <div className="flex items-center gap-4">
          <span
            className={`text-sm ${connected ? "text-green-500" : "text-zinc-500"}`}
          >
            {connected ? "● Live" : "○ Connecting..."}
          </span>
          <a href="/" className="text-sm text-violet-400 hover:underline">
            New Research
          </a>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* Left: Agent Status */}
        <aside className="w-80 border-r border-white/10 p-4 flex flex-col gap-4 overflow-y-auto">
          <h2 className="text-sm font-medium text-zinc-400">Agent Status</h2>
          {AGENTS.map((name) => (
            <div
              key={name}
              className={`p-3 rounded-xl border transition-all ${
                activeAgent === name
                  ? "border-violet-500/50 bg-violet-500/10"
                  : "border-white/10 bg-white/5"
              }`}
            >
              <div className="flex items-center gap-2">
                <span
                  className={`w-2 h-2 rounded-full ${
                    activeAgent === name ? "bg-violet-500 animate-pulse" : "bg-zinc-600"
                  }`}
                />
                <span className="font-medium">{name}</span>
              </div>
              <p className="text-xs text-zinc-500 mt-1">
                {activeAgent === name ? "Active..." : "Waiting"}
              </p>
            </div>
          ))}
          <div className="mt-auto pt-4 border-t border-white/10">
            <p className="text-sm text-zinc-400">
              Phase: <span className="text-zinc-200">{session?.phase || "-"}</span>
            </p>
            <p className="text-sm text-zinc-400 mt-1">
              Cost: {session ? formatCost(session.total_cost) : "-"}
            </p>
          </div>
        </aside>

        {/* Center: Activity Feed */}
        <section className="flex-1 flex flex-col overflow-hidden">
          <div className="p-4 border-b border-white/10">
            <h2 className="text-sm font-medium text-zinc-400">Live Activity</h2>
            <p className="text-sm text-zinc-500 mt-1 truncate">
              {session?.query}
            </p>
          </div>
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            <AnimatePresence>
              {messages.map((msg, i) => (
                <MessageItem key={i} msg={msg} />
              ))}
            </AnimatePresence>
            {session?.phase === "complete" && session.report && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-6"
              >
                <button
                  onClick={() => router.push(`/reports/${sessionId}`)}
                  className="px-6 py-3 rounded-xl bg-violet-600 hover:bg-violet-500 text-white font-medium"
                >
                  View Report →
                </button>
              </motion.div>
            )}
          </div>
        </section>

        {/* Right: Sources */}
        <aside className="w-80 border-l border-white/10 p-4 overflow-y-auto">
          <h2 className="text-sm font-medium text-zinc-400 mb-4">Sources Found</h2>
          <div className="space-y-3">
            {session?.sources?.slice(0, 10).map((s, i) => (
              <div
                key={i}
                className="p-3 rounded-xl bg-white/5 border border-white/10"
              >
                <div className="flex items-center gap-2">
                  <span
                    className={`text-xs ${
                      (s.credibility_score || 0) >= 8 ? "text-green-500" : "text-yellow-500"
                    }`}
                  >
                    {s.credibility_score || "-"}/10
                  </span>
                </div>
                <p className="text-sm font-medium mt-1 truncate">{s.title || "Untitled"}</p>
                <a
                  href={s.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-violet-400 hover:underline truncate block"
                >
                  {s.url}
                </a>
              </div>
            ))}
            {(!session?.sources || session.sources.length === 0) && (
              <p className="text-sm text-zinc-500">No sources yet</p>
            )}
          </div>
        </aside>
      </div>
    </main>
  );
}

function MessageItem({ msg }: { msg: WSMessage }) {
  const agentName = msg.data?.agent_name as string | undefined;
  const content =
    msg.data?.content ??
    msg.data?.finding ??
    (msg.data?.phase && `Phase: ${msg.data.phase}`) ??
    (msg.data?.sub_task && `Task: ${(msg.data.sub_task as { question?: string }).question}`) ??
    (Object.keys(msg.data || {}).length > 0 ? JSON.stringify(msg.data) : null);

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="p-3 rounded-xl bg-white/5 border border-white/10"
    >
      <div className="flex items-center gap-2">
        <span className="text-violet-400 font-medium">
          {agentName || msg.type}
        </span>
        <span className="text-xs text-zinc-500">{msg.type}</span>
      </div>
      <p className="text-sm text-zinc-300 mt-2 line-clamp-3">
        {content || "-"}
      </p>
    </motion.div>
  );
}
