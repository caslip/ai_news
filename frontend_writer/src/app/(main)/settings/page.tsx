"use client";

import { useState, useEffect, useCallback } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import {
  Key,
  Plus,
  Edit2,
  Trash2,
  TestTube,
  Check,
  AlertCircle,
  Eye,
  EyeOff,
  Loader2,
} from "lucide-react";
import { apiClient } from "@/lib/api";

const STYLE_OPTIONS = [
  { value: "technical", label: "技术解读" },
  { value: "news_analysis", label: "热点分析" },
  { value: "tutorial", label: "教程指南" },
  { value: "opinion", label: "观点评论" },
  { value: "product_review", label: "产品评测" },
];

const TONE_OPTIONS = [
  { value: "professional", label: "专业严谨" },
  { value: "casual", label: "轻松活泼" },
  { value: "concise", label: "简洁明了" },
  { value: "storytelling", label: "故事叙述" },
];

const LENGTH_OPTIONS = [
  { value: "short", label: "短篇 (~500字)" },
  { value: "medium", label: "中篇 (~1500字)" },
  { value: "long", label: "长篇 (~3000字)" },
];

// Provider configuration
const PROVIDERS = [
  { id: "deepseek", name: "DeepSeek", logo: "🔮", color: "from-violet-500 to-purple-500" },
  { id: "kimi", name: "Kimi", logo: "🌙", color: "from-blue-500 to-cyan-500" },
  { id: "minimax", name: "MiniMax", logo: "🎯", color: "from-orange-500 to-red-500" },
  { id: "openai", name: "OpenAI", logo: "🤖", color: "from-green-500 to-emerald-500" },
  { id: "gemini", name: "Gemini", logo: "✨", color: "from-yellow-500 to-amber-500" },
  { id: "anthropic", name: "Anthropic", logo: "🧠", color: "from-orange-400 to-red-400" },
  { id: "openrouter", name: "OpenRouter", logo: "🌐", color: "from-indigo-500 to-blue-500" },
] as const;

type ProviderId = typeof PROVIDERS[number]["id"];
type ApiKeyStatus = "configured" | "unconfigured" | "error" | "testing";

interface ApiKeyInfo {
  provider: string;
  masked_key: string;
  label?: string;
  is_active: boolean;
  created_at?: string;
}

interface ProviderCardProps {
  id: ProviderId;
  name: string;
  logo: string;
  color: string;
  status: ApiKeyStatus;
  onAdd: () => void;
  onEdit: () => void;
  onDelete: () => void;
  onTest: () => void;
  isTesting?: boolean;
}

function ProviderCard({
  id,
  name,
  logo,
  color,
  status,
  onAdd,
  onEdit,
  onDelete,
  onTest,
  isTesting,
}: ProviderCardProps) {
  const isConfigured = status === "configured";
  const isError = status === "error";
  const isTestingStatus = status === "testing" || isTesting;

  return (
    <div
      className={`
        relative p-4 rounded-lg border transition-all duration-200
        ${isConfigured ? "bg-card border-border" : "bg-card/50 border-border/50"}
        ${isError ? "border-destructive/50 bg-destructive/5" : ""}
        ${isTestingStatus ? "border-primary/50 bg-primary/5" : ""}
        hover:border-primary/30 hover:shadow-sm
      `}
    >
      {/* Header */}
      <div className="flex items-center gap-3 mb-3">
        <div
          className={`w-10 h-10 rounded-lg bg-gradient-to-br ${color} flex items-center justify-center text-xl shadow-sm`}
        >
          {isTestingStatus ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            logo
          )}
        </div>
        <div className="flex-1 min-w-0">
          <h4 className="font-medium text-sm truncate">{name}</h4>
          <div className="flex items-center gap-1.5 mt-0.5">
            <span
              className={`w-2 h-2 rounded-full ${
                isConfigured
                  ? "bg-green-500"
                  : isError
                  ? "bg-destructive"
                  : isTestingStatus
                  ? "bg-primary animate-pulse"
                  : "bg-muted-foreground/30"
              }`}
            />
            <span className="text-xs text-muted-foreground">
              {isConfigured ? "已配置" : isError ? "配置错误" : isTestingStatus ? "测试中..." : "未配置"}
            </span>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex gap-1.5">
        {isConfigured ? (
          <>
            <Button
              variant="ghost"
              size="icon-xs"
              onClick={onTest}
              disabled={isTesting}
              title="测试连接"
              className="hover:text-primary"
            >
              {isTesting ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <TestTube className="w-3.5 h-3.5" />
              )}
            </Button>
            <Button
              variant="ghost"
              size="icon-xs"
              onClick={onEdit}
              title="编辑密钥"
              className="hover:text-primary"
            >
              <Edit2 className="w-3.5 h-3.5" />
            </Button>
            <Button
              variant="ghost"
              size="icon-xs"
              onClick={onDelete}
              title="删除密钥"
              className="hover:text-destructive"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </Button>
          </>
        ) : (
          <Button
            variant="outline"
            size="sm"
            className="w-full text-xs h-7 gap-1"
            onClick={onAdd}
          >
            <Plus className="w-3 h-3" />
            添加密钥
          </Button>
        )}
      </div>
    </div>
  );
}

interface AddKeyDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  provider?: ProviderId;
  mode: "add" | "edit";
  onSave: (provider: ProviderId, apiKey: string, label?: string) => Promise<void>;
  onTest: (provider: ProviderId, apiKey: string) => Promise<{ success: boolean; message: string }>;
}

function AddKeyDialog({
  open,
  onOpenChange,
  provider: initialProvider,
  mode,
  onSave,
  onTest,
}: AddKeyDialogProps) {
  const [selectedProvider, setSelectedProvider] = useState<ProviderId | "">("");
  const [apiKey, setApiKey] = useState("");
  const [label, setLabel] = useState("");
  const [showKey, setShowKey] = useState(false);
  const [isTesting, setIsTesting] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);

  useEffect(() => {
    if (open) {
      setSelectedProvider(initialProvider || "");
      setApiKey("");
      setLabel("");
      setShowKey(false);
      setTestResult(null);
      setIsTesting(false);
      setIsSaving(false);
    }
  }, [open, initialProvider]);

  const handleTest = async () => {
    const provider = selectedProvider as ProviderId;
    if (!provider || !apiKey.trim()) {
      toast.error("请选择提供商并输入 API 密钥");
      return;
    }

    setIsTesting(true);
    setTestResult(null);

    try {
      const result = await onTest(provider, apiKey);
      setTestResult(result);
      if (result.success) {
        toast.success("连接测试成功");
      } else {
        toast.error("连接测试失败: " + result.message);
      }
    } catch {
      setTestResult({ success: false, message: "测试请求失败" });
      toast.error("测试请求失败");
    } finally {
      setIsTesting(false);
    }
  };

  const handleSave = async () => {
    const provider = selectedProvider as ProviderId;
    if (!provider || !apiKey.trim()) {
      toast.error("请选择提供商并输入 API 密钥");
      return;
    }

    setIsSaving(true);
    try {
      await onSave(provider, apiKey, label || undefined);
      toast.success(mode === "add" ? "API 密钥已添加" : "API 密钥已更新");
      onOpenChange(false);
    } catch {
      toast.error("保存失败，请重试");
    } finally {
      setIsSaving(false);
    }
  };

  const configuredProviders = [] as string[];
  const availableProviders = PROVIDERS.filter(
    (p) => mode === "add" || p.id === selectedProvider
  );

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Key className="w-5 h-5 text-primary" />
            {mode === "add" ? "添加 API 密钥" : "更新 API 密钥"}
          </DialogTitle>
          <DialogDescription>
            {initialProvider
              ? `为 ${PROVIDERS.find((p) => p.id === initialProvider)?.name} 添加 API 密钥`
              : mode === "add"
              ? "选择一个 AI 服务提供商并输入您的 API 密钥"
              : "输入新的 API 密钥来更新现有配置"}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-2">
          {/* Provider Selection - Hidden when provider is pre-selected */}
          {!initialProvider ? (
            <div className="space-y-2">
              <Label htmlFor="provider">AI 服务提供商</Label>
              <Select
                value={selectedProvider}
                onValueChange={(v) => setSelectedProvider(v as ProviderId)}
              >
                <SelectTrigger id="provider">
                  <SelectValue placeholder="选择提供商..." />
                </SelectTrigger>
                <SelectContent>
                  {PROVIDERS.map((provider) => (
                    <SelectItem key={provider.id} value={provider.id}>
                      <span className="flex items-center gap-2">
                        <span>{provider.logo}</span>
                        <span>{provider.name}</span>
                      </span>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          ) : (
            <div className="space-y-2">
              <Label>AI 服务提供商</Label>
              <div className="flex items-center gap-2 px-3 py-2 bg-muted/50 rounded-md border border-border/50 text-sm">
                {PROVIDERS.find((p) => p.id === initialProvider)?.logo}
                <span>{PROVIDERS.find((p) => p.id === initialProvider)?.name}</span>
              </div>
            </div>
          )}

          {/* API Key Input */}
          <div className="space-y-2">
            <Label htmlFor="api-key">API 密钥</Label>
            <div className="relative">
              <Input
                id="api-key"
                type={showKey ? "text" : "password"}
                placeholder="sk-..."
                value={apiKey}
                onChange={(e) => {
                  setApiKey(e.target.value);
                  setTestResult(null);
                }}
                className="pr-10 font-mono text-sm"
              />
              <Button
                type="button"
                variant="ghost"
                size="icon"
                className="absolute right-0 top-0 h-full px-3 hover:bg-transparent"
                onClick={() => setShowKey(!showKey)}
              >
                {showKey ? (
                  <EyeOff className="w-4 h-4 text-muted-foreground" />
                ) : (
                  <Eye className="w-4 h-4 text-muted-foreground" />
                )}
              </Button>
            </div>
          </div>

          {/* Label (Optional) */}
          <div className="space-y-2">
            <Label htmlFor="label">
              标签{" "}
              <span className="text-xs text-muted-foreground font-normal">
                (可选)
              </span>
            </Label>
            <Input
              id="label"
              placeholder="例如：工作账号 / 个人账号"
              value={label}
              onChange={(e) => setLabel(e.target.value)}
            />
          </div>

          {/* Test Result */}
          {testResult && (
            <div
              className={`p-3 rounded-lg text-sm flex items-start gap-2 ${
                testResult.success
                  ? "bg-green-500/10 text-green-600 dark:text-green-400"
                  : "bg-destructive/10 text-destructive"
              }`}
            >
              {testResult.success ? (
                <Check className="w-4 h-4 mt-0.5 shrink-0" />
              ) : (
                <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
              )}
              <span>{testResult.message}</span>
            </div>
          )}
        </div>

        <DialogFooter className="gap-2 sm:gap-0">
          <Button
            variant="outline"
            onClick={handleTest}
            disabled={!selectedProvider || !apiKey.trim() || isTesting || isSaving}
            className="gap-1.5"
          >
            {isTesting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                测试中...
              </>
            ) : (
              <>
                <TestTube className="w-4 h-4" />
                测试连接
              </>
            )}
          </Button>
          <Button
            onClick={handleSave}
            disabled={!selectedProvider || !apiKey.trim() || isSaving || isTesting}
            className="gap-1.5"
          >
            {isSaving ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                保存中...
              </>
            ) : (
              <>
                <Check className="w-4 h-4" />
                {mode === "add" ? "添加" : "更新"}
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

interface DeleteConfirmDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  providerName: string;
  onConfirm: () => void;
}

function DeleteConfirmDialog({
  open,
  onOpenChange,
  providerName,
  onConfirm,
}: DeleteConfirmDialogProps) {
  const [isDeleting, setIsDeleting] = useState(false);

  const handleConfirm = async () => {
    setIsDeleting(true);
    try {
      await onConfirm();
      toast.success(`已删除 ${providerName} 的 API 密钥`);
      onOpenChange(false);
    } catch {
      toast.error("删除失败，请重试");
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-destructive">
            <Trash2 className="w-5 h-5" />
            确认删除
          </DialogTitle>
          <DialogDescription>
            确定要删除 {providerName} 的 API 密钥吗？此操作无法撤销。
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            取消
          </Button>
          <Button variant="destructive" onClick={handleConfirm} disabled={isDeleting}>
            {isDeleting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                删除中...
              </>
            ) : (
              <>
                <Trash2 className="w-4 h-4" />
                确认删除
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

export default function SettingsPage() {
  const [defaultStyle, setDefaultStyle] = useState("technical");
  const [defaultTone, setDefaultTone] = useState("professional");
  const [defaultLength, setDefaultLength] = useState("medium");
  const [autoSave, setAutoSave] = useState(true);
  const [streaming, setStreaming] = useState(false);
  const [apiUrl, setApiUrl] = useState("http://localhost:8001");

  // API Keys state
  const [apiKeys, setApiKeys] = useState<ApiKeyInfo[]>([]);
  const [isLoadingKeys, setIsLoadingKeys] = useState(true);
  const [testingProvider, setTestingProvider] = useState<string | null>(null);

  // Dialogs state
  const [addKeyDialogOpen, setAddKeyDialogOpen] = useState(false);
  const [editProvider, setEditProvider] = useState<ProviderId | undefined>();
  const [deleteProvider, setDeleteProvider] = useState<{ id: ProviderId; name: string } | null>(null);

  // Fetch API keys from backend
  const fetchApiKeys = useCallback(async () => {
    setIsLoadingKeys(true);
    try {
      const response = await apiClient.get("/api/api-keys");
      if (response.data) {
        setApiKeys(response.data.items || []);
      }
    } catch {
      console.error("Failed to fetch API keys");
    } finally {
      setIsLoadingKeys(false);
    }
  }, []);

  useEffect(() => {
    fetchApiKeys();
  }, [fetchApiKeys]);

  const getKeyStatus = (providerId: string): ApiKeyStatus => {
    if (testingProvider === providerId) return "testing";
    const key = apiKeys.find((k) => k.provider === providerId);
    if (!key) return "unconfigured";
    // API response has is_active, map to configured/error based on is_active
    return key.is_active ? "configured" : "error";
  };

  const handleAddKey = async (provider: ProviderId, apiKey: string, label?: string) => {
    const response = await apiClient.post("/api/api-keys", { provider, api_key: apiKey, label });

    if (response.status !== 201 && response.status !== 200) {
      throw new Error("Failed to add API key");
    }

    await fetchApiKeys();
  };

  const handleUpdateKey = async (provider: ProviderId, apiKey: string) => {
    // Check if key already exists
    const existingKey = apiKeys.find((k) => k.provider === provider);
    
    if (existingKey) {
      // Key exists, use PATCH to update
      await apiClient.patch(`/api/api-keys/${provider}`, { api_key: apiKey });
    } else {
      // Key doesn't exist, use POST to create
      await apiClient.post("/api/api-keys", { provider, api_key: apiKey });
    }
    setEditProvider(undefined);
    await fetchApiKeys();
  };

  const handleDeleteKey = async (provider: ProviderId) => {
    await apiClient.delete(`/api/api-keys/${provider}`);
    await fetchApiKeys();
  };

  const handleTestKey = async (provider: ProviderId) => {
    setTestingProvider(provider);

    try {
      // 测试已存储的密钥，后端会自动从数据库解密并测试
      const response = await apiClient.post("/api/api-keys/test", {
        provider,
      });

      const result = response.data;

      if (result.success) {
        toast.success(`${PROVIDERS.find((p) => p.id === provider)?.name} 连接成功`);
      } else {
        toast.error(`测试失败: ${result.message}`);
      }
    } catch (error) {
      // 提取 axios 错误信息
      const axiosError = error as { response?: { data?: { detail?: string; message?: string } } };
      const errorMsg = axiosError.response?.data?.detail 
        || axiosError.response?.data?.message 
        || "测试请求失败";
      toast.error(errorMsg);
    } finally {
      setTestingProvider(null);
    }
  };

  const handleTestNewKey = async (
    provider: ProviderId,
    apiKey: string
  ): Promise<{ success: boolean; message: string }> => {
    try {
      const response = await apiClient.post("/api/api-keys/test", {
        provider,
        api_key: apiKey,
      });

      return response.data;
    } catch (error) {
      // 提取 axios 错误信息
      const axiosError = error as { response?: { data?: { detail?: string; message?: string } } };
      const errorMsg = axiosError.response?.data?.detail 
        || axiosError.response?.data?.message 
        || "测试请求失败";
      return { success: false, message: errorMsg };
    }
  };

  const handleSave = () => {
    toast.success("设置已保存");
  };

  return (
    <div className="container mx-auto px-6 py-6 space-y-6 max-w-2xl">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold">设置</h1>
        <p className="text-muted-foreground text-sm mt-1">
          配置你的写作偏好和 API 密钥
        </p>
      </div>

      {/* Writing Preferences */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <span>📝</span> 写作偏好
          </CardTitle>
          <CardDescription>
            设置默认的写作风格，这些设置将作为新文章的初始值
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>默认写作风格</Label>
            <Select value={defaultStyle} onValueChange={setDefaultStyle}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {STYLE_OPTIONS.map((opt) => (
                  <SelectItem key={opt.value} value={opt.value}>
                    {opt.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label>默认语气</Label>
            <Select value={defaultTone} onValueChange={setDefaultTone}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {TONE_OPTIONS.map((opt) => (
                  <SelectItem key={opt.value} value={opt.value}>
                    {opt.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label>默认篇幅</Label>
            <Select value={defaultLength} onValueChange={setDefaultLength}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {LENGTH_OPTIONS.map((opt) => (
                  <SelectItem key={opt.value} value={opt.value}>
                    {opt.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <Separator />

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>自动保存草稿</Label>
              <p className="text-sm text-muted-foreground">
                每 30 秒自动保存一次草稿
              </p>
            </div>
            <Switch checked={autoSave} onCheckedChange={setAutoSave} />
          </div>

          <Separator />

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>流式输出</Label>
              <p className="text-sm text-muted-foreground">
                实时显示生成进度（需要后端支持 SSE）
              </p>
            </div>
            <Switch checked={streaming} onCheckedChange={setStreaming} />
          </div>
        </CardContent>
      </Card>

      {/* API Keys Management */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Key className="w-5 h-5 text-primary" />
            API 密钥配置
          </CardTitle>
          <CardDescription>
            配置 AI 服务提供商的 API 密钥，支持多个提供商
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoadingKeys ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="p-4 rounded-lg border">
                  <div className="flex items-center gap-3 mb-3">
                    <Skeleton className="w-10 h-10 rounded-lg" />
                    <div className="space-y-2 flex-1">
                      <Skeleton className="h-4 w-16" />
                      <Skeleton className="h-3 w-12" />
                    </div>
                  </div>
                  <Skeleton className="h-7 w-full" />
                </div>
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              {PROVIDERS.map((provider) => (
                <ProviderCard
                  key={provider.id}
                  id={provider.id}
                  name={provider.name}
                  logo={provider.logo}
                  color={provider.color}
                  status={getKeyStatus(provider.id)}
                  isTesting={testingProvider === provider.id}
                  onAdd={() => {
                    setEditProvider(provider.id);
                    setAddKeyDialogOpen(true);
                  }}
                  onEdit={() => {
                    setEditProvider(provider.id);
                    setAddKeyDialogOpen(true);
                  }}
                  onDelete={() => setDeleteProvider({ id: provider.id, name: provider.name })}
                  onTest={() => handleTestKey(provider.id)}
                />
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* API Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <span>🌐</span> API 地址
          </CardTitle>
          <CardDescription>
            配置后端 API 连接地址
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="api-url">API 地址</Label>
            <Input
              id="api-url"
              placeholder="http://localhost:8001"
              value={apiUrl}
              onChange={(e) => setApiUrl(e.target.value)}
            />
            <p className="text-xs text-muted-foreground">
              修改后需要刷新页面生效
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Save Button */}
      <div className="flex justify-end">
        <Button onClick={handleSave}>保存设置</Button>
      </div>

      {/* Add/Edit Key Dialog */}
      <AddKeyDialog
        open={addKeyDialogOpen}
        onOpenChange={(open) => {
          setAddKeyDialogOpen(open);
          if (!open) setEditProvider(undefined);
        }}
        provider={editProvider}
        mode={editProvider ? "edit" : "add"}
        onSave={editProvider ? handleUpdateKey : handleAddKey}
        onTest={handleTestNewKey}
      />

      {/* Delete Confirm Dialog */}
      <DeleteConfirmDialog
        open={!!deleteProvider}
        onOpenChange={(open) => !open && setDeleteProvider(null)}
        providerName={deleteProvider?.name || ""}
        onConfirm={() => deleteProvider && handleDeleteKey(deleteProvider.id)}
      />
    </div>
  );
}
