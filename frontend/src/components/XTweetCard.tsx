"use client";

import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  Heart,
  Repeat2,
  MessageSquare,
  ExternalLink,
  Clock,
  Bookmark,
} from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { zhCN } from "date-fns/locale";

interface XTweetCardProps {
  tweet: {
    id: string;
    title: string;
    url: string;
    summary?: string;
    source_name: string;
    source_type: string;
    hot_score: number;
    author?: string;
    engagement?: {
      likes: number;
      retweets: number;
      comments: number;
    };
    published_at?: string;
    fetched_at: string;
    is_bookmarked?: boolean;
  };
  onBookmark?: (id: string) => void;
  variant?: "default" | "compact";
}

function formatNumber(num: number): string {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + "M";
  }
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + "w";
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + "k";
  }
  return num.toString();
}

function getInitials(name: string): string {
  return name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
}

export function XTweetCard({
  tweet,
  onBookmark,
  variant = "default",
}: XTweetCardProps) {
  const isCompact = variant === "compact";
  const authorInitials = tweet.author ? getInitials(tweet.author) : "X";
  const isNitter = tweet.source_type === "nitter";

  return (
    <Card
      className={`group hover:shadow-md transition-all duration-200 hover:border-sky-500/50 border-sky-200 dark:border-sky-800 ${
        isCompact ? "py-0" : ""
      }`}
    >
      {!isCompact && (
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between gap-3">
            <div className="flex items-start gap-3">
              {/* Avatar */}
              <Avatar className="h-10 w-10 rounded-full bg-sky-100 dark:bg-sky-900">
                <AvatarFallback className="text-sky-600 dark:text-sky-300 font-semibold text-sm">
                  {authorInitials}
                </AvatarFallback>
              </Avatar>

              <div className="flex-1 min-w-0">
                {/* Author info row */}
                <div className="flex items-center gap-2 mb-1">
                  {tweet.author && (
                    <span className="font-semibold text-sm truncate">
                      {tweet.author}
                    </span>
                  )}
                  <Badge
                    variant="outline"
                    className="bg-sky-500/10 text-sky-500 border-sky-500/30 text-xs"
                  >
                    <XIcon className="h-3 w-3 mr-1" />
                    {isNitter ? "Nitter" : "X"}
                  </Badge>
                  <span className="text-xs text-muted-foreground truncate">
                    {tweet.source_name}
                  </span>
                </div>

                {/* Timestamp */}
                <div className="flex items-center gap-1 text-xs text-muted-foreground">
                  <Clock className="h-3 w-3" />
                  {formatDistanceToNow(
                    new Date(tweet.published_at || tweet.fetched_at),
                    {
                      addSuffix: true,
                      locale: zhCN,
                    }
                  )}
                </div>
              </div>
            </div>

            {/* Hot score indicator */}
            <div className="flex flex-col items-center gap-1 text-center min-w-[50px]">
              <span className="text-xs text-muted-foreground">热度</span>
              <span className="text-lg font-bold text-sky-500">
                {tweet.hot_score.toFixed(1)}
              </span>
            </div>
          </div>
        </CardHeader>
      )}

      <CardContent className={isCompact ? "pt-0" : ""}>
        {/* Tweet title/content */}
        <div className="space-y-3">
          {isCompact && (
            <div className="flex items-center gap-2 mb-2">
              <Avatar className="h-6 w-6 rounded-full bg-sky-100 dark:bg-sky-900">
                <AvatarFallback className="text-sky-600 dark:text-sky-300 font-semibold text-xs">
                  {authorInitials}
                </AvatarFallback>
              </Avatar>
              <span className="text-xs font-medium truncate">{tweet.author}</span>
              <Badge
                variant="outline"
                className="bg-sky-500/10 text-sky-500 border-sky-500/30 text-xs py-0 px-1.5"
              >
                <XIcon className="h-2.5 w-2.5 mr-0.5" />
              </Badge>
            </div>
          )}

          <a
            href={tweet.url}
            target="_blank"
            rel="noopener noreferrer"
            className="block"
          >
            <p
              className={`text-foreground hover:text-sky-500 transition-colors ${
                isCompact ? "text-sm line-clamp-2" : "text-base leading-relaxed line-clamp-4"
              }`}
            >
              {tweet.title}
            </p>
          </a>

          {tweet.summary && !isCompact && (
            <p className="text-sm text-muted-foreground line-clamp-2">
              {tweet.summary}
            </p>
          )}

          {/* Engagement stats */}
          {tweet.engagement && (
            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              {tweet.engagement.likes > 0 && (
                <span className="flex items-center gap-1 hover:text-pink-500 transition-colors">
                  <Heart className="h-4 w-4" />
                  {formatNumber(tweet.engagement.likes)}
                </span>
              )}
              {tweet.engagement.retweets > 0 && (
                <span className="flex items-center gap-1 hover:text-green-500 transition-colors">
                  <Repeat2 className="h-4 w-4" />
                  {formatNumber(tweet.engagement.retweets)}
                </span>
              )}
              {tweet.engagement.comments > 0 && (
                <span className="flex items-center gap-1 hover:text-sky-500 transition-colors">
                  <MessageSquare className="h-4 w-4" />
                  {formatNumber(tweet.engagement.comments)}
                </span>
              )}
            </div>
          )}

          {/* Action buttons */}
          <div className="flex items-center justify-between pt-2 border-t border-border/50">
            <div className="flex items-center gap-1 text-xs text-muted-foreground">
              {isCompact && (
                <span>
                  {formatDistanceToNow(
                    new Date(tweet.published_at || tweet.fetched_at),
                    {
                      addSuffix: true,
                      locale: zhCN,
                    }
                  )}
                </span>
              )}
            </div>
            <div className="flex items-center gap-1">
              {onBookmark && (
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8"
                  onClick={() => onBookmark(tweet.id)}
                >
                  <Bookmark
                    className={`h-4 w-4 ${
                      tweet.is_bookmarked ? "fill-current text-sky-500" : ""
                    }`}
                  />
                </Button>
              )}
              <Button variant="ghost" size="icon" className="h-8 w-8" asChild>
                <a
                  href={tweet.url}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <ExternalLink className="h-4 w-4" />
                </a>
              </Button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// X Logo SVG component
function XIcon({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="currentColor"
      className={className}
    >
      <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
    </svg>
  );
}

export default XTweetCard;
