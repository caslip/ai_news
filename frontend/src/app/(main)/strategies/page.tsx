"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Separator } from "@/components/ui/separator";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Settings2,
  Plus,
  History,
  Check,
  RotateCcw,
  Trash2,
  Clock,
  Loader2,
  Zap,
} from "lucide-react";

interface Strategy {
  id: string;
  name: string;
  description?: string;
  version: number;
  params: {
    max_fan_count: number;
    min_engagement: number;
    min_viral_score: number;
    min_quality_score: number;
    hotness_boost_threshold: number;
    exclude_keywords: string[];
  };
  is_active: boolean;
  created_at: string;
}

const mockStrategies: Strategy[] = [
  {
    id: "1",
    name: "低粉爆文标准版",
    description: "默认的低粉爆文筛选策略，适合大多数场景",
    version: 3,
    params: {
      max_fan_count: 10000,
      min_engagement: 100,
      min_viral_score: 5.0,
      min_quality_score: 6.0,
      hotness_boost_threshold: 7.5,
      exclude_keywords: ["广告", "推广"],
    },
    is_active: true,
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
  },
  {
    id: "2",
    name: "高门槛版",
    description: "更严格的筛选条件，只保留最优质的爆文",
    version: 1,
    params: {
      max_fan_count: 5000,
      min_engagement: 500,
      min_viral_score: 10.0,
      min_quality_score: 7.5,
      hotness_boost_threshold: 8.0,
      exclude_keywords: ["广告", "推广", "抽奖"],
    },
    is_active: false,
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 48).toISOString(),
  },
];

const defaultParams = {
  max_fan_count: 10000,
  min_engagement: 100,
  min_viral_score: 5.0,
  min_quality_score: 6.0,
  hotness_boost_threshold: 7.5,
  exclude_keywords: [] as string[],
};

export default function StrategiesPage() {
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [newStrategy, setNewStrategy] = useState({
    name: "",
    description: "",
    params: { ...defaultParams },
  });
  const queryClient = useQueryClient();

  const { data: strategies, isLoading } = useQuery({
    queryKey: ["strategies"],
    queryFn: async () => {
      await new Promise((r) => setTimeout(r, 300));
      return mockStrategies;
    },
  });

  const activeStrategy = strategies?.find((s) => s.is_active);

  const createMutation = useMutation({
    mutationFn: async () => {
      await new Promise((r) => setTimeout(r, 500));
      return { ...newStrategy, id: Math.random().toString(), version: 1, is_active: false, created_at: new Date().toISOString() };
    },
    onSuccess: () => {
      setIsCreateDialogOpen(false);
      setNewStrategy({ name: "", description: "", params: { ...defaultParams } });
      queryClient.invalidateQueries({ queryKey: ["strategies"] });
    },
  });

  const activateMutation = useMutation({
    mutationFn: async (id: string) => {
      await new Promise((r) => setTimeout(r, 300));
      return id;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["strategies"] }),
  });

  return (
    <div className="flex flex-col h-full">
      <header className="border-b bg-card/50 backdrop-blur supports-[backdrop-filter]:bg-card/50 sticky top-0 z-10">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl font-bold flex items-center gap-2">
                <Settings2 className="h-6 w-6" />
                精选策略
              </h1>
              <p className="text-sm text-muted-foreground">
                配置 AI 评分规则和低粉爆文筛选条件
              </p>
            </div>
            <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  新建策略
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
                <DialogHeader>
                  <DialogTitle>创建新策略</DialogTitle>
                  <DialogDescription>
                    配置你的精选策略参数，每次修改都会创建新版本
                  </DialogDescription>
                </DialogHeader>

                <div className="space-y-6 py-4">
                  <div className="space-y-2">
                    <Label>策略名称</Label>
                    <Input
                      placeholder="例如：我的精选策略"
                      value={newStrategy.name}
                      onChange={(e) => setNewStrategy({ ...newStrategy, name: e.target.value })}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>策略描述</Label>
                    <Input
                      placeholder="描述这个策略的用途..."
                      value={newStrategy.description}
                      onChange={(e) => setNewStrategy({ ...newStrategy, description: e.target.value })}
                    />
                  </div>

                  <Separator />

                  <div className="space-y-6">
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <Label>最大粉丝数</Label>
                        <span className="text-sm font-medium">{newStrategy.params.max_fan_count.toLocaleString()}</span>
                      </div>
                      <Slider
                        value={[newStrategy.params.max_fan_count]}
                        onValueChange={([v]) => setNewStrategy({ ...newStrategy, params: { ...newStrategy.params, max_fan_count: v } })}
                        min={1000}
                        max={100000}
                        step={1000}
                      />
                      <p className="text-xs text-muted-foreground">超过此粉丝数的账号内容将被过滤</p>
                    </div>

                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <Label>最低互动数</Label>
                        <span className="text-sm font-medium">{newStrategy.params.min_engagement}</span>
                      </div>
                      <Slider
                        value={[newStrategy.params.min_engagement]}
                        onValueChange={([v]) => setNewStrategy({ ...newStrategy, params: { ...newStrategy.params, min_engagement: v } })}
                        min={10}
                        max={1000}
                        step={10}
                      />
                      <p className="text-xs text-muted-foreground">点赞 + 转发×3 + 评论×2 的最低阈值</p>
                    </div>

                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <Label>最低爆文指数</Label>
                        <span className="text-sm font-medium">{newStrategy.params.min_viral_score.toFixed(1)}</span>
                      </div>
                      <Slider
                        value={[newStrategy.params.min_viral_score * 10]}
                        onValueChange={([v]) => setNewStrategy({ ...newStrategy, params: { ...newStrategy.params, min_viral_score: v / 10 } })}
                        min={10}
                        max={50}
                        step={5}
                      />
                      <p className="text-xs text-muted-foreground">爆文指数 = (互动数 / 粉丝数) × 1000</p>
                    </div>

                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <Label>最低 AI 质量评分</Label>
                        <span className="text-sm font-medium">{newStrategy.params.min_quality_score.toFixed(1)}</span>
                      </div>
                      <Slider
                        value={[newStrategy.params.min_quality_score * 10]}
                        onValueChange={([v]) => setNewStrategy({ ...newStrategy, params: { ...newStrategy.params, min_quality_score: v / 10 } })}
                        min={30}
                        max={100}
                        step={5}
                      />
                      <p className="text-xs text-muted-foreground">AI 评分系统给出的内容质量分数 (1-10)</p>
                    </div>
                  </div>
                </div>

                <DialogFooter>
                  <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                    取消
                  </Button>
                  <Button onClick={() => createMutation.mutate()}>创建策略</Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
        </div>
      </header>

      <div className="flex-1 container mx-auto px-6 py-6 space-y-6">
        {/* Active Strategy */}
        {activeStrategy && (
          <Card className="border-green-500/50 bg-green-500/5">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-green-500/20 rounded-lg">
                    <Zap className="h-5 w-5 text-green-600" />
                  </div>
                  <div>
                    <CardTitle className="text-lg">{activeStrategy.name}</CardTitle>
                    <CardDescription>v{activeStrategy.version} · 当前激活</CardDescription>
                  </div>
                </div>
                <Badge variant="default" className="bg-green-500">使用中</Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-4 gap-4">
                <div>
                  <p className="text-xs text-muted-foreground">最大粉丝数</p>
                  <p className="text-lg font-semibold">{activeStrategy.params.max_fan_count.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">最低互动数</p>
                  <p className="text-lg font-semibold">{activeStrategy.params.min_engagement}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">最低爆文指数</p>
                  <p className="text-lg font-semibold">{activeStrategy.params.min_viral_score.toFixed(1)}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">最低 AI 评分</p>
                  <p className="text-lg font-semibold">{activeStrategy.params.min_quality_score.toFixed(1)}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* All Strategies */}
        <div>
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <History className="h-5 w-5" />
            版本历史
          </h2>
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : (
            <Card>
              <CardContent className="p-0">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>策略</TableHead>
                      <TableHead>版本</TableHead>
                      <TableHead>最大粉丝</TableHead>
                      <TableHead>最低互动</TableHead>
                      <TableHead>创建时间</TableHead>
                      <TableHead className="text-right">操作</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {strategies?.map((strategy) => (
                      <TableRow key={strategy.id}>
                        <TableCell>
                          <div>
                            <p className="font-medium">{strategy.name}</p>
                            {strategy.description && (
                              <p className="text-xs text-muted-foreground">{strategy.description}</p>
                            )}
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline">v{strategy.version}</Badge>
                        </TableCell>
                        <TableCell>{strategy.params.max_fan_count.toLocaleString()}</TableCell>
                        <TableCell>{strategy.params.min_engagement}</TableCell>
                        <TableCell className="text-sm text-muted-foreground">
                          {new Date(strategy.created_at).toLocaleDateString("zh-CN")}
                        </TableCell>
                        <TableCell className="text-right">
                          <div className="flex items-center justify-end gap-1">
                            {strategy.is_active ? (
                              <Badge variant="default" className="bg-green-500">使用中</Badge>
                            ) : (
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => activateMutation.mutate(strategy.id)}
                                disabled={activateMutation.isPending}
                              >
                                <Check className="h-4 w-4 mr-1" />
                                激活
                              </Button>
                            )}
                            <Button variant="ghost" size="icon" className="h-8 w-8 text-red-500 hover:text-red-600">
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
