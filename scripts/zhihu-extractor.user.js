// ==UserScript==
// @name         知乎问题提取器
// @namespace    http://tampermonkey.net/
// @version      1.2
// @description  提取知乎邀请回答页面的问题数据，发送到后端 API
// @author       AI News
// @match        https://www.zhihu.com/*
// @icon         https://www.zhihu.com/favicon.ico
// @grant        unsafeWindow
// @grant        GM_xmlhttpRequest
// @grant        window.onurlchange
// @connect      localhost
// @connect      127.0.0.1
// @run-at       document-idle
// @license      MIT
// ==/UserScript==

(function () {
    "use strict";

    // ============================================================
    // 知乎问题提取器 - 调试版本
    // 所有执行步骤都会输出到 Console
    // ============================================================

    console.log("🚀 [知乎提取器] 脚本开始加载...");

    // 配置：后端 API 地址（本地开发用）
    const API_BASE =
        typeof unsafeWindow !== "undefined" && unsafeWindow.__API_BASE__
            ? unsafeWindow.__API_BASE__
            : "http://localhost:8001/api/news/zhihu";

    console.log(`📡 [知乎提取器] API 地址: ${API_BASE}`);

    // ============================================================
    // 前置条件检查
    // ============================================================
    function checkPrerequisites() {
        console.log("🔍 [知乎提取器] 开始检查前置条件...");

        const checks = {
            "Tampermonkey 环境": typeof GM_xmlhttpRequest !== "undefined",
            "unsafeWindow 可用": typeof unsafeWindow !== "undefined",
            "window.onurlchange 可用": typeof window.onurlchange !== "undefined",
            "页面文档就绪": document.readyState !== "loading",
        };

        console.table(checks);
        console.log("✅ [知乎提取器] 前置条件检查完成");

        return Object.values(checks).every(v => v);
    }

    // ============================================================
    // URL 路径解析
    // ============================================================
    function getCurrentLabel() {
        const path = window.location.pathname;
        console.log(`📍 [知乎提取器] 当前路径: ${path}`);

        let label;
        if (path.includes("/invited")) {
            label = "surging";
            console.log("📋 [知乎提取器] 识别为: 飙升问题 (surging)");
        } else if (path.includes("/new")) {
            label = "new";
            console.log("📋 [知乎提取器] 识别为: 新问题 (new)");
        } else {
            label = "recommend";
            console.log("📋 [知乎提取器] 识别为: 推荐问题 (recommend)");
        }

        return label;
    }

    // ============================================================
    // 检查当前 URL 是否是创作者问题页面
    // ============================================================
    function isCreatorQuestionPage() {
        const path = window.location.pathname;
        console.log(`🔎 [知乎提取器] 检查页面类型: ${path}`);

        const patterns = [
            "/creator/featured-question",
            "/creator/invited",
            "/creator/question"
        ];

        const isMatch = patterns.some(p => path.includes(p));
        console.log(`${isMatch ? "✅" : "❌"} [知乎提取器] 是否为创作者问题页面: ${isMatch}`);

        return isMatch;
    }

    // ============================================================
    // 提取问题数据
    // ============================================================
    function extractQuestions() {
        console.log("=" .repeat(50));
        console.log("📥 [知乎提取器] 开始提取问题数据...");
        console.log("=" .repeat(50));

        const questions = [];
        const label = getCurrentLabel();
        console.log(`🏷️  [知乎提取器] 当前标签: ${label}`);

        // 新版知乎使用动态类名，需要用属性选择器
        // 1. 找到问题列表容器
        console.log("🔍 [知乎提取器] 查找问题列表容器...");

        // 尝试多种方式找到问题列表
        let questionList = document.querySelector('[role="list"]');
        if (!questionList) {
            questionList = document.querySelector(".css-0, [class*='list']");
        }

        if (!questionList) {
            console.error("❌ [知乎提取器] 未找到问题列表容器");
            showToast("未找到问题列表，请确认是否在正确的页面", "error");
            return [];
        }

        console.log(`✅ [知乎提取器] 找到问题列表容器`);

        // 2. 在列表中查找所有问题链接
        // 知乎的问题链接格式: <a href="/question/数字/...">
        const questionLinks = questionList.querySelectorAll('a[href*="/question/"]');

        console.log(`📊 [知乎提取器] 在列表中找到 ${questionLinks.length} 个问题链接`);

        if (questionLinks.length === 0) {
            // 备选：从整个页面查找
            console.log("⚠️ [知乎提取器] 列表中未找到，尝试从整个页面查找...");
            const allQuestionLinks = document.querySelectorAll('a[href*="/question/"]');
            console.log(`   整个页面找到 ${allQuestionLinks.length} 个问题链接`);

            if (allQuestionLinks.length > 0) {
                questionLinks.length = 0;
                // 只保留看起来是问题标题的链接（通常在特定容器内）
                allQuestionLinks.forEach(link => {
                    const href = link.href;
                    // 跳过用户主页、话题等链接
                    if (!href.includes('/people/') && !href.includes('/topic/') && !href.includes('/column/')) {
                        // 检查这个链接是否在问题列表附近
                        let parent = link.closest('[role="listitem"], li, article, .Card, .item');
                        if (parent && parent.textContent.length > 20) {
                            questionLinks.push(link);
                        }
                    }
                });
                console.log(`📊 [知乎提取器] 过滤后保留 ${questionLinks.length} 个问题链接`);
            }
        }

        // 3. 去重并提取问题数据
        const seenUrls = new Set();

        questionLinks.forEach((link, index) => {
            const href = link.href;

            // 跳过已处理的问题
            if (seenUrls.has(href)) return;
            seenUrls.add(href);

            // 获取问题标题
            const title = link.textContent.trim();

            // 跳过无效标题
            if (!title || title.length < 5) {
                console.log(`⏭️ [知乎提取器] 跳过无效标题: "${title}"`);
                return;
            }

            // 提取问题 ID
            const urlMatch = href.match(/\/question\/(\d+)/);
            const zhihu_id = urlMatch ? urlMatch[1] : '';

            if (!zhihu_id) {
                console.log(`⏭️ [知乎提取器] 跳过无法提取 ID 的链接: ${href}`);
                return;
            }

            // 获取父级容器（问题卡片）
            const card = link.closest('[role="listitem"], li, div[class*="item"], div[class*="card"]') || link.parentElement;

            // 提取统计数据
            let answer_count = 0;
            let follower_count = 0;
            let inviter = '';
            let invite_time = '';

            // 方式1: 从父容器中查找
            if (card) {
                const text = card.textContent || '';

                // 匹配 "138 回答 · 335 关注" 格式
                const statsMatch = text.match(/(\d+)\s*回答.*?(\d+)\s*关注/);
                if (statsMatch) {
                    answer_count = parseInt(statsMatch[1], 10);
                    follower_count = parseInt(statsMatch[2], 10);
                } else {
                    // 方式2: 单独匹配
                    const answerMatch = text.match(/(\d+)\s*回答/);
                    const followerMatch = text.match(/(\d+)\s*关注/);
                    if (answerMatch) answer_count = parseInt(answerMatch[1], 10);
                    if (followerMatch) follower_count = parseInt(followerMatch[1], 10);
                }

                // 提取邀请者
                const inviterEls = card.querySelectorAll('[class*="nr5ql7"], [class*="author"], strong, b');
                inviterEls.forEach(el => {
                    const elText = el.textContent.trim();
                    // 邀请者通常是短名字，且不是数字
                    if (elText.length > 1 && elText.length < 20 && !/^\d+$/.test(elText)) {
                        if (!elText.includes('回答') && !elText.includes('关注') && !elText.includes('浏览')) {
                            inviter = elText;
                        }
                    }
                });

                // 提取邀请时间
                const timeMatch = text.match(/(\d+\s*(?:分钟|小时|天)前)/);
                if (timeMatch) {
                    invite_time = timeMatch[1];
                }
            }

            // 构建问题数据
            const question = {
                zhihu_id,
                title,
                answer_count,
                follower_count,
                url: href,
                label,
                inviter: inviter || '',
                invite_time: invite_time || '',
                content_hash: generateHash(`${zhihu_id}:${title}`),
                raw_metadata: {
                    extracted_at: new Date().toISOString(),
                },
            };

            questions.push(question);
            console.log(`✅ [知乎提取器] #${questions.length}: ${title.substring(0, 40)}... (${answer_count}回答/${follower_count}关注)`);
        });

        console.log(`\n📦 [知乎提取器] 提取完成，共 ${questions.length} 条数据`);
        return questions;
    }

    // 解析带 K/M 后缀的数字
    function parseNumber(text) {
        text = text.trim().toUpperCase();
        let num = parseFloat(text);
        if (isNaN(num)) return 0;
        if (text.includes("K")) num *= 1000;
        else if (text.includes("万")) num *= 10000;
        return Math.round(num);
    }

    // 生成 SHA256 哈希
    function generateHash(content) {
        let hash = 0;
        for (let i = 0; i < content.length; i++) {
            const char = content.charCodeAt(i);
            hash = (hash << 5) - hash + char;
            hash = hash & hash;
        }
        return Math.abs(hash).toString(16);
    }

    // 发送数据到后端
    function sendToBackend(questions) {
        console.log("=" .repeat(50));
        console.log("📤 [知乎提取器] 开始发送数据到后端...");
        console.log("=" .repeat(50));

        if (questions.length === 0) {
            console.warn("⚠️ [知乎提取器] 没有可发送的问题数据");
            showToast("没有找到可提取的问题", "warning");
            return;
        }

        console.log(`📦 [知乎提取器] 待发送数据:`);
        console.log(`   - 问题数量: ${questions.length}`);
        console.log(`   - API 地址: ${API_BASE}/questions`);
        console.log(`   - 数据预览:`);
        questions.forEach((q, i) => {
            console.log(`     ${i + 1}. [${q.zhihu_id}] ${q.title.substring(0, 40)}...`);
        });

        const payload = JSON.stringify({ questions });
        console.log(`📝 [知乎提取器] 请求载荷大小: ${new Blob([payload]).size} 字节`);

        showToast(`正在提取 ${questions.length} 条问题...`, "info");

        // 使用 GM_xmlhttpRequest 以支持跨域
        console.log("⏳ [知乎提取器] 发送请求中...");
        GM_xmlhttpRequest({
            method: "POST",
            url: `${API_BASE}/questions`,
            headers: {
                "Content-Type": "application/json",
            },
            data: payload,
            onload: function (response) {
                console.log("📬 [知乎提取器] 收到响应:");
                console.log(`   - 状态码: ${response.status}`);
                console.log(`   - 响应内容: ${response.responseText.substring(0, 200)}...`);

                if (response.status >= 200 && response.status < 300) {
                    try {
                        const result = JSON.parse(response.responseText);
                        console.log("✅ [知乎提取器] 请求成功!");
                        console.log(`   - 创建: ${result.created} 条`);
                        console.log(`   - 更新: ${result.updated} 条`);
                        showToast(
                            `成功！已保存 ${result.created} 条，新增 ${result.updated} 条更新`,
                            "success"
                        );
                    } catch (e) {
                        console.error("❌ [知乎提取器] 解析响应失败:", e);
                        showToast("提取成功，但解析响应失败", "success");
                    }
                } else {
                    console.error(`❌ [知乎提取器] 请求失败: ${response.status}`);
                    showToast(`提取失败: ${response.status}`, "error");
                    console.error("[知乎提取器] API 错误:", response);
                }
            },
            onerror: function (error) {
                console.error("❌ [知乎提取器] 网络请求失败:");
                console.error(error);
                showToast(`网络错误: ${error}`, "error");
                console.error("[知乎提取器] 网络错误:", error);
            },
        });
    }

    // 显示提示消息
    function showToast(message, type = "info") {
        // 移除已有 toast
        const existing = document.getElementById("zhihu-extractor-toast");
        if (existing) existing.remove();

        const toast = document.createElement("div");
        toast.id = "zhihu-extractor-toast";
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 8px;
            font-size: 14px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            z-index: 999999;
            max-width: 320px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            animation: slideIn 0.3s ease;
        `;

        const colors = {
            success: "#10b981",
            error: "#ef4444",
            warning: "#f59e0b",
            info: "#3b82f6",
        };

        toast.style.backgroundColor = colors[type] || colors.info;
        toast.style.color = "#fff";
        toast.textContent = message;

        // 添加动画样式
        const style = document.createElement("style");
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOut {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
        `;
        if (!document.querySelector("#zhihu-extractor-style")) {
            style.id = "zhihu-extractor-style";
            document.head.appendChild(style);
        }

        document.body.appendChild(toast);

        // 3秒后自动消失
        setTimeout(() => {
            toast.style.animation = "slideOut 0.3s ease";
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    // 创建提取按钮
    function createExtractButton() {
        console.log("🎨 [知乎提取器] 开始创建提取按钮...");

        // 避免重复创建
        const existingBtn = document.getElementById("zhihu-extractor-btn");
        if (existingBtn) {
            console.log("⚠️ [知乎提取器] 按钮已存在，跳过创建");
            return;
        }

        console.log("✅ [知乎提取器] 开始创建按钮元素...");

        const button = document.createElement("button");
        button.id = "zhihu-extractor-btn";
        button.textContent = "提取问题";
        console.log("   - 创建按钮元素成功");

        button.style.cssText = `
            position: fixed;
            bottom: 24px;
            right: 24px;
            padding: 12px 24px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #fff;
            border: none;
            border-radius: 24px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            z-index: 999998;
            box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4);
            transition: transform 0.2s, box-shadow 0.2s;
        `;
        console.log("   - 按钮样式设置成功");

        button.addEventListener("mouseenter", () => {
            button.style.transform = "translateY(-2px)";
            button.style.boxShadow = "0 6px 20px rgba(102, 126, 234, 0.5)";
        });

        button.addEventListener("mouseleave", () => {
            button.style.transform = "translateY(0)";
            button.style.boxShadow = "0 4px 16px rgba(102, 126, 234, 0.4)";
        });

        const clickHandler = () => {
            console.log("🖱️ [知乎提取器] 用户点击了提取按钮!");
            const questions = extractQuestions();
            sendToBackend(questions);
        };
        button.addEventListener("click", clickHandler);
        console.log("   - 点击事件绑定成功");

        document.body.appendChild(button);
        console.log("✅ [知乎提取器] 按钮已添加到页面");

        // 验证按钮是否真的添加成功了
        const verifyBtn = document.getElementById("zhihu-extractor-btn");
        if (verifyBtn) {
            console.log("✅ [知乎提取器] 按钮验证成功，位于页面底部右侧");
        } else {
            console.error("❌ [知乎提取器] 按钮添加失败!");
        }
    }

    // 根据 URL 条件决定是否创建按钮
    function tryCreateButton() {
        console.log("🔔 [知乎提取器] 调用 tryCreateButton...");
        console.log(`   当前 URL: ${window.location.href}`);

        const isMatch = isCreatorQuestionPage();

        if (isMatch) {
            console.log("✅ [知乎提取器] 页面匹配条件，创建按钮");
            createExtractButton();
        } else {
            console.log(`⏭️ [知乎提取器] 页面不匹配，不创建按钮`);
            console.log(`   💡 如果你想在这个页面使用，请访问:`);
            console.log(`      - /creator/featured-question (推荐问题)`);
            console.log(`      - /creator/invited (邀请问题)`);
            console.log(`      - /creator/question (问题广场)`);
        }
    }

    // 初始化
    function init() {
        console.log("=" .repeat(50));
        console.log("🚀 [知乎提取器] 开始初始化...");
        console.log("=" .repeat(50));

        // 1. 检查前置条件
        const prereqOk = checkPrerequisites();
        console.log(`🔧 [知乎提取器] 前置条件检查: ${prereqOk ? "✅ 通过" : "⚠️ 部分失败"}`);

        // 2. 检查页面状态
        console.log(`📄 [知乎提取器] 页面状态: ${document.readyState}`);

        // 3. 等待页面加载
        if (document.readyState === "loading") {
            console.log("⏳ [知乎提取器] 等待 DOM 加载完成...");
            document.addEventListener("DOMContentLoaded", () => {
                console.log("✅ [知乎提取器] DOM 加载完成");
                setTimeout(tryCreateButton, 1000);
            });
        } else {
            console.log("✅ [知乎提取器] DOM 已就绪");
            setTimeout(tryCreateButton, 1000);
        }

        // 4. 监听 SPA URL 变化 - 使用多种方式确保兼容性
        console.log("🔗 [知乎提取器] 设置 URL 变化监听...");

        let lastUrl = window.location.href;

        // 方式1: Tampermonkey 内置的 onurlchange (Chrome 102+)
        if (typeof window.onurlchange !== "undefined") {
            window.addEventListener("urlchange", (info) => {
                console.log("🔄 [知乎提取器] URL 变化 (onurlchange):", info.url || window.location.href);
                handleUrlChange();
            });
            console.log("✅ [知乎提取器] onurlchange 监听已设置");
        }

        // 方式2: 拦截 history.pushState 和 history.replaceState
        const originalPushState = history.pushState;
        const originalReplaceState = history.replaceState;

        history.pushState = function(...args) {
            originalPushState.apply(this, args);
            console.log("🔄 [知乎提取器] history.pushState 检测到 URL 变化");
            handleUrlChange();
        };

        history.replaceState = function(...args) {
            originalReplaceState.apply(this, args);
            console.log("🔄 [知乎提取器] history.replaceState 检测到 URL 变化");
            handleUrlChange();
        };

        window.addEventListener("popstate", () => {
            console.log("🔄 [知乎提取器] popstate 事件检测到 URL 变化");
            handleUrlChange();
        });

        console.log("✅ [知乎提取器] history API 拦截已设置");

        // 方式3: 备用轮询机制 (每2秒检查一次 URL)
        let pollCount = 0;
        const pollInterval = setInterval(() => {
            const currentUrl = window.location.href;
            if (currentUrl !== lastUrl) {
                console.log(`🔄 [知乎提取器] 轮询检测到 URL 变化 (检查了 ${pollCount} 次)`);
                lastUrl = currentUrl;
                handleUrlChange();
            }
            pollCount++;
        }, 2000);

        // URL 变化处理函数
        function handleUrlChange() {
            const currentUrl = window.location.href;
            if (currentUrl === lastUrl) return;
            lastUrl = currentUrl;

            console.log("=" .repeat(50));
            console.log(`🔄 [知乎提取器] 处理 URL 变化!`);
            console.log(`   新 URL: ${currentUrl}`);
            console.log("=" .repeat(50));

            // 移除旧按钮
            const oldBtn = document.getElementById("zhihu-extractor-btn");
            if (oldBtn) {
                console.log("🗑️ [知乎提取器] 移除旧按钮");
                oldBtn.remove();
            }

            // 重新尝试创建
            setTimeout(tryCreateButton, 1500);
        }

        console.log("✅ [知乎提取器] URL 变化监听全部设置完成");
        console.log(`💡 提示: 在开发者工具 Console 中查看详细日志`);
    }

    init();
})();
