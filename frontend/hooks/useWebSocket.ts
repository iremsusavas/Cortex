"use client";

import { useEffect, useRef, useState } from "react";
import { getWebSocketUrl } from "@/lib/api";
import type { WSMessage } from "@/lib/types";

export function useWebSocket(sessionId: string | null) {
  const [messages, setMessages] = useState<WSMessage[]>([]);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttempts = useRef(0);
  const maxReconnect = 10;

  useEffect(() => {
    if (!sessionId) return;

    const connect = () => {
      const url = getWebSocketUrl(sessionId);
      const ws = new WebSocket(url);

      ws.onopen = () => {
        setConnected(true);
        reconnectAttempts.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data) as WSMessage;
          if (msg.type !== "ping") {
            setMessages((prev) => [...prev, msg]);
          }
        } catch {
          // ignore parse errors
        }
      };

      ws.onclose = () => {
        setConnected(false);
        if (reconnectAttempts.current < maxReconnect) {
          reconnectAttempts.current += 1;
          setTimeout(connect, 5000);
        }
      };

      ws.onerror = () => {};

      wsRef.current = ws;
    };

    connect();
    return () => {
      wsRef.current?.close();
      wsRef.current = null;
    };
  }, [sessionId]);

  return { messages, connected };
}
