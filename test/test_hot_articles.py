"""
热点资讯页面测试脚本
验证信源资讯显示和筛选功能
"""
from playwright.sync_api import sync_playwright
import sys


def test_hot_articles_page():
    """测试热点资讯页面"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        print("=" * 60)
        print("开始测试热点资讯页面")
        print("=" * 60)

        try:
            # 1. 访问首页
            print("\n[步骤1] 访问热点资讯页面...")
            page.goto('http://localhost:3000', timeout=60000)

            # 等待页面基本加载
            page.wait_for_selector('h1', timeout=30000)
            print("✓ 页面已加载")

            # 截图保存
            page.screenshot(path='test_output/homepage_initial.png', full_page=True)
            print("已保存初始页面截图: test_output/homepage_initial.png")

            # 2. 检查页面标题
            print("\n[步骤2] 检查页面标题...")
            title = page.locator('h1').first
            title_text = title.inner_text()
            print(f"页面标题: {title_text}")
            if "热点资讯" in title_text:
                print("✓ 页面标题正确")
            else:
                print(f"⚠ 标题异常: {title_text}")

            # 3. 检查统计卡片
            print("\n[步骤3] 检查统计卡片...")
            stats_text = page.locator('body').inner_text()
            if "今日新增" in stats_text:
                print("✓ 找到统计卡片")
            elif "暂无资讯" in stats_text:
                print("⚠ 当前无数据，显示'暂无资讯'")
            else:
                print("⚠ 未找到统计卡片或数据为空")

            # 4. 检查筛选控件
            print("\n[步骤4] 检查筛选控件...")
            filter_text = stats_text
            if "今日" in filter_text or "本周" in filter_text or "本月" in filter_text:
                print("✓ 找到时间范围筛选")
            if "全部信源" in filter_text:
                print("✓ 找到全部信源筛选")
            if "RSS" in filter_text:
                print("✓ 找到 RSS 信源")
            if "Twitter" in filter_text or "X / Twitter" in filter_text:
                print("✓ 找到 Twitter 信源")
            if "GitHub" in filter_text:
                print("✓ 找到 GitHub 信源")
            if "Nitter" in filter_text:
                print("✓ 找到 Nitter 信源")

            # 5. 检查搜索框
            print("\n[步骤5] 检查搜索框...")
            search_input = page.locator('input[type="text"], input[placeholder]').all()
            print(f"✓ 找到 {len(search_input)} 个输入框")

            # 6. 截图最终状态
            page.screenshot(path='test_output/homepage_final.png', full_page=True)
            print("\n已保存最终页面截图: test_output/homepage_final.png")

            # 7. 测试 API 调用
            print("\n[步骤6] 测试后端 API...")

            # 测试文章列表 API
            try:
                api_response = page.request.get(
                    "http://localhost:8000/api/articles?time_range=today&page=1&page_size=5",
                    timeout=10000
                )
                print(f"  /api/articles 响应状态: {api_response.status}")
                if api_response.ok:
                    data = api_response.json()
                    print(f"  返回文章总数: {data.get('total', 0)}")
                    print(f"  当前页文章数: {len(data.get('items', []))}")
                    if data.get('items'):
                        print("  前3篇文章:")
                        for i, item in enumerate(data['items'][:3]):
                            print(f"    {i+1}. [{item.get('source_type', 'unknown').upper()}] {item.get('title', '')[:50]}")
            except Exception as e:
                print(f"  ⚠ API 请求失败: {e}")

            # 测试统计 API
            try:
                stats_response = page.request.get(
                    "http://localhost:8000/api/articles/stats",
                    timeout=10000
                )
                print(f"  /api/articles/stats 响应状态: {stats_response.status}")
                if stats_response.ok:
                    stats = stats_response.json()
                    print(f"  今日新增: {stats.get('today_count', 0)}")
                    print(f"  本周新增: {stats.get('week_count', 0)}")
                    print(f"  本月新增: {stats.get('month_count', 0)}")
            except Exception as e:
                print(f"  ⚠ 统计 API 请求失败: {e}")

            # 测试 GitHub Trending API
            try:
                trending_response = page.request.get(
                    "http://localhost:8000/api/github/trending?limit=3",
                    timeout=10000
                )
                print(f"  /api/github/trending 响应状态: {trending_response.status}")
                if trending_response.ok:
                    trending_data = trending_response.json()
                    repos = trending_data.get('repos', [])
                    print(f"  GitHub Trending 数量: {len(repos)}")
                    if repos:
                        print("  前3个 Trending 项目:")
                        for i, repo in enumerate(repos[:3]):
                            print(f"    {i+1}. {repo.get('owner')}/{repo.get('repo')}")
            except Exception as e:
                print(f"  ⚠ GitHub Trending API 请求失败: {e}")

            # 8. 检查页面元素
            print("\n[步骤7] 检查页面元素...")
            body_text = page.locator('body').inner_text()

            # 检查不同信源的文章
            source_counts = {
                'RSS': body_text.count('RSS') + body_text.count('rss'),
                'Twitter': body_text.count('TWITTER') + body_text.count('twitter'),
                'GitHub': body_text.count('GITHUB') + body_text.count('github'),
                'Nitter': body_text.count('NETTER') + body_text.count('nitter'),
            }
            print("  页面中各信源出现次数:")
            for source, count in source_counts.items():
                if count > 0:
                    print(f"    {source}: {count}")

            # 检查 GitHub Trending
            if "GitHub Trending" in body_text or "TRENDING" in body_text:
                print("  ✓ 页面包含 GitHub Trending 区域")
            else:
                print("  ⚠ 页面不包含 GitHub Trending 区域")

        except Exception as e:
            print(f"\n⚠ 测试过程中出现错误: {e}")
            page.screenshot(path='test_output/error_state.png', full_page=True)
            print("已保存错误状态截图: test_output/error_state.png")

        print("\n" + "=" * 60)
        print("测试完成!")
        print("=" * 60)

        browser.close()


if __name__ == "__main__":
    test_hot_articles_page()
