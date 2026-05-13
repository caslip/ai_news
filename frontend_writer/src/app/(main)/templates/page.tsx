"use client";

import { useRouter } from "next/navigation";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { LayoutTemplate } from "lucide-react";
import { useTemplates } from "@/hooks/useWriter";
import { toast } from "sonner";

const CATEGORY_COLORS: Record<string, string> = {
  技术博客: "bg-blue-500/10 text-blue-600 border-blue-500/20",
  产品评测: "bg-purple-500/10 text-purple-600 border-purple-500/20",
  行业分析: "bg-green-500/10 text-green-600 border-green-500/20",
  教程指南: "bg-amber-500/10 text-amber-600 border-amber-500/20",
};

export default function TemplatesPage() {
  const router = useRouter();
  const { data, isLoading } = useTemplates();

  const templates = data?.items ?? [];

  const handleUse = (templateId: string, style: string, tone: string) => {
    router.push(`/generate?template=${templateId}&style=${style}&tone=${tone}`);
    toast.success("已应用模板");
  };

  return (
    <div className="container mx-auto px-6 py-6 space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold">模板库</h1>
        <p className="text-muted-foreground text-sm mt-1">
          选择一个写作模板，快速开始创作
        </p>
      </div>

      {/* Templates Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <Card key={i}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="space-y-2">
                    <Skeleton className="h-5 w-32" />
                    <Skeleton className="h-4 w-48" />
                  </div>
                  <Skeleton className="h-5 w-16 rounded-full" />
                </div>
              </CardHeader>
              <CardContent>
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-3/4 mt-2" />
                <Skeleton className="h-9 w-24 mt-4" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : templates.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <LayoutTemplate className="h-12 w-12 text-muted-foreground/30 mb-4" />
          <p className="text-muted-foreground">暂无模板</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {templates.map((template) => {
            const colorClass =
              CATEGORY_COLORS[template.category] ||
              "bg-muted text-muted-foreground border-border";
            return (
              <Card key={template.id} className="hover:shadow-md transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between gap-2">
                    <div className="space-y-1">
                      <CardTitle className="text-base">{template.name}</CardTitle>
                      <CardDescription className="line-clamp-2">
                        {template.description}
                      </CardDescription>
                    </div>
                    <Badge
                      variant="outline"
                      className={`shrink-0 ${colorClass}`}
                    >
                      {template.category}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-xs text-muted-foreground mb-4">
                    已使用 {template.use_count} 次
                  </p>
                  <Button
                    size="sm"
                    onClick={() =>
                      handleUse(template.id, template.style, template.tone)
                    }
                  >
                    使用模板
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {/* Category Legend */}
      <div className="flex flex-wrap gap-3">
        {Object.entries(CATEGORY_COLORS).map(([category, colorClass]) => (
          <div key={category} className="flex items-center gap-2">
            <span
              className={`inline-block w-3 h-3 rounded-full border ${colorClass}`}
            />
            <span className="text-xs text-muted-foreground">{category}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
