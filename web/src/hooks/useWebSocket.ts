import { useState, useEffect, useRef } from 'react';

export function useWebSocket(url: string) {
  const [messages, setMessages] = useState<any[]>([]);
  const [status, setStatus] = useState<'connecting' | 'connected' | 'disconnected'>('connecting');
  const ws = useRef<WebSocket | null>(null);
  const reconnectTimeout = useRef<number | null>(null);
  const reconnectAttempts = useRef(0);

  useEffect(() => {
    function connect() {
      setStatus('connecting');
      ws.current = new WebSocket(url);

      ws.current.onopen = () => {
        setStatus('connected');
        reconnectAttempts.current = 0;
      };

      ws.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setMessages(prev => [...prev, data]);
        } catch (e) {
          console.error("WS parse error", e);
        }
      };

      ws.current.onclose = () => {
        setStatus('disconnected');
        const timeout = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000);
        reconnectAttempts.current += 1;
        reconnectTimeout.current = window.setTimeout(connect, timeout);
      };
      
      ws.current.onerror = () => {
        ws.current?.close();
      };
    }

    connect();

    return () => {
      if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current);
      ws.current?.close();
    };
  }, [url]);

  return { messages, status, ws: ws.current };
}
