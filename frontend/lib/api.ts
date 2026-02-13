/** API client for Cortex backend */

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function createResearch(query: string, depth = 2, language = "en") {
  const res = await fetch(`${API_URL}/api/v1/research`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, depth, language }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getResearch(sessionId: string) {
  const res = await fetch(`${API_URL}/api/v1/research/${sessionId}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getReports() {
  const res = await fetch(`${API_URL}/api/v1/reports`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getReport(reportId: string) {
  const res = await fetch(`${API_URL}/api/v1/reports/${reportId}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export function getWebSocketUrl(sessionId: string): string {
  const base = (process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000").replace(
    /^http/,
    "ws"
  );
  return `${base}/api/v1/ws/research/${sessionId}`;
}
