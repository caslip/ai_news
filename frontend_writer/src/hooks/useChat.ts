"use client";

import { useState, useCallback, useRef } from "react";
import {
  createChatSession,
  deleteChatSession,
  getChatHistory,
  listChatSessions,
  chatStream,
  chatToGenerate,
  type ChatMessage,
  type ChatSession,
} from "@/lib/api";

export interface UseChatOptions {
  sessionId?: string;
}

export interface ChatStreamOptions {
  sessionId: string;
  message: string;
  model?: string;
  context_type?: "article" | "twitter" | "xiaohongshu" | null;
  source_content?: string | null;
  onChunk: (content: string) => void;
  onDone: (sessionId: string) => void;
  onError: (error: string) => void;
}

export interface SendMessageOptions {
  model?: string;
  context_type?: "article" | "twitter" | "xiaohongshu" | null;
  source_content?: string | null;
}

export function useChat(options: UseChatOptions = {}) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState(options.sessionId || "");
  const streamingContent = useRef("");

  const startNewSession = useCallback(async () => {
    const { session_id } = await createChatSession();
    setCurrentSessionId(session_id);
    setMessages([]);
    return session_id;
  }, []);

  const loadHistory = useCallback(async (sessionId: string) => {
    const { messages: history } = await getChatHistory(sessionId);
    setMessages(history);
    setCurrentSessionId(sessionId);
  }, []);

  const loadSessions = useCallback(async () => {
    try {
      const { sessions } = await listChatSessions();
      setSessions(sessions);
    } catch {
      // Silently fail if API not available
      setSessions([]);
    }
  }, []);

  const deleteSession = useCallback(async (sessionId: string) => {
    try {
      await deleteChatSession(sessionId);
    } catch {
      // Silently fail if API not available
    }
    setSessions((prev) => prev.filter((s) => s.session_id !== sessionId));
    if (currentSessionId === sessionId) {
      setMessages([]);
      setCurrentSessionId("");
    }
  }, [currentSessionId]);

  const sendMessage = useCallback(async (
    content: string,
    options?: SendMessageOptions
  ) => {
    if (!content.trim()) return;

    let sessionId = currentSessionId;
    if (!sessionId) {
      sessionId = await startNewSession();
    }

    setMessages((prev) => [...prev, { role: "user", content }]);
    setIsLoading(true);
    streamingContent.current = "";

    return new Promise<void>((resolve, reject) => {
      chatStream({
        sessionId,
        message: content,
        model: options?.model,
        context_type: options?.context_type,
        source_content: options?.source_content,
        onChunk: (chunk) => {
          streamingContent.current += chunk;
          setMessages((prev) => {
            const last = prev[prev.length - 1];
            if (last?.role === "assistant") {
              return [
                ...prev.slice(0, -1),
                { ...last, content: streamingContent.current },
              ];
            }
            return [...prev, { role: "assistant", content: chunk }];
          });
        },
        onDone: (finalSessionId) => {
          setIsLoading(false);
          setCurrentSessionId(finalSessionId);
          resolve();
        },
        onError: (error) => {
          setIsLoading(false);
          setMessages((prev) => [
            ...prev,
            { role: "assistant", content: `错误: ${error}` },
          ]);
          reject(new Error(error));
        },
      });
    });
  }, [currentSessionId, startNewSession]);

  const generateFromChat = useCallback(async (options?: { model?: string; context_type?: "article" | "twitter" | "xiaohongshu" | null }) => {
    return await chatToGenerate({
      session_id: currentSessionId,
      message: "请基于以上对话生成一篇完整的文章",
      model: options?.model,
      context_type: options?.context_type,
    });
  }, [currentSessionId]);

  return {
    messages,
    sessions,
    isLoading,
    currentSessionId,
    sendMessage,
    startNewSession,
    loadHistory,
    loadSessions,
    deleteSession,
    generateFromChat,
  };
}
