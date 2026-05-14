"use client";

import { useState, useRef, useEffect } from "react";
import { useChat } from "@/hooks/useChat";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import {
  MessageSquare,
  X,
  Send,
  Plus,
  Sparkles,
  ChevronDown,
  ChevronUp,
  FilePen,
  Loader2,
  Settings2,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { toast } from "sonner";

const MODEL_OPTIONS = [
  { value: "deepseek/deepseek-chat-v3-5:free", label: "DeepSeek", badge: "Free" },
  { value: "anthropic/claude-3.5-sonnet", label: "Claude", badge: "Pro" },
  { value: "openai/gpt-4o", label: "GPT-4o", badge: "Pro" },
];

const SUGGESTIONS = [
  "帮我分析最近AI领域有什么新趋势",
  "如何写一篇吸引人的技术文章",
  "帮我把这段话改得更专业",
];

export default function FloatingChat() {
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState("");
  const [selectedModel, setSelectedModel] = useState(MODEL_OPTIONS[0].value);
  const [isMinimized, setIsMinimized] = useState(false);
  const [writingMode, setWritingMode] = useState(false);
  const [contextType, setContextType] = useState<"article" | "twitter" | "xiaohongshu">("article");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const {
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
  } = useChat();

  useEffect(() => {
    if (isOpen) {
      void loadSessions();
    }
  }, [isOpen, loadSessions]);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollTop = messagesEndRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;
    const text = input;
    setInput("");
    try {
      await sendMessage(text, {
        model: selectedModel,
        context_type: writingMode ? contextType : undefined,
      });
    } catch {
      // error handled in hook
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      void handleSend();
    }
  };

  const handleGenerate = async () => {
    if (!currentSessionId) {
      toast.error("请先对话后再生成文章");
      return;
    }
    try {
      const result = await generateFromChat({
        model: selectedModel,
        context_type: writingMode ? contextType : undefined,
      });
      toast.success("文章已生成，正在跳转...");
      window.location.href = `/drafts?id=${result.id}`;
    } catch {
      toast.error("生成失败，请重试");
    }
  };

  const handleNewChat = async () => {
    await startNewSession();
    setIsMinimized(false);
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInput(suggestion);
    inputRef.current?.focus();
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end gap-3">
      {isOpen && (
        <div
          className={cn(
            "w-[420px] bg-background border rounded-2xl shadow-2xl flex flex-col overflow-hidden transition-all duration-300",
            isMinimized ? "h-12" : "h-[600px]"
          )}
        >
          <div className="flex items-center justify-between px-4 py-3 border-b bg-gradient-to-r from-primary/10 to-primary/5">
            <div className="flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-primary" />
              <span className="font-semibold text-sm">AI 写作助手</span>
              {currentSessionId && (
                <Badge variant="secondary" className="text-xs">
                  {messages.length} 条消息
                </Badge>
              )}
            </div>
            <div className="flex items-center gap-1">
              <Button
                variant="ghost"
                size="icon-sm"
                onClick={() => setIsMinimized(!isMinimized)}
              >
                {isMinimized ? (
                  <ChevronUp className="h-4 w-4" />
                ) : (
                  <ChevronDown className="h-4 w-4" />
                )}
              </Button>
              <Button
                variant="ghost"
                size="icon-sm"
                onClick={() => setIsOpen(false)}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {!isMinimized && (
            <>
              <div className="px-4 py-2 border-b flex flex-col gap-2">
                <div className="flex items-center gap-2">
                  <Settings2 className="h-3 w-3 text-muted-foreground" />
                  <div className="flex gap-1 flex-wrap">
                    {MODEL_OPTIONS.map((m) => (
                      <Badge
                        key={m.value}
                        variant={selectedModel === m.value ? "default" : "outline"}
                        className="text-xs cursor-pointer"
                        onClick={() => setSelectedModel(m.value)}
                      >
                        {m.label}
                        {m.badge && (
                          <span className="ml-1 opacity-60">{m.badge}</span>
                        )}
                      </Badge>
                    ))}
                  </div>
                </div>
                <div className="flex items-center gap-2 pl-5">
                  <div className="flex items-center gap-2">
                    <Switch
                      id="writing-mode"
                      checked={writingMode}
                      onCheckedChange={setWritingMode}
                      className="scale-90"
                    />
                    <Label htmlFor="writing-mode" className="text-xs cursor-pointer text-muted-foreground">
                      写作模式
                    </Label>
                  </div>
                  {writingMode && (
                    <Select value={contextType} onValueChange={(v) => setContextType(v as typeof contextType)}>
                      <SelectTrigger className="h-6 text-xs w-auto">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="article">文章写作</SelectItem>
                        <SelectItem value="twitter">推文撰写</SelectItem>
                        <SelectItem value="xiaohongshu">小红书笔记</SelectItem>
                      </SelectContent>
                    </Select>
                  )}
                </div>
              </div>

              {sessions.length > 0 && (
                <div className="px-4 py-2 border-b flex gap-2 overflow-x-auto">
                  <Button
                    variant="outline"
                    size="sm"
                    className="text-xs flex-shrink-0"
                    onClick={handleNewChat}
                  >
                    <Plus className="h-3 w-3 mr-1" />
                    新对话
                  </Button>
                  {sessions.slice(0, 3).map((s) => (
                    <Badge
                      key={s.session_id}
                      variant={currentSessionId === s.session_id ? "default" : "outline"}
                      className="text-xs cursor-pointer flex-shrink-0 max-w-[120px] truncate"
                      onClick={() => void loadHistory(s.session_id)}
                    >
                      {s.title}
                    </Badge>
                  ))}
                </div>
              )}

              <ScrollArea className="flex-1 px-4 py-3">
                <div ref={messagesEndRef} className="space-y-4">
                  {messages.length === 0 && (
                    <div className="flex flex-col items-center justify-center h-full text-center py-8">
                      <Sparkles className="h-10 w-10 text-primary/30 mb-3" />
                      <p className="text-sm text-muted-foreground">
                        问我任何关于写作的问题
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">
                        我可以帮你分析素材、构思文章、改进文案
                      </p>
                      <div className="flex gap-2 mt-4 flex-wrap justify-center">
                        {SUGGESTIONS.map((suggestion) => (
                          <button
                            key={suggestion}
                            className="text-xs text-left px-3 py-1.5 rounded-full bg-primary/10 hover:bg-primary/20 text-primary transition-colors"
                            onClick={() => handleSuggestionClick(suggestion)}
                          >
                            {suggestion}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}

                  {messages.map((msg, i) => (
                    <div
                      key={i}
                      className={cn(
                        "flex gap-2",
                        msg.role === "user" && "flex-row-reverse"
                      )}
                    >
                      <Avatar className="h-7 w-7 flex-shrink-0 mt-1">
                        <AvatarFallback className="text-xs">
                          {msg.role === "user"
                            ? "ME"
                            : msg.role === "assistant"
                            ? "AI"
                            : "SYS"}
                        </AvatarFallback>
                      </Avatar>
                      <div
                        className={cn(
                          "max-w-[80%] rounded-2xl px-3 py-2 text-sm",
                          msg.role === "user"
                            ? "bg-primary text-primary-foreground"
                            : "bg-muted"
                        )}
                      >
                        <div className="whitespace-pre-wrap">{msg.content}</div>
                      </div>
                    </div>
                  ))}

                  {isLoading && messages[messages.length - 1]?.role !== "assistant" && (
                    <div className="flex gap-2">
                      <Avatar className="h-7 w-7 flex-shrink-0 mt-1">
                        <AvatarFallback className="text-xs">AI</AvatarFallback>
                      </Avatar>
                      <div className="bg-muted rounded-2xl px-3 py-2">
                        <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                      </div>
                    </div>
                  )}
                </div>
              </ScrollArea>

              {messages.length > 1 && (
                <div className="px-4 py-2 border-t">
                  <Button
                    variant="outline"
                    className="w-full text-xs"
                    size="sm"
                    onClick={() => void handleGenerate()}
                    disabled={isLoading}
                  >
                    <FilePen className="h-3 w-3 mr-1" />
                    基于对话生成文章
                  </Button>
                </div>
              )}

              <div className="px-4 py-3 border-t">
                <div className="flex gap-2 items-end">
                  <Textarea
                    ref={inputRef}
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="输入消息... (Enter 发送, Shift+Enter 换行)"
                    className="min-h-[44px] max-h-[120px] resize-none text-sm"
                    rows={1}
                    disabled={isLoading}
                  />
                  <Button
                    size="icon-sm"
                    onClick={() => void handleSend()}
                    disabled={!input.trim() || isLoading}
                  >
                    {isLoading ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Send className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              </div>
            </>
          )}
        </div>
      )}

      <Button
        size="icon"
        className="h-14 w-14 rounded-full shadow-lg"
        onClick={() => setIsOpen(!isOpen)}
      >
        {isOpen ? (
          <X className="h-5 w-5" />
        ) : (
          <>
            <MessageSquare className="h-5 w-5" />
            <span className="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[10px] text-primary-foreground">
              AI
            </span>
          </>
        )}
      </Button>
    </div>
  );
}
