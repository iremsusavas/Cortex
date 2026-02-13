"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { createResearch } from "@/lib/api";

const SUGGESTIONS = [
  "Impact of AI on healthcare in 2024",
  "Quantum computing breakthroughs 2024",
  "Climate change mitigation strategies",
  "Future of remote work",
  "Renewable energy trends",
];

export default function Home() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || loading) return;
    setLoading(true);
    try {
      const { session_id } = await createResearch(query.trim());
      router.push(`/research/${session_id}`);
    } catch (err) {
      console.error(err);
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-8 relative overflow-hidden">
      {/* Background gradient mesh */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(139,92,246,0.15),transparent)]" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_60%_60%_at_80%_50%,rgba(34,211,238,0.08),transparent)]" />

      <motion.div
        className="relative z-10 max-w-2xl w-full"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <motion.h1
          className="text-5xl font-bold text-center mb-2 bg-gradient-to-r from-violet-400 to-cyan-400 bg-clip-text text-transparent"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          Cortex
        </motion.h1>
        <motion.p
          className="text-zinc-400 text-center mb-12 text-lg"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          Multi-Agent Research Intelligence
        </motion.p>

        <motion.form
          onSubmit={handleSubmit}
          className="space-y-6"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          <div className="relative">
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter your research question..."
              className="w-full h-32 px-6 py-4 rounded-xl bg-zinc-900/80 border border-white/10 focus:border-violet-500/50 focus:ring-2 focus:ring-violet-500/20 outline-none transition-all resize-none text-zinc-100 placeholder-zinc-500"
              disabled={loading}
            />
            <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-violet-500/20 to-cyan-500/20 -z-10 blur-xl opacity-0 focus-within:opacity-100 transition-opacity pointer-events-none" />
          </div>

          <div className="flex justify-center">
            <motion.button
              type="submit"
              disabled={!query.trim() || loading}
              className="px-8 py-3 rounded-xl bg-gradient-to-r from-violet-600 to-cyan-600 text-white font-semibold disabled:opacity-50 disabled:cursor-not-allowed hover:scale-105 hover:shadow-lg hover:shadow-violet-500/25 transition-all"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              {loading ? "Starting..." : "Start Research"}
            </motion.button>
          </div>
        </motion.form>

        <motion.div
          className="mt-8 flex flex-wrap gap-2 justify-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          {SUGGESTIONS.map((s, i) => (
            <motion.button
              key={s}
              type="button"
              onClick={() => setQuery(s)}
              className="px-4 py-2 rounded-lg bg-white/5 border border-white/10 hover:border-violet-500/30 hover:bg-violet-500/10 text-sm text-zinc-400 hover:text-zinc-200 transition-colors"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 + i * 0.05 }}
            >
              {s}
            </motion.button>
          ))}
        </motion.div>

        <div className="mt-12 flex justify-center gap-6">
          <a href="/reports" className="text-sm text-zinc-500 hover:text-violet-400 transition-colors">
            View Reports
          </a>
          <a href="/dashboard" className="text-sm text-zinc-500 hover:text-violet-400 transition-colors">
            Dashboard
          </a>
        </div>
        <p className="mt-6 text-center text-xs text-zinc-600">
          Powered by 5 AI Agents
        </p>
      </motion.div>
    </main>
  );
}
