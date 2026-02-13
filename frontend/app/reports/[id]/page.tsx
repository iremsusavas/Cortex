"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import ReactMarkdown from "react-markdown";
import { getReport } from "@/lib/api";
import type { ResearchSession } from "@/lib/types";
import { formatCost } from "@/lib/utils";

export default function ReportPage() {
  const params = useParams();
  const id = params.id as string;
  const [report, setReport] = useState<ResearchSession | null>(null);

  useEffect(() => {
    getReport(id).then(setReport);
  }, [id]);

  if (!report) {
    return (
      <main className="min-h-screen p-8">
        <p className="text-zinc-500">Loading...</p>
      </main>
    );
  }

  const score = report.evaluation?.overall_score as number | undefined;

  return (
    <main className="min-h-screen p-8 max-w-4xl mx-auto">
      <header className="mb-8">
        <a href="/reports" className="text-sm text-violet-400 hover:underline mb-4 inline-block">
          ← Reports
        </a>
        <h1 className="text-2xl font-bold">{report.query}</h1>
        <div className="flex gap-6 mt-4 text-sm text-zinc-500">
          <span>{formatCost(report.total_cost)}</span>
          <span>{report.sources?.length || 0} sources</span>
          {score !== undefined && (
            <span className="text-violet-400">Quality: {score}/100</span>
          )}
        </div>
      </header>

      <article className="prose prose-invert prose-zinc max-w-none">
        <ReactMarkdown>{report.report || "*No content*"}</ReactMarkdown>
      </article>
    </main>
  );
}
