import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // 性能优化配置
  reactStrictMode: true,
  
  // Docker 生产环境独立输出
  output: "standalone",
  
  // 图片优化
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "**",
      },
      {
        protocol: "http",
        hostname: "**",
      },
    ],
    formats: ["image/avif", "image/webp"],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  },
  
  // 实验性功能
  experimental: {
    // 优化包导入
    optimizePackageImports: ["lucide-react", "@radix-ui/react-icons"],
  },
  
  // Turbopack 配置 (Next.js 16+)
  turbopack: {
    resolveAlias: {
      // 别名配置
    },
  },
  
  // 编译器优化
  compiler: {
    // 移除 console.log (生产环境)
    removeConsole: process.env.NODE_ENV === "production",
  },
  
  // Headers 配置
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          {
            key: "X-DNS-Prefetch-Control",
            value: "on",
          },
          {
            key: "X-Content-Type-Options",
            value: "nosniff",
          },
          {
            key: "Referrer-Policy",
            value: "origin-when-cross-origin",
          },
        ],
      },
      {
        source: "/api/:path*",
        headers: [
          {
            key: "Cache-Control",
            value: "no-store, max-age=0",
          },
        ],
      },
      {
        source: "/(.*)\\.(ico|svg|png|jpg|jpeg|gif|webp|avif|woff|woff2|ttf|eot)",
        headers: [
          {
            key: "Cache-Control",
            value: "public, max-age=31536000, immutable",
          },
        ],
      },
    ];
  },
  
  // 重定向配置
  async redirects() {
    return [
      // 旧路径重定向到新路径
      {
        source: "/home",
        destination: "/",
        permanent: true,
      },
      {
        source: "/trends",
        destination: "/trending",
        permanent: true,
      },
    ];
  },
};

export default nextConfig;
