"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getReports } from "@/lib/api";
import type { ResearchSession } from "@/lib/types";
import { formatCost } from "@/lib/utils";

export default function ReportsPage() {
  const [reports, setReports] = useState<ResearchSession[]>([]);
  const router = useRouter();

  useEffect(() => {
    getReports().then((r) => setReports(r.reports || []));
  }, []);

  return (
    <main className="min-h-screen p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold">Reports</h1>
        <p className="text-zinc-400 mt-1">Your completed research reports</p>
      </header>

      <div className="grid gap-4">
        {reports.map((r) => (
          <div
            key={r.id}
            onClick={() => router.push(`/reports/${r.id}`)}
            className="p-6 rounded-xl bg-white/5 border border-white/10 hover:border-violet-500/30 cursor-pointer transition-colors"
          >
            <p className="font-medium truncate">{r.query}</p>
            <div className="flex gap-4 mt-2 text-sm text-zinc-500">
              <span>{formatCost(r.total_cost)}</span>
              <span>{r.sources?.length || 0} sources</span>
            </div>
          </div>
        ))}
        {reports.length === 0 && (
          <p className="text-zinc-500">No reports yet. Start a research to get started.</p>
        )}
      </div>

      <a href="/" className="inline-block mt-8 text-violet-400 hover:underline">
        ← New Research
      </a>
    </main>
  );
}
