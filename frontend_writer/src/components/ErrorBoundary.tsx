"use client";

/**
 * Error Boundary Component
 *
 * Catches React component errors and reports them to the backend
 * Provides a fallback UI when errors occur
 */

import React, { Component, ErrorInfo, ReactNode } from "react";
import { getLogger, handleGlobalError } from "@/lib/logger";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    // Update state so the next render will show the fallback UI
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Store error info in state
    this.setState({
      errorInfo,
    });

    // Log the error using our logger
    const logger = getLogger();
    logger.error(error.message, error, {
      componentStack: errorInfo.componentStack,
      boundary: "ErrorBoundary",
    });

    // Call custom error handler if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  render() {
    if (this.state.hasError) {
      // If a custom fallback is provided, use it
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default fallback UI
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
          <div className="max-w-md w-full mx-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
              <div className="flex items-center justify-center w-12 h-12 mx-auto mb-4 rounded-full bg-red-100 dark:bg-red-900/30">
                <svg
                  className="w-6 h-6 text-red-600 dark:text-red-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                  />
                </svg>
              </div>

              <h2 className="text-xl font-semibold text-center text-gray-900 dark:text-white mb-2">
                出错了
              </h2>

              <p className="text-gray-600 dark:text-gray-400 text-center mb-4">
                应用程序遇到了一个错误。请刷新页面重试。
              </p>

              {process.env.NODE_ENV === "development" && this.state.error && (
                <div className="mb-4 p-3 bg-gray-100 dark:bg-gray-700 rounded-lg">
                  <p className="text-sm font-mono text-red-600 dark:text-red-400 break-all">
                    {this.state.error.toString()}
                  </p>
                </div>
              )}

              <div className="flex gap-3">
                <button
                  onClick={() => window.location.reload()}
                  className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                >
                  刷新页面
                </button>
                <button
                  onClick={() => {
                    this.setState({ hasError: false, error: null, errorInfo: null });
                  }}
                  className="flex-1 px-4 py-2 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-lg transition-colors"
                >
                  重试
                </button>
              </div>

              {this.state.errorInfo?.componentStack && process.env.NODE_ENV === "development" && (
                <details className="mt-4">
                  <summary className="text-sm text-gray-500 dark:text-gray-400 cursor-pointer">
                    查看错误堆栈
                  </summary>
                  <pre className="mt-2 p-3 bg-gray-100 dark:bg-gray-700 rounded-lg text-xs font-mono overflow-auto max-h-48 text-gray-600 dark:text-gray-300">
                    {this.state.errorInfo.componentStack}
                  </pre>
                </details>
              )}
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

// ============================================================
// Hook for manual error handling
// ============================================================

export function useErrorHandler() {
  const [error, setError] = React.useState<Error | null>(null);

  const handleError = React.useCallback((err: Error | string) => {
    const error = err instanceof Error ? err : new Error(err);
    setError(error);

    const logger = getLogger();
    logger.error(error.message, error);
  }, []);

  const clearError = React.useCallback(() => {
    setError(null);
  }, []);

  return { error, handleError, clearError };
}

// ============================================================
// Global Error Handler for non-React errors
// ============================================================

export function setupGlobalErrorHandlers() {
  if (typeof window === "undefined") return;

  // Handle unhandled promise rejections
  window.addEventListener("unhandledrejection", (event) => {
    event.preventDefault();

    const logger = getLogger();
    logger.error("Unhandled Promise Rejection", event.reason, {
      type: "unhandledrejection",
    });
  });

  // Handle uncaught errors
  window.addEventListener("error", (event) => {
    const logger = getLogger();
    logger.error("Uncaught Error", event.error, {
      type: "uncaughterror",
      filename: event.filename,
      lineno: event.lineno,
      colno: event.colno,
    });
  });

  // Handle console errors (for errors logged via console.error)
  const originalError = console.error;
  console.error = (...args: unknown[]) => {
    // Check if it's actually an error
    const [firstArg] = args;
    if (firstArg instanceof Error || (typeof firstArg === "string" && firstArg.includes("Error"))) {
      const logger = getLogger();
      logger.error(
        typeof firstArg === "string" ? firstArg : firstArg.message,
        firstArg instanceof Error ? firstArg : new Error(String(firstArg))
      );
    }

    // Call original console.error
    originalError.apply(console, args);
  };
}
