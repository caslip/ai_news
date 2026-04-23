#!/usr/bin/env python
"""
AI News Aggregator - Code Quality Check
检查代码质量、规范和潜在问题
"""

import os
import re
import sys
from pathlib import Path

class CodeQualityChecker:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.issues = []
        self.warnings = []
        
    def check_all(self):
        """运行所有检查"""
        print("=" * 60)
        print("AI News Aggregator - Code Quality Check")
        print("=" * 60)
        
        print("\n[1/4] Checking Backend Code...")
        self.check_backend()
        
        print("\n[2/4] Checking Frontend Code...")
        self.check_frontend()
        
        print("\n[3/4] Checking Configuration Files...")
        self.check_config()
        
        print("\n[4/4] Checking Documentation...")
        self.check_docs()
        
        self.print_summary()
        
        return len(self.issues) == 0
    
    def check_backend(self):
        """检查后端代码"""
        backend_dir = self.project_root / "backend"
        if not backend_dir.exists():
            self.warnings.append("Backend directory not found")
            return
        
        # 检查关键文件是否存在
        required_files = [
            "app/main.py",
            "app/config.py",
            "app/database.py",
            "app/models/__init__.py",
            "app/schemas/__init__.py",
            "app/routers/__init__.py",
            "requirements.txt",
        ]
        
        for file in required_files:
            if not (backend_dir / file).exists():
                self.issues.append(f"Missing backend file: {file}")
            else:
                print(f"  ✓ {file}")
        
        # 检查模型文件
        models_dir = backend_dir / "app" / "models"
        required_models = ["user.py", "source.py", "article.py", "bookmark.py", "strategy.py"]
        for model in required_models:
            if not (models_dir / model).exists():
                self.issues.append(f"Missing model: {model}")
        
        # 检查服务文件
        services_dir = backend_dir / "app" / "services"
        required_services = ["auth.py", "crawler.py", "openrouter.py", "celery_tasks.py", "ai_tasks.py"]
        for service in required_services:
            if not (services_dir / service).exists():
                self.issues.append(f"Missing service: {service}")
    
    def check_frontend(self):
        """检查前端代码"""
        frontend_dir = self.project_root / "frontend"
        if not frontend_dir.exists():
            self.warnings.append("Frontend directory not found")
            return
        
        # 检查关键文件
        required_files = [
            "package.json",
            "src/app/layout.tsx",
            "src/app/(main)/layout.tsx",
            "src/app/(main)/page.tsx",
            "src/components/layout/Sidebar.tsx",
            "src/lib/api.ts",
            "src/stores/authStore.ts",
        ]
        
        for file in required_files:
            if not (frontend_dir / file).exists():
                self.issues.append(f"Missing frontend file: {file}")
            else:
                print(f"  ✓ {file}")
        
        # 检查页面文件
        pages = [
            "src/app/auth/login/page.tsx",
            "src/app/auth/register/page.tsx",
            "src/app/(main)/trending/page.tsx",
            "src/app/(main)/sources/page.tsx",
            "src/app/(main)/favorites/page.tsx",
            "src/app/(main)/strategies/page.tsx",
            "src/app/(main)/monitor/page.tsx",
        ]
        
        for page in pages:
            if not (frontend_dir / page).exists():
                self.warnings.append(f"Missing page: {page}")
            else:
                print(f"  ✓ {page}")
    
    def check_config(self):
        """检查配置文件"""
        required_config = [
            "docker-compose.yml",
            ".env.example",
        ]
        
        for config in required_config:
            if not (self.project_root / config).exists():
                self.issues.append(f"Missing config: {config}")
            else:
                print(f"  ✓ {config}")
    
    def check_docs(self):
        """检查文档"""
        required_docs = [
            "README.md",
            "SPEC.md",
        ]
        
        for doc in required_docs:
            if not (self.project_root / doc).exists():
                self.issues.append(f"Missing doc: {doc}")
            else:
                print(f"  ✓ {doc}")
    
    def print_summary(self):
        """打印总结"""
        print("\n" + "=" * 60)
        print("Summary")
        print("=" * 60)
        
        if self.warnings:
            print(f"\nWarnings ({len(self.warnings)}):")
            for w in self.warnings:
                print(f"  ⚠ {w}")
        
        if self.issues:
            print(f"\nIssues ({len(self.issues)}):")
            for issue in self.issues:
                print(f"  ✗ {issue}")
        else:
            print("\n✓ No critical issues found!")
        
        print(f"\nTotal: {len(self.issues)} issues, {len(self.warnings)} warnings")

def main():
    project_root = Path(__file__).parent.parent
    checker = CodeQualityChecker(project_root)
    
    success = checker.check_all()
    
    if not success:
        sys.exit(1)
    
    sys.exit(0)

if __name__ == '__main__':
    main()
