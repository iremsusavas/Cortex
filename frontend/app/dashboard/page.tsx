"use client";

import { useEffect, useState } from "react";
import { getResearch } from "@/lib/api";

export default function DashboardPage() {
  const [sessions, setSessions] = useState<unknown[]>([]);

  useEffect(() => {
    fetch(
      `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/research`
    )
      .then((r) => r.json())
      .then((d) => setSessions(d.sessions || []));
  }, []);

  const totalCost = sessions.reduce(
    (acc: number, s: { total_cost?: number }) => acc + (s.total_cost || 0),
    0
  );

  return (
    <main className="min-h-screen p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold">Analytics Dashboard</h1>
        <p className="text-zinc-400 mt-1">Research metrics and costs</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="p-6 rounded-xl bg-white/5 border border-white/10">
          <p className="text-zinc-500 text-sm">Total Research</p>
          <p className="text-3xl font-bold mt-1">{sessions.length}</p>
        </div>
        <div className="p-6 rounded-xl bg-white/5 border border-white/10">
          <p className="text-zinc-500 text-sm">Total Cost</p>
          <p className="text-3xl font-bold mt-1">${totalCost.toFixed(4)}</p>
        </div>
        <div className="p-6 rounded-xl bg-white/5 border border-white/10">
          <p className="text-zinc-500 text-sm">Avg per Research</p>
          <p className="text-3xl font-bold mt-1">
            ${sessions.length ? (totalCost / sessions.length).toFixed(4) : "0"}
          </p>
        </div>
      </div>

      <a href="/" className="text-violet-400 hover:underline">
        ← New Research
      </a>
    </main>
  );
}
