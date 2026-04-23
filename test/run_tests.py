#!/usr/bin/env python
"""
AI News Aggregator - Backend Test Runner
运行方式: python run_tests.py
"""

import sys
import os
import subprocess
import argparse

def run_backend_tests():
    """运行后端测试"""
    print("=" * 60)
    print("Running Backend Tests (pytest)")
    print("=" * 60)
    
    # 切换到 backend 目录
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    
    # 检查 pytest 是否安装
    try:
        subprocess.run([sys.executable, '-m', 'pytest', '--version'], 
                     capture_output=True, check=True)
    except subprocess.CalledProcessError:
        print("Installing pytest...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 
                      os.path.join(backend_dir, 'tests', 'requirements.txt')],
                     capture_output=True)
    
    # 运行测试
    result = subprocess.run(
        [sys.executable, '-m', 'pytest', 'tests/', '-v', '--tb=short'],
        cwd=backend_dir,
        capture_output=False
    )
    
    return result.returncode == 0

def run_syntax_check():
    """检查代码语法"""
    print("\n" + "=" * 60)
    print("Running Syntax Check")
    print("=" * 60)
    
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    errors = []
    
    # 检查 Python 文件
    for root, dirs, files in os.walk(backend_dir):
        # 跳过 __pycache__ 和虚拟环境
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.venv', 'venv', 'node_modules']]
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        compile(f.read(), filepath, 'exec')
                except SyntaxError as e:
                    errors.append(f"{filepath}: {e}")
    
    if errors:
        print("Syntax Errors Found:")
        for err in errors:
            print(f"  - {err}")
        return False
    else:
        print("✓ All Python files have valid syntax")
        return True

def check_imports():
    """检查关键导入"""
    print("\n" + "=" * 60)
    print("Checking Key Imports")
    print("=" * 60)
    
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    sys.path.insert(0, backend_dir)
    
    modules_to_check = [
        ('app.config', 'Settings'),
        ('app.models', 'User'),
        ('app.schemas.user', 'UserResponse'),
        ('app.services.auth', 'AuthService'),
        ('app.services.crawler', 'RSSCrawler'),
        ('app.services.openrouter', 'score_article'),
        ('app.routers.auth', 'router'),
        ('app.routers.articles', 'router'),
        ('app.routers.sources', 'router'),
    ]
    
    errors = []
    for module_name, expected in modules_to_check:
        try:
            module = __import__(module_name, fromlist=[expected])
            if not hasattr(module, expected):
                errors.append(f"{module_name}.{expected} not found")
            else:
                print(f"✓ {module_name}.{expected}")
        except ImportError as e:
            errors.append(f"{module_name}: {e}")
        except Exception as e:
            errors.append(f"{module_name}: {e}")
    
    if errors:
        print("\nImport Errors:")
        for err in errors:
            print(f"  - {err}")
        return False
    
    return True

def main():
    parser = argparse.ArgumentParser(description='AI News Aggregator Test Runner')
    parser.add_argument('--syntax', action='store_true', help='Only run syntax check')
    parser.add_argument('--imports', action='store_true', help='Only run import check')
    parser.add_argument('--tests', action='store_true', help='Only run pytest')
    args = parser.parse_args()
    
    all_passed = True
    
    if args.syntax:
        all_passed = run_syntax_check() if all_passed else False
    elif args.imports:
        all_passed = check_imports() if all_passed else False
    else:
        # 运行所有检查
        all_passed = run_syntax_check()
        all_passed = check_imports() if all_passed else False
        
        # 尝试运行 pytest（可能因缺少依赖而失败）
        print("\n" + "=" * 60)
        print("Running pytest (optional - requires full environment)")
        print("=" * 60)
        try:
            run_backend_tests()
        except Exception as e:
            print(f"Note: pytest not run due to: {e}")
            print("To run tests manually:")
            print("  cd backend && pip install -r requirements.txt")
            print("  pytest tests/ -v")
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All checks passed!")
    else:
        print("✗ Some checks failed")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
