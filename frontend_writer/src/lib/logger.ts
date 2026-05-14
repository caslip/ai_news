/**
 * Frontend Logger
 *
 * Provides structured logging for the frontend application with:
 * - Error tracking and reporting
 * - User behavior analytics
 * - Performance monitoring
 * - Integration with backend audit system
 */

// ============================================================
// UUID Generator (simple implementation)
// ============================================================

function generateUUID(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

// ============================================================
// Types
// ============================================================

export type LogLevel = "debug" | "info" | "warn" | "error";

export type EventStatus = "success" | "failed" | "denied";

export interface FrontendEvent {
  event_id: string;
  timestamp: string;
  user_id?: string;
  username?: string;
  session_id: string;
  user_agent: string;
  ip?: string;
  action: string;
  resource_type?: string;
  resource_id?: string;
  before?: unknown;
  after?: unknown;
  status: EventStatus;
  error_code?: string;
  error_message?: string;
  stack_trace?: string;
  duration_ms?: number;
  service: "ai-news-frontend";
  env: string;
  trace_id?: string;
  request_id?: string;
  page_url?: string;
  page_name?: string;
}

export interface LoggerConfig {
  serviceName?: string;
  environment?: string;
  apiEndpoint?: string;
  enableConsole?: boolean;
  enableRemote?: boolean;
  minLevel?: LogLevel;
}

// ============================================================
// Session Management
// ============================================================

let sessionId: string | null = null;
let userId: string | null = null;
let username: string | null = null;
let traceId: string | null = null;

export function setSessionInfo(info: {
  sessionId?: string;
  userId?: string;
  username?: string;
}) {
  if (info.sessionId) sessionId = info.sessionId;
  if (info.userId) userId = info.userId;
  if (info.username) username = info.username;
}

export function clearSessionInfo() {
  sessionId = null;
  userId = null;
  username = null;
}

export function getSessionId(): string {
  if (!sessionId) {
    sessionId = localStorage.getItem("frontend_session_id") || generateUUID();
    localStorage.setItem("frontend_session_id", sessionId);
  }
  return sessionId;
}

// ============================================================
// Trace ID Management
// ============================================================

export function getTraceId(): string {
  if (!traceId) {
    // Check if trace_id is in localStorage from a previous page navigation
    traceId = localStorage.getItem("trace_id") || generateUUID();
    localStorage.setItem("trace_id", traceId);
  }
  return traceId;
}

export function setTraceId(newTraceId: string) {
  traceId = newTraceId;
  localStorage.setItem("trace_id", traceId);
}

// ============================================================
// Logger Class
// ============================================================

class FrontendLogger {
  private config: Required<LoggerConfig>;
  private eventQueue: FrontendEvent[] = [];
  private flushInterval: number | null = null;
  private readonly FLUSH_INTERVAL_MS = 5000;
  private readonly MAX_QUEUE_SIZE = 50;

  constructor(config: LoggerConfig = {}) {
    this.config = {
      serviceName: config.serviceName || "ai-news-frontend",
      environment: config.environment || process.env.NODE_ENV || "development",
      apiEndpoint: config.apiEndpoint || "/api/logging/client-event",
      enableConsole: config.enableConsole ?? true,
      enableRemote: config.enableRemote ?? true,
      minLevel: config.minLevel || "info",
    };

    // Start flush interval
    this.startFlushInterval();

    // Listen for page unload to flush remaining events
    if (typeof window !== "undefined") {
      window.addEventListener("beforeunload", () => this.flush());
    }
  }

  private shouldLog(level: LogLevel): boolean {
    const levels: Record<LogLevel, number> = {
      debug: 0,
      info: 1,
      warn: 2,
      error: 3,
    };
    return levels[level] >= levels[this.config.minLevel];
  }

  private formatEvent(
    action: string,
    options: Partial<FrontendEvent> = {}
  ): FrontendEvent {
    return {
      event_id: generateUUID(),
      timestamp: new Date().toISOString(),
      user_id: userId || undefined,
      username: username || undefined,
      session_id: getSessionId(),
      user_agent: typeof navigator !== "undefined" ? navigator.userAgent : "unknown",
      action,
      status: options.status || "success",
      service: this.config.serviceName as "ai-news-frontend",
      env: this.config.environment,
      trace_id: getTraceId(),
      request_id: options.request_id,
      page_url: typeof window !== "undefined" ? window.location.href : undefined,
      page_name: this.getPageName(),
      ...options,
    };
  }

  private getPageName(): string | undefined {
    if (typeof window === "undefined") return undefined;

    // Try to get from Next.js router
    const path = window.location.pathname;
    if (path.includes("/drafts")) return "drafts";
    if (path.includes("/generate")) return "generate";
    if (path.includes("/chat")) return "chat";
    if (path.includes("/login")) return "login";
    if (path.includes("/register")) return "register";

    return path;
  }

  private logToConsole(level: LogLevel, message: string, data?: unknown) {
    if (!this.config.enableConsole) return;

    const prefix = `[${level.toUpperCase()}]`;
    const logMethod = level === "error" ? console.error : level === "warn" ? console.warn : console.log;

    if (data) {
      logMethod(prefix, message, data);
    } else {
      logMethod(prefix, message);
    }
  }

  private async sendToBackend(event: FrontendEvent) {
    if (!this.config.enableRemote) return;

    try {
      const response = await fetch(this.config.apiEndpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(event),
        // Don't await - fire and forget
      });

      if (!response.ok) {
        console.warn("Failed to send log event to backend:", response.status);
      }
    } catch (error) {
      // Silently fail - don't disrupt the application
      console.debug("Failed to send log event:", error);
    }
  }

  private async sendBatch(events: FrontendEvent[]) {
    if (!this.config.enableRemote) return;

    try {
      const response = await fetch(`${this.config.apiEndpoint}/batch`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ events }),
      });

      if (!response.ok) {
        console.warn("Failed to send batch log events:", response.status);
      }
    } catch (error) {
      console.debug("Failed to send batch log events:", error);
    }
  }

  private queueEvent(event: FrontendEvent) {
    this.eventQueue.push(event);

    // Flush if queue is too large
    if (this.eventQueue.length >= this.MAX_QUEUE_SIZE) {
      this.flush();
    }
  }

  private startFlushInterval() {
    if (typeof window === "undefined") return;

    this.flushInterval = window.setInterval(() => {
      this.flush();
    }, this.FLUSH_INTERVAL_MS);
  }

  private flush() {
    if (this.eventQueue.length === 0) return;

    const eventsToSend = [...this.eventQueue];
    this.eventQueue = [];

    this.sendBatch(eventsToSend);
  }

  // ============================================================
  // Public API
  // ============================================================

  debug(message: string, data?: unknown) {
    if (!this.shouldLog("debug")) return;
    this.logToConsole("debug", message, data);
  }

  info(message: string, data?: unknown) {
    if (!this.shouldLog("info")) return;
    this.logToConsole("info", message, data);
  }

  warn(message: string, data?: unknown) {
    if (!this.shouldLog("warn")) return;
    this.logToConsole("warn", message, data);
  }

  error(message: string, error?: Error | unknown, context?: Record<string, unknown>) {
    if (!this.shouldLog("error")) return;

    const errorInfo = this.extractErrorInfo(error);

    this.logToConsole("error", message, { ...errorInfo, ...context });

    const event = this.formatEvent("client.error", {
      status: "failed",
      error_code: errorInfo.error_code,
      error_message: errorInfo.error_message,
      stack_trace: errorInfo.stack_trace,
      ...context,
    });

    this.queueEvent(event);
    this.sendToBackend(event);
  }

  private extractErrorInfo(error: Error | unknown): {
    error_code: string;
    error_message: string;
    stack_trace?: string;
  } {
    if (error instanceof Error) {
      return {
        error_code: error.name || "Error",
        error_message: error.message,
        stack_trace: error.stack,
      };
    }

    if (typeof error === "string") {
      return {
        error_code: "Error",
        error_message: error,
      };
    }

    return {
      error_code: "UnknownError",
      error_message: "An unknown error occurred",
    };
  }

  // ============================================================
  // Audit Event Logging
  // ============================================================

  /**
   * Log a user action event
   */
  logAction(
    action: string,
    options: {
      resource_type?: string;
      resource_id?: string;
      before?: unknown;
      after?: unknown;
      status?: EventStatus;
      duration_ms?: number;
      error_code?: string;
      error_message?: string;
    } = {}
  ) {
    const event = this.formatEvent(action, options);

    this.queueEvent(event);
    this.sendToBackend(event);
  }

  /**
   * Log a page view event
   */
  logPageView(page: string, referrer?: string) {
    this.logAction("page.view", {
      resource_type: "page",
      resource_id: page,
      before: referrer ? { referrer } : undefined,
    });
  }

  /**
   * Log a button click event
   */
  logClick(element: string, page?: string) {
    this.logAction("ui.click", {
      resource_type: "button",
      resource_id: element,
      page_name: page || this.getPageName(),
    });
  }

  /**
   * Log a form submission event
   */
  logFormSubmit(formId: string, status: EventStatus = "success", errorMessage?: string) {
    this.logAction("form.submit", {
      resource_type: "form",
      resource_id: formId,
      status,
      error_message: errorMessage,
    });
  }

  /**
   * Log an API request event
   */
  logApiRequest(
    endpoint: string,
    method: string,
    options: {
      status?: EventStatus;
      duration_ms?: number;
      error_code?: string;
      error_message?: string;
    } = {}
  ) {
    this.logAction(`${method.toLowerCase()}.${endpoint}`, {
      resource_type: "api",
      resource_id: endpoint,
      method,
      ...options,
    });
  }

  /**
   * Log a navigation event
   */
  logNavigation(from: string, to: string) {
    this.logAction("app.navigate", {
      resource_type: "navigation",
      before: { from },
      after: { to },
    });
  }

  /**
   * Log authentication events
   */
  logAuth(action: "login" | "logout" | "register", success: boolean, errorMessage?: string) {
    this.logAction(`auth.${action}`, {
      resource_type: "auth",
      status: success ? "success" : "failed",
      error_message: errorMessage,
    });
  }

  /**
   * Log content generation events
   */
  logContentGeneration(
    action: "start" | "complete" | "fail",
    draftId?: string,
    options: {
      duration_ms?: number;
      error_message?: string;
      word_count?: number;
    } = {}
  ) {
    this.logAction(`content.${action}`, {
      resource_type: "draft",
      resource_id: draftId,
      after: options.word_count ? { word_count: options.word_count } : undefined,
      duration_ms: options.duration_ms,
      error_message: options.error_message,
      status: action === "fail" ? "failed" : "success",
    });
  }

  // ============================================================
  // Lifecycle
  // ============================================================

  /**
   * Clean up resources
   */
  destroy() {
    if (this.flushInterval) {
      clearInterval(this.flushInterval);
      this.flushInterval = null;
    }
    this.flush();
  }
}

// ============================================================
// Singleton Instance
// ============================================================

let loggerInstance: FrontendLogger | null = null;

export function getLogger(config?: LoggerConfig): FrontendLogger {
  if (!loggerInstance) {
    loggerInstance = new FrontendLogger(config);
  }
  return loggerInstance;
}

// Default export for convenience
export default getLogger;

// ============================================================
// React Hook for Error Boundary Integration
// ============================================================

let errorHandler: ((error: Error, errorInfo: React.ErrorInfo) => void) | null = null;

export function setGlobalErrorHandler(
  handler: (error: Error, errorInfo: React.ErrorInfo) => void
) {
  errorHandler = handler;
}

export function handleGlobalError(error: Error, errorInfo?: React.ErrorInfo) {
  const logger = getLogger();
  logger.error(error.message, error, {
    componentStack: errorInfo?.componentStack,
  });

  if (errorHandler && errorInfo) {
    errorHandler(error, errorInfo);
  }
}
